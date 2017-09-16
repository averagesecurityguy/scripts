package main

import (
	"bufio"
	"crypto/tls"
	"flag"
	"fmt"
	"net"
	"os"
	"time"
)

type Config struct {
	verbose   bool
	timeout   time.Duration
	tlsConfig *tls.Config
}

var config Config

func vprint(msg string) {
	if config.verbose {
		fmt.Printf(msg)
	}
}

func fail(err error) {
	if err != nil {
		fmt.Printf("[E] %s\n", err)
		os.Exit(1)
	}
}

func banner() {
	fmt.Println("            [ The SWEET32 Tester ]")
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

func connection(target string) (*tls.Conn, error) {
	// Create a TCP connection.
	conn, err := net.DialTimeout("tcp", target, config.timeout)
	fail(err)

	vprint(fmt.Sprintf("[+] Successfully connected to: %s\n", conn.RemoteAddr()))

	// Create TLS connection using our TCP connection and set a deadline
	// before attempting the handshake. This will ensure the handshake times
	// out.
	tlsconn := tls.Client(conn, config.tlsConfig)
	tlsconn.SetDeadline(time.Now().Add(config.timeout))

	err = tlsconn.Handshake()
	if err != nil {
		return tlsconn, err
	}

	// Reset the deadline to zero.
	tlsconn.SetDeadline(time.Time{})

	// Document cipher suite
	state := tlsconn.ConnectionState()
	vprint(fmt.Sprintf("[+] Using: %s\n", cipherstring(state.CipherSuite)))

	return tlsconn, nil
}

func parse(filename string) []string {
	var targets []string

	data, err := os.Open(filename)
	fail(err)

	defer data.Close()

	scan := bufio.NewScanner(data)
	for scan.Scan() {
		target := scan.Text()
		if target != "" {
			targets = append(targets, target)
		}
	}

	return targets
}

func check(target string) {
	banner()
	fmt.Printf("[*] Testing connection to %s.\n", target)

	conn, err := connection(target)
	defer conn.Close()

	if err == nil {
		// Write data to the connection.
		for i := 1; i <= 10000; i++ {
			send := []byte(fmt.Sprintf("GET / HTTP/1.1\r\nHost: %s\r\n\r\n", target))
			_, err := conn.Write(send)
			if err != nil {
				vprint("\n")
				vprint(fmt.Sprintf("[+] Connection closed after %d requests.\n", i))
				fmt.Printf("[+] %s is not vulnerable.\n", target)
				break
			}

			resp := make([]byte, 512)
			conn.Read(resp)

			if i%20 == 0 {
				vprint(".")
			}

			if i == 10000 {
				vprint("\n")
				vprint(fmt.Sprintf("[-] The server accepted 10000 requests.\n"))
				fmt.Printf("[-] %s is likely vulnerable.\n", target)
			}
		}
		fmt.Println("")
	} else {
		fmt.Printf("[E] %s\n", err)
		fmt.Println("")
	}
}

func main() {
	var verbose bool
	var server string
	var port string
	var filename string

	flag.BoolVar(&verbose, "v", false, "Verbose output.")
	flag.StringVar(&server, "s", "", "IP address or hostname of web server.")
	flag.StringVar(&port, "p", "", "Port number of web server.")
	flag.StringVar(&filename, "f", "", "File containing a list of servers in server:port format.")
	flag.Parse()

	// Configuration
	config.verbose = verbose
	config.timeout = 30 * time.Second
	config.tlsConfig = &tls.Config{
		InsecureSkipVerify: true,
		CipherSuites: []uint16{
			tls.TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA,
			tls.TLS_RSA_WITH_3DES_EDE_CBC_SHA,
		},
	}

	switch {
	case filename != "":
		targets := parse(filename)
		for _, target := range targets {
			check(target)
		}

	case server != "" && port != "":
		target := fmt.Sprintf("%s:%s", server, port)
		check(target)

	default:
		flag.Usage()
	}
}
