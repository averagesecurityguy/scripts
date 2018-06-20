package main

import (
	"flag"
	"fmt"
	"io/ioutil"
	"net"
	"os"
	"strings"
	"sync"
	"time"

	"golang.org/x/net/proxy"
)

var proxyStr string

// Struct to hold our target information.
type Target struct {
	host string
	port string
}

func (t *Target) String() string {
	return fmt.Sprintf("%s:%s", t.host, t.port)
}

// Build a struct to satisfy the proxy.Dialer interface
type direct struct{}

// Add a time out to our Dial so that the connection attempt doesn't hang
// forever.
func (direct) Dial(network, addr string) (net.Conn, error) {
	return net.DialTimeout(network, addr, 10*time.Second)
}

// Open file and split it into strings using sep as the separator.
func items(filename, sep string) []string {
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		fmt.Println(err.Error())
		return nil
	}

	return strings.Split(string(data), sep)
}

// Connect to a target using our proxy
func connect(t Target) {
	var d direct

	// Build the proxy connection
	prx, err := proxy.SOCKS5("tcp", proxyStr, nil, d)
	if err != nil {
		fmt.Printf("Cannot connect to SOCKS server: %s\n", err)
		os.Exit(1)
	}

	conn, err := prx.Dial("tcp", t.String())

	// Do not print timeout errors.
	if nerr, ok := err.(net.Error); ok && nerr.Timeout() {
		return
	}

	// Do not print EOF errors.
	if strings.Contains("EOF", err.Error()) {
		return
	}

	if err != nil {
		fmt.Printf("Error: %s - %s\n", t.String(), err)
		return
	}

	fmt.Printf("Open: %s\n", t.String())
	conn.Close()
}

func main() {
	var hostFile string
	var portFile string
	var threads int

	flag.StringVar(&hostFile, "H", "hosts", "File containing a list of target hosts.")
	flag.StringVar(&portFile, "P", "ports", "File containing a list of target ports.")
	flag.IntVar(&threads, "t", 10, "Number of scanning threads.")
	flag.StringVar(&proxyStr, "p", "127.0.0.1:1080", "Proxy string in host:port format.")

	flag.Parse()

	// Get our hosts and ports
	hosts := items(hostFile, "\n")
	ports := items(portFile, "\n")

	// Create channel and worker pool
	targetChan := make(chan Target, threads)
	processorGroup := new(sync.WaitGroup)
	processorGroup.Add(threads)

	for i := 0; i < threads; i++ {
		go func() {
			for target := range targetChan {
				connect(target)
			}

			processorGroup.Done()
		}()
	}

	for _, host := range hosts {
		for _, port := range ports {
			targetChan <- Target{host, port}
		}
	}

	close(targetChan)
	processorGroup.Wait()

	fmt.Println(ports)
}
