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

type Hash struct {
    User []byte
    Salt []byte
    Key  string
}

func NewHash(hash string) *Hash {
    h := new(Hash)

    parts := strings.Split(hash, ":")
    h.User = []byte(parts[0])

    parts = strings.Split(parts[2], "$")
    salt := parts[3]
    h.Key = parts[4]

    for {
        if len(salt) % 3 == 0 { break }
        salt = salt + "="
    }

    //Decode our salt
    decoded, err := base64.StdEncoding.DecodeString(salt)
    if err == nil {
        h.Salt = decoded
    }

    return h
}

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


func verify_scram(hash *Hash, pwd []byte) {
    /*
    Verify that the username/password combination matches the stored_key.
    */
    var userpass bytes.Buffer

    userpass.Write(hash.User)
    userpass.WriteString(":mongo:")
    userpass.Write(pwd)

    scram := calculate_scram(userpass.Bytes(), hash.Salt)

    if scram == hash.Key {
        fmt.Printf("%s:%s\n", hash.User, pwd)
    }
}

// Parse the given file to get the mongo-scram hashes
func parse(filename string) []*Hash {
    var hashes []*Hash

    data, err := os.Open(filename)
    if err != nil {
        fmt.Printf("Could not open file: %s\n", filename)
    }

    defer data.Close()

    scan := bufio.NewScanner(data)
    for scan.Scan() {
        text := scan.Text()
        if text != "" {
            hash := NewHash(text)
            hashes = append(hashes, hash)
        }
    }

    return hashes
}


func main() {
    if len(os.Args) != 3 {
        fmt.Println("Usage: mongoscram hash password_file")
        os.Exit(1)
    }

    hash_file := os.Args[1]
    pwd_file := os.Args[2]
    hashes := parse(hash_file)
    threads := 10


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
                for _, hash := range hashes {
                    verify_scram(hash, []byte(word))
                }
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