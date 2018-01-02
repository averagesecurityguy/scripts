/*
Copyright (c) 2017, AverageSecurityGuy
# All rights reserved.

Parse an Nmap XML file to get all of the SSL/TLS certificate SHA1 fingerprints
and search Censys for other servers with the same certificate.

Example usage:

$ go run certquery.go nmap_file
*/
package main

import (
	"os"
    "fmt"
    "time"
    "bytes"
    "regexp"
    "strings"
    "net/http"
    "io/ioutil"
	"encoding/json"
    "encoding/xml"
)


const uid = ""
const secret = ""


type Nmap struct {
    Version string `xml:"version,attr"`
    Args    string `xml:"args,attr"`
    Hosts   []Host `xml:"host"`
}

type Host struct {
    Addresses []Address `xml:"address"`
    Ports     []Port    `xml:"ports>port"`
}

type Address struct {
    Address     string `xml:"addr,attr"`
    AddressType string `xml:"addrtype,attr"`
}

type Port struct {
    Port     string   `xml:"portid,attr"`
    Protocol string   `xml:"protocol,attr"`
    Scripts  []Script `xml:"script"`
}

type Script struct {
    Name    string `xml:"id,attr"`
    Output  string `xml:"output,attr"`
}

type Certificate struct {
    Address string
    Port    string
    Hash    string
}

type Ip struct {
    Ip string
}

type Metadata struct {
    Pages int
}

type Response struct {
    Results  []Ip
    Metadata Metadata
}


func check(e error) {
    if e != nil {
        fmt.Printf("Error: %s\n", e.Error())
        os.Exit(0)
    }
}


func get_address(addrs []Address) string {
    address := ""

    for _, a := range addrs {
        if a.AddressType == "ipv4" {
            address = a.Address
            break
        }
    }

    return address
}


func get_sha1(scripts []Script) string {
    sha1 := ""
    re := regexp.MustCompile("SHA-1: .*")

    for _, s := range scripts {
        if s.Name == "ssl-cert" {
            sha1 = re.FindString(s.Output)
            sha1 = strings.Replace(sha1, "SHA-1:", "", -1)
            sha1 = strings.Replace(sha1, " ", "", -1)
            break
        }
    }

    return sha1
}


func load_nmap(filename string) []byte {
    f, err := os.Open(filename)
    check(err)
    defer f.Close()

    nmap_data, err := ioutil.ReadAll(f)
    check(err)

    return nmap_data
}


func get_cert_hashes(nmap_data []byte) []Certificate {
    var nmap Nmap
    err := xml.Unmarshal(nmap_data, &nmap)
    check(err)

    var certificates []Certificate

    for _, h := range nmap.Hosts {
        addr := get_address(h.Addresses)

        for _, p := range h.Ports {
            sha1 := get_sha1(p.Scripts)

            if sha1 != "" {
                var certificate Certificate
                certificate.Address = addr
                certificate.Port = p.Port
                certificate.Hash = sha1
                certificates = append(certificates, certificate)
            }
        }
    }

    return certificates
}


func lookup(query []byte) ([]string, int) {
    servers := make([]string, 0)
    pages := 0
    url := "https://censys.io/api/v1/search/ipv4"
    client := &http.Client{}

    req, err := http.NewRequest("POST", url, bytes.NewBuffer(query))
    check(err)

    req.SetBasicAuth(uid, secret)
    resp, err := client.Do(req)
	check(err)

	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	check(err)

	if resp.StatusCode == 404 {
        fmt.Println("[-] File not found.")
    } else if resp.StatusCode == 429 {
        fmt.Println("[-] Rate limit exceeded. Waiting...")
    } else if resp.StatusCode == 500 {
        fmt.Println("[-] Internal Server Error.")
    } else {
        var data Response

        err := json.Unmarshal(body, &data)
        check(err)

        pages = data.Metadata.Pages
        for _, s := range data.Results {
            servers = append(servers, s.Ip)
        }
	}
    
    time.Sleep(5500 * time.Millisecond)
    
    return servers, pages
}


func build_query(hash string, page int) []byte {
    q := fmt.Sprintf(`{"query":"%s","page":%d,"fields":["ip"],"flatten":true}`, hash, page)
    return []byte(q)
}


func get_servers(hash string) []string {
    var servers []string

    page := 1
    query := build_query(hash, page)
    res, pages := lookup(query)

    for {
        servers = append(servers, res...)

        if page == pages {
            break
        }

        page = page + 1
        res, pages = lookup(query)
    }
    
    return servers
}


func main() {
    if len(os.Args) != 2 {
        fmt.Println("Usage: go run certquery.go nmap_xml_file")
        os.Exit(0)
    }

    nmap_data := load_nmap(os.Args[1])
    certificates := get_cert_hashes(nmap_data)

    for _, cert := range certificates {
        servers := get_servers(cert.Hash)
        header := fmt.Sprintf("%s (%s)", cert.Address, cert.Port)
        fmt.Println(header)
        fmt.Println(strings.Repeat("-", len(header)))
        fmt.Printf("Certificate: %s\n", cert.Hash)
        fmt.Println("Servers:")
        fmt.Println(strings.Join(servers, "\n"))
        fmt.Println("")
    }
}
