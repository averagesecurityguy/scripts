#!/bin/bash
# Excutes a progressive scan on a subnet using nmap.
#  * Discovery
#  * Port Scan
#  * Thorough Scan

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 subnet" >&2
    exit 1
fi

opts="-T4 --open"
pingopts="-sn -PS21-23,25,53,80,443,3389 -PO -PE -PM -PP"

echo "--------"
echo "Finding active hosts"
echo "--------"
echo "nmap $opts $pingopts -oG alive.gnmap $1"
nmap $opts $pingopts -oG alive.gnmap $1

grep "Status: Up" alive.gnmap | awk '{ print $2 }' > targets
count=$(wc -l targets | awk '{ print $1 }')
echo "[+] Found $count active hosts."

echo ""
echo "--------"
echo "Finding open ports"
echo "--------"
echo "nmap $opts -iL targets -p 1-65535 -oG ports.gnmap"
nmap $opts -iL targets -p 1-65535 -oG ports.gnmap

grep -o -E "[0-9]+/open" ports.gnmap | cut -d "/" -f1 | sort -u > ports
count=$(wc -l ports | awk '{ print $1 }')
echo "[+] Found $count unique open ports"

echo ""
echo "--------"
echo "Running full nmap scan"
echo "--------"

portlist=$(tr '\n' , < ports)
echo "nmap $opts -iL targets -p $portlist -A -oA full_scan"
nmap $opts -iL targets -p $portlist -A -oA full_scan
echo "[+] Scan results available in full_scan.*"

