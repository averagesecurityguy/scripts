/*
Copyright 2017 LCI Technology Group, LLC

This is a simple insertion shell encoder modeled after the one found here:
https://gist.github.com/geyslan/5376542

Usage of ./insert_encoder:
  -e string
    	Bytes to signal end of encoding (default "f1f1")
  -g string
    	Garbage byte (default "2f")
  -p string
    	Insertion pattern x is garbage byte, b is real byte. (default "xb")
  -s string
    	Shellcode to be encode. (default "0000")

The following command:
./insert_encoder -g 55 -e 3333 -s 0001ff02ffff -p xbb

Results in the following output:
[+] Encoded shellcode with decoder:
\xeb\x1a\x5e\x8d\x3e\x31\xc9\x8b\x1c\x0e\x41\x66\x81\xfb\x33\x33\x74\x0f\x80
\xfb\x55\x74\xf0\x88\x1f\x47\xeb\xeb\xe8\xe1\xff\xff\xff\x55\x00\x01\x55\xff
\x02\x55\xff\xff\x33\x33

I have made no effort to ensure the decoder shellcode is safe. I copied it
directly from the Python script mentioned above.
*/
package main

import (
    "os"
    "fmt"
    "flag"
    "bytes"
    "encoding/hex"
)


func fatal(msg string) {
    fmt.Println(msg)
    os.Exit(1)
}


func decode(s string) []byte {
    h, err := hex.DecodeString(s)

    if err != nil {
        fatal(fmt.Sprintf("Could not decode hex string: %s", err.Error()))
    }

    return h
}


func main () {
    var g string
    var p string
    var e string
    var s string

    flag.StringVar(&g, "g", "2f", "Garbage byte")
    flag.StringVar(&p, "p", "xb", "Insertion pattern x is garbage byte, b is real byte.")
    flag.StringVar(&e, "e", "f1f1", "Bytes to signal end of encoding")
    flag.StringVar(&s, "s", "0000", "Shellcode to be encode.")

    flag.Parse()

    gb := decode(g)
    eb := decode(e)
    sb := decode(s)

    if bytes.Contains(sb, gb) {
        fatal("Shellcode contains the garbage byte. Choose another.")
    }
    if bytes.Contains(sb, eb) {
        fatal("Shellcode contains end pattern. Choose another.")
    }

    var enc []byte

    // Add the decoder routine to our payload
    enc = append(enc, decode("eb1a5e8d3e31c98b1c0e416681fb")...)
    enc = append(enc, eb...)
    enc = append(enc, decode("740f80fb")...)
    enc = append(enc, gb...)
    enc = append(enc, decode("74f0881f47ebebe8e1ffffff")...)

    // Encode our shellcode and add it to the payload
    for i := 0; i < len(sb); i++ {
        for j := 0; j < len(p); j++ {
            if p[j] == 'x' {
                enc = append(enc, gb...)
            } else if p[j] == 'b' {
                enc = append(enc, sb[i])
                i++
            } else {
                // Ignore any unnecessary characters in the pattern.
            }

            if i > len(sb) {
                break
            }
        }

        // If we've reached the end of our pattern i will get incremented by
        // the for loop. Decrement it first so it ends up where we left off.
        i--
    }

    // Add our end byte to the payload.
    enc = append(enc, eb...)

    // Print the final payload
    fmt.Println("[+] Encoded shellcode with decoder:")
    for _, v := range enc {
        fmt.Printf("\\x%02x", v)
    }
    fmt.Println()
}
