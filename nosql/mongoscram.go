package main

import (
    "os"
    "fmt"
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
    User  string
    Salt  []byte
    Key   string
}

func parseHash(hash string) (string, string, []byte) {
    parts := strings.Split(hash, ":")
    user := parts[0]

    parts = strings.Split(parts[2], "$")
    salt := parts[3]
    expected := parts[4]

    for {
        if len(salt) % 3 == 0 { break }
        salt = salt + "="
    }

    //Decode our salt
    decoded, err := base64.StdEncoding.DecodeString(salt)
    if err != nil {
        return "", "", []byte("")
    }

    return user, expected, decoded
}

func calculate_scram(user, pwd string, salt []byte) string {
    /*
    Calculate the MongoDB SCRAM-SHA-1 hash. It varies from the standard
    slightly by calculating the MD5 of the password and hex encoding it before
    putting it through the PBKDF2 function.

    Thanks @StrangeWill for helping me with that.
    */
    str := fmt.Sprintf("%s:mongo:%s", user, pwd)
    pwd_md5 := md5.New().Sum([]byte(str))

    pwd_hex := make([]byte, hex.EncodedLen(len(pwd_md5)))
    hex.Encode(pwd_hex, pwd_md5)

    salted_password := pbkdf2.Key(pwd_hex, salt, 10000, 20, sha1.New)
    
    client_key := hmac.New(sha1.New, salted_password)
    client_key.Write([]byte("Client Key"))    
    
    stored_key := sha1.New()
    stored_key.Write(client_key.Sum(nil))

    return base64.StdEncoding.EncodeToString(stored_key.Sum(nil))
}

// Parse the given file to get the mongo-scram hashes
func hashes(filename string) []string {
    var hashes []string

    data, err := os.Open(filename)
    if err != nil {
        fmt.Printf("Could not open file: %s\n", filename)
    }

    defer data.Close()

    scan := bufio.NewScanner(data)
    for scan.Scan() {
        text := scan.Text()
        if text != "" {
            hashes = append(hashes, text)
        }
    }

    return hashes
}

func words(filename string) <-chan string {
    out := make(chan string)

    go func() {
        // Open our password list
        wordlist, err := os.Open(filename)
        if err != nil {
            panic("Failed to open wordlist")
        }

        defer wordlist.Close()

        // Lazy reading of the wordlist line by line
        scan := bufio.NewScanner(wordlist)
        for scan.Scan() {
            text := scan.Text()

            // Skip "comment" lines
            if strings.HasPrefix(text, "#") == false {
                out <- text
            }
        }

        close(out)
    }()

    return out
}

func main() {
    if len(os.Args) != 3 {
        fmt.Println("Usage: mongoscram hash password_file")
        os.Exit(1)
    }

    hashList := hashes(os.Args[1])
    wordChan := words(os.Args[2])

    for pwd := range wordChan {
        for _, hash := range hashList {
            user, expected, salt := parseHash(hash)
            if user == "" { continue }
            pass := pwd

            go func() {
                calculated := calculate_scram(user, pass, salt)

                if expected == calculated {
                    fmt.Printf("%s:%s\n", user, pass)
                }
            }()
        }
    }
}