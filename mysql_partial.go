package main

import (
	"os"
	"fmt"
	"sync"
	"bytes"
	"bufio"
	"crypto/sha1"
	"encoding/hex"
)

const thread_count = 16
var wait sync.WaitGroup


func catch_panic() {
	r := recover()
	if r != nil {
		fmt.Printf("[-] %s\n", r)
	}
}


func hash(pwds chan string, partial []byte) {
	defer wait.Done()

	for pwd := range pwds {
		h1 := sha1.Sum([]byte(pwd))
		h2 := sha1.Sum(h1[:])

		if bytes.Compare(h2[:len(partial)], partial) == 0 {
			fmt.Printf("[+] %s: %x\n", pwd, h2[:])
		}
	}
}


func add(pwd_chan chan string, file *os.File) {
	fmt.Println("[*] Loading words...")
	count := 0

	pscan := bufio.NewScanner(file)
	for pscan.Scan() {
		pwd_chan <- pscan.Text()
		count++
	}

	close(pwd_chan)
	fmt.Printf("[*] %d words loaded.\n", count)
}


func main() {
	defer catch_panic()

	if len(os.Args) != 3 {
		panic("Usage: mysql_partial pass_file partial_hash")
	}

	partial, err := hex.DecodeString(os.Args[2])
	if err != nil {
		panic("The partial hash must be a hex string. (Ex: 001c2f)")
	}

	filename := os.Args[1]
	fmt.Printf("[*] Opening password file: %s\n", filename)

	pass_file, err := os.Open(filename)
	if err != nil {
		panic(fmt.Sprintf("Could not open %s", filename))
	}
	defer pass_file.Close()

	// Create Channels
	pwd_chan := make(chan string, thread_count)
	wait.Add(thread_count)

	// Start the hashing threads.
	for i := 0; i < thread_count; i++ {
		go hash(pwd_chan, partial)
	}

	// Add passwords to the channel then wait for the goroutines to finish.
	add(pwd_chan, pass_file)
	wait.Wait()
}
