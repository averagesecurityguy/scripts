if [ "$#" -ne 1 ]; then
    echo "Usage: $0 filename" >&2;
    exit 1;
fi

# Run Gobuster against each URL in the file.
IFS=$'\n' read -d '' -r -a hosts < "$1";
gb="gobuster -q -e -s 200 -m dir";
dl="/usr/share/seclists/Discovery/Web_Content/raft-small-directories.txt";
wl="/usr/share/seclists/Discovery/Web_Content/raft-small-files.txt";

for host in ${hosts[@]}; do
    echo "Busting $host";

    $gb -u $host -w $dl;
    $gb -u $host -w $wl;

    echo "";

done
