package main

import (
    "os"
    "fmt"
    "crypto/tls"
)


func check(e error) {
    if e != nil {
        fmt.Println(e)
        os.Exit(1)
    }
}


func cipherstring(i uint16) string {
    switch {
    case i == 0x000a:
        return "TLS_RSA_WITH_3DES_EDE_CBC_SHA"
    case i == 0xc012:
        return "TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA"
    default:
        return ""
    }
}


func main() {

    if len(os.Args) != 3 {
        fmt.Println("Usage go run sweet32.go server port")
        os.Exit(0)
    }

    host := os.Args[1]
    port := os.Args[2]
    server := fmt.Sprintf("%s:%s", host, port)


    // Build TLS Config
    conf := &tls.Config{
        InsecureSkipVerify: true,
        CipherSuites: []uint16{
            tls.TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA,
            tls.TLS_RSA_WITH_3DES_EDE_CBC_SHA,
        },
    }

    conn, err := tls.Dial("tcp", server, conf)
    check(err)
    defer conn.Close()

    state := conn.ConnectionState()
    fmt.Printf("Successfully connected to: %s\n", conn.RemoteAddr())
    fmt.Printf("Using: %s\n", cipherstring(state.CipherSuite))


    for i := 1; i <= 10000; i++ {
        send := []byte(fmt.Sprintf("GET / HTTP/1.1\r\nHost: %s\r\n\r\n", server))
        _, err = conn.Write(send)

        resp := make([]byte, 512)
        _, err = conn.Read(resp)
        if err != nil {
            if err.Error() == "EOF" {
                fmt.Println("\n")
                fmt.Printf("Connection closed after %d requests. Server is not vulnerable.\n", i)
                break
            }
        }

        if i % 20 == 0 {
            fmt.Printf(".")
        }

        if i == 10000 {
            fmt.Println("\n")
            fmt.Println("The server accepted 10000 requests. Server is likely vulnerable.")
        }
    }
    fmt.Println("\n")
}