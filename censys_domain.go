/*
Copyright (c) 2017, AverageSecurityGuy
# All rights reserved.

Find subdomains using Censys certificate information.

Usage:

$ go run censys_domain.go domain
*/
package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"sort"
	"strings"
	"time"
)

const url = "https://censys.io/api/v1/search/certificates"
const uid = ""
const secret = ""

// The Query struct is used to create a query JSON object for Censys searches.
type Query struct {
	Query   string   `json:"query"`
	Fields  []string `json:"fields"`
	Page    int      `json:"page"`
	Flatten bool     `json:"flatten"`
}

// The Result struct holds a single result from the Censys JSON response.
type Result struct {
	CommonNames []string `json:"parsed.subject.common_name"`
	DnsNames    []string `json:"parsed.extensions.subject_alt_name.dns_names"`
	Names       []string `json:"parsed.names"`
}

// The Metadata struct holds metadata information from the Censys JSON response.
type Metadata struct {
	Count int    `json:"count"`
	Query string `json:"query"`
	Time  int    `json:"backend_time"`
	Page  int    `json:"page"`
	Pages int    `json:"pages"`
}

// The Response struct holds a Censys JSON response.
type Response struct {
	Status   string   `json:"status"`
	Results  []Result `json:"results"`
	Metadata Metadata `json:"metadata"`
}

// The Research struct holds the end result of our iterative queries.
type Research struct {
	Domain   string
	Searched []string
	Search   []string
	Hosts    []string
}

var research Research

// The In function determines if a string is in a slice of strings.
func in(items []string, item string) bool {
	sort.Strings(items)
	i := sort.SearchStrings(items, item)

	if i < len(items) && items[i] == item {
		return true
	}

	return false
}

// Pop removes the first item in the slice and returns the item and the new
// slice.
func pop(items []string) ([]string, string) {
	item := items[0]
	items = items[1:]

	return items, item
}

// The request function makes a Censys request and processes the response. If
// there are no errors a response struct is returned.
func request(data *bytes.Buffer) (Response, error) {
	var response Response

	client := &http.Client{}
	req, err := http.NewRequest("POST", url, data)
	if err != nil {
		return response, err
	}

	req.SetBasicAuth(uid, secret)
	resp, err := client.Do(req)
	if err != nil {
		return response, err
	}

	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return response, err
	}

	if resp.StatusCode == 429 {
		return response, errors.New("Rate limit exceeded. Please wait and try again.")
	} else if resp.StatusCode == 500 {
		return response, errors.New("Internal Server Error.")
	} else {
		err := json.Unmarshal(body, &response)
		if err != nil {
			return response, err
		}
	}

	time.Sleep(3 * time.Second)
	return response, nil
}

// The search function queries the Censys API for subdomains related to the
// given domain.
func search(domain string) ([]Result, error) {
	fmt.Printf(".")

	var results []Result
	var query Query
	pages := 100

	query.Query = fmt.Sprintf("parsed.subject.common_name: /.*\\.%s/", domain)
	query.Fields = []string{"parsed.names", "parsed.extensions.subject_alt_name.dns_names", "parsed.subject.common_name"}
	query.Flatten = true

	for i := 1; i <= pages; i++ {
		query.Page = i

		j, err := json.Marshal(query)
		if err != nil {
			research.Search = append(research.Search, domain)
			return results, err
		}

		resp, err := request(bytes.NewBuffer(j))
		if err != nil {
			research.Search = append(research.Search, domain)
			return results, err
		}

		results = append(results, resp.Results...)
		pages = resp.Metadata.Pages
	}

	research.Searched = append(research.Searched, domain)
	return results, nil
}

// Process the results and update the subdomains map with the results.
func process(results []Result, domain string) {
	var subs []string

	for _, r := range results {
		if len(r.CommonNames) == 0 {
			continue
		}

		if strings.HasSuffix(r.CommonNames[0], domain) {
			subs = append(subs, r.CommonNames...)
			subs = append(subs, r.DnsNames...)
			subs = append(subs, r.Names...)
		}
	}

	// Add new subdomains to our Hosts and Search slices.
	for _, sub := range subs {
		if !in(research.Hosts, sub) {
			research.Hosts = append(research.Hosts, sub)
		}

		if !in(research.Searched, sub) && !in(research.Search, sub) {
			research.Search = append(research.Search, sub)
		}
	}
}

func main() {
	if len(os.Args) != 2 {
		fmt.Println("Usage: censys_domain.go domain")
		os.Exit(0)
	}

	domain := os.Args[1]
	research.Domain = domain
	fmt.Printf("[*] Iteratively searching for subdomains for %s\n", domain)

	results, err := search(domain)
	if err != nil {
		fmt.Printf("\n[-] Error: %s", err)
	}

	process(results, domain)

	for {
		if len(research.Search) == 0 {
			break
		}

		research.Search, domain = pop(research.Search)
		results, err := search(domain)
		if err != nil {
			fmt.Printf("\n[-] Error: %s", err)
			break
		}

		process(results, domain)
	}

	fmt.Println("")
	fmt.Printf("Subdomains for %s\n", research.Domain)
	fmt.Println(strings.Join(research.Hosts, "\n"))
}
