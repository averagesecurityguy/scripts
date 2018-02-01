package main

import (
    "os"
    "fmt"
    "encoding/hex"
    "bytes"
    "io/ioutil"
    "crypto/sha256"
    "crypto/hmac"
    "strings"
    "bufio"

    "golang.org/x/crypto/pbkdf2"
)

func check(err error) {
    if err != nil {
        fmt.Printf("Error: %s\n", err)
        os.Exit(0)
    }
}

func decodeHex(hexBytes []byte) []byte {
    decoded := make([]byte, hex.DecodedLen(len(hexBytes)))

	_, err := hex.Decode(decoded, hexBytes)
    check(err)

    return decoded
}

func checkPass(salt, data []byte, target, password string) bool {
    dk := pbkdf2.Key([]byte(password), salt, 10000, 80, sha256.New)

    mac := hmac.New(sha256.New, dk[32:64])
    mac.Write(data)
    sum := mac.Sum(nil)
    candidate := hex.EncodeToString(sum)

    return target == candidate
}

func parseVault(filename string) ([]byte, string, []byte) {
    data, err := ioutil.ReadFile(os.Args[1])
    check(err)

    lines := bytes.Split(data, []byte("\n"))
    hexBytes := bytes.Join(lines[1:], []byte(""))
    decoded := decodeHex(hexBytes)
    params := bytes.Split(decoded, []byte("\n"))

    salt := decodeHex(params[0])
    crypted := decodeHex(params[2])
    hash := string(params[1])

    return salt, hash, crypted
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
        fmt.Println("Usage: vaultcrack <vault_file> <password_file>")
        os.Exit(0)
    }

    wordChan := words(os.Args[2])
    salt, target, crypted := parseVault(os.Args[1])

    for pwd := range wordChan {
        password := pwd
        if checkPass(salt, crypted, target, password) {
                fmt.Printf("Success: %s\n", password)
        }
    }
}
