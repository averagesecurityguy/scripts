/*
Copyright 2017 AverageSecurityGuy (Stephen Haywood)

iterhash takes a string and hashes it the specified number of times until a
match is found of the specified count is reached. This can be used to
determine if a password is being iteratively hashed instead of hashed with a
key derivation formula. Supports MD5, SHA1, and SHA256.

Usage:

go run iterhash.go plaintext iterations hashtype hash

or

go build iterhash.go
./iterhash plaintext iterations hashtype hash
*/

package main

import (
  "os"
  "io"
  "fmt"
  "strconv"
  "crypto/md5"
  "crypto/sha1"
  "crypto/sha256"
  "encoding/hex"
)


func usage(msg string) {
  if msg != "" {
    fmt.Printf("Error: %s\n", msg)
  }

  fmt.Println("Usage: iterhash plaintext iterations md5|sha1|sha256 hash")
  os.Exit(1)  
}


func main() {
  if len(os.Args) != 5 {
    usage("")
  }

  // Get arguments
  word := os.Args[1]
  htyp := os.Args[3]
  hash := os.Args[4]
  iter, err := strconv.Atoi(os.Args[2])

  // Validate arguments
  if (err != nil) || (iter <= 0) {
    usage("Iterations should be a numeric value greater than zero")
  }

  _, err = hex.DecodeString(hash)
  if err != nil {
    usage(fmt.Sprintf("%s", err))
  }

  if htyp != "md5" && htyp != "sha1" && htyp != "sha256" {
    usage("Hash type must be one of md5, sha1, or sha256")
  }

  if htyp == "md5" && len(hash) != 32 {
    usage("MD5 hash is not 32 characters.")
  }

  if htyp == "sha1" && len(hash) != 40 {
    usage("SHA1 hash is not 40 characters.")
  }

  if htyp == "sha256" && len(hash) != 64 {
    usage("SHA256 hash is not 64 characters.")
  }

  // Setup our hash object
  h := md5.New()

  if htyp == "sha1" {
    h = sha1.New()
  } else {
    h = sha256.New()
  }

  // Run hash iterations
  w := word

  for i := 1; i <= iter; i++ {
    io.WriteString(h, w)
    w = fmt.Sprintf("%x", h.Sum(nil))

    if w == hash {
      fmt.Printf("Found %s hash after %d iterations.\n", htyp, i)
      os.Exit(0)
    }

    h.Reset()
  }
}