if [ "$#" -ne 2 ]; then
    echo "Usage: $0 filename http|https" >&2;
    exit 1;
fi

# Run Gobuster against each IP or hostname in the list on both 80 and 443.
IFS=$'\n' read -d '' -r -a hosts < "$1";
gb="gobuster -q -e -r -s 200 -m dir";
dl="/usr/share/seclists/Discovery/Web_Content/raft-small-directories.txt";
wl="/usr/share/seclists/Discovery/Web_Content/raft-small-files.txt";

for host in ${hosts[@]}; do
    echo "Busting $host";

    if [ "$2" = "http" ]; then
        $gb -u http://$host -w $dl;
        $gb -u http://$host -w $wl;
    fi

    if [ "$2" = "https" ]; then
        gobuster -q -e -m dir -u https://$host -w /usr/share/seclists/Discovery/Web_Content/raft-small-directories.txt;
        gobuster -q -e -m dir -u https://$host -w /usr/share/seclists/Discovery/Web_Content/raft-small-files.txt;
    fi

    echo "";

done
