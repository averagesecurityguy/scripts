package main

import (
  "fmt"
  "io/ioutil"
  "encoding/xml"
  "os"
  "net/http"
  "strings"
  "errors"

  "github.com/abiosoft/ishell"
)

// Define bucket structure
type Bucket struct {
    Name string
    Contents []*Content
}

func (b *Bucket) String() string {
    var contents []string

    for i, _ := range b.Contents {
        contents = append(contents, b.Contents[i].String())
    }

    return strings.Join(contents, "\n")
}

// Define content structure
type Content struct {
    Key string
    LastModified string
    Size int
}

func (c *Content) String() string {
    return fmt.Sprintf("%d\t%s\t%s", c.Size, c.LastModified, c.Key)
}


// Define our methods.
func check(e error) {
    if e != nil {
        fmt.Println(e)
        os.Exit(0)
    }
}

func get(url string) ([]byte, error) {
    resp, err := http.Get(url)
    if err != nil {
        return nil, errors.New(fmt.Sprintf("Download Error: %s", err.Error()))
    }

    if resp.StatusCode != 200 {
        switch resp.StatusCode {
        case 403:
            return nil, errors.New("Permission denied.")
        case 404:
            return nil, errors.New("Not found.")
        default:
            return nil, errors.New("An unknown error occurred.")
        }
    }

    defer resp.Body.Close()
    body, err := ioutil.ReadAll(resp.Body)
    if err != nil {
        return nil, errors.New("Could not read response.")
    }

    return body, nil
}

func usage() {
    fmt.Println("Usage: s3browse bucket")
    fmt.Println("Example: s3browse bucket-name.s3.amazonaws.com")
    os.Exit(0)
}

func main() {
    if len(os.Args) != 2 {
        usage()
    }

    baseUrl := "http://" + os.Args[1]
    shell := ishell.New()
    defer shell.Close()

    shell.AddCmd(&ishell.Cmd{
        Name: "ls",
        Help: "List bucket contents",
        Func: func (c *ishell.Context) {
            data, err := get(baseUrl)
            if err != nil {
                c.Println(err.Error())
                return
            }

            var bucket Bucket

            err = xml.Unmarshal(data, &bucket)
            if err != nil {
                c.Println("Could not parse response.")
                return
            }

            c.Println(bucket.String())
        },
    })

    shell.AddCmd(&ishell.Cmd{
        Name: "cat",
        Help: "cat key_name\tDisplay key value",
        Func: func (c *ishell.Context) {
            url := baseUrl + "/" + c.Args[0]
            data, err := get(url)
            if err != nil {
                c.Println(err.Error())
                return
            }

            c.Println(string(data))
        },
    })

    shell.Printf("Browsing S3 bucket: %s\n", baseUrl)
    shell.Run()
}
