package main

import (
    "os"
    "fmt"
    "sync"
    "bytes"
    "bufio"
    "strings"
    "crypto/hmac"
    "crypto/sha1"
    "crypto/md5"
    "encoding/base64"
    "encoding/hex"
    "golang.org/x/crypto/pbkdf2"
)


func calculate_scram(pwd, salt []byte) string {
    /*
    Calculate the MongoDB SCRAM-SHA-1 hash. It varies from the standard
    slightly by calculating the MD5 of the password and hex encoding it before
    putting it through the PBKDF2 function.

    Thanks @StrangeWill for helping me with that.
    */
    digested_password := md5.New()
    digested_password.Write(pwd)
    hex_md5 := hex.EncodeToString(digested_password.Sum(nil))

    salted_password := pbkdf2.Key([]byte(hex_md5), salt, 10000, 20, sha1.New)
    
    client_key := hmac.New(sha1.New, salted_password)
    client_key.Write([]byte("Client Key"))    
    
    stored_key := sha1.New()
    stored_key.Write(client_key.Sum(nil))

    return base64.StdEncoding.EncodeToString(stored_key.Sum(nil))
}


func verify_scram(user, pwd, salt []byte, stored_key string) {
    /*
    Verify that the username/password combination matches the stored_key.
    */
    var userpass bytes.Buffer
    userpass.Write(user)
    userpass.WriteString(":mongo:")
    userpass.Write(pwd)

    hash := calculate_scram(userpass.Bytes(), salt)

    if hash == stored_key {
        fmt.Printf("%s:%s\n", user, pwd)
    }
}


func main() {
    if len(os.Args) != 5 {
        fmt.Println("Usage: scram username password_file salt stored_key")
        os.Exit(1)
    }

    name := os.Args[1]
    pwd_file := os.Args[2]
    salt := os.Args[3]
    stored_key := os.Args[4]
    threads := 10

    //Decode our salt
    salt_byte, err := base64.StdEncoding.DecodeString(salt)
    if err != nil {
        panic("Could not decode salt.")
    }

    /*
    Everything below this point was blatantly stolen from @TheColonial's
    excellent gobuster program. https://github.com/OJ/gobuster

    Thanks @TheColonial
    */

    // Open our password list
    wordlist, err := os.Open(pwd_file)
    if err != nil {
        panic("Failed to open wordlist")
    }

    // channels used for comms
    wordChan := make(chan string, threads)

    // Use a wait group for waiting for all threads to finish
    processorGroup := new(sync.WaitGroup)
    processorGroup.Add(threads)

    // Create goroutines for each of the number of threads
    // specified.
    for i := 0; i < threads; i++ {
        go func() {
            for {
                word := <-wordChan

                // Did we reach the end? If so break.
                if word == "" {
                    break
                }

                // Mode-specific processing
                verify_scram([]byte(name), []byte(word), salt_byte, stored_key)
            }

            // Indicate to the wait group that the thread
            // has finished.
            processorGroup.Done()
        }()
    }

    defer wordlist.Close()

    // Lazy reading of the wordlist line by line
    scanner := bufio.NewScanner(wordlist)
    for scanner.Scan() {
        word := scanner.Text()

        // Skip "comment" lines
        if strings.HasPrefix(word, "#") == false {
            wordChan <- word
        }
    }

    close(wordChan)
    processorGroup.Wait()    
}