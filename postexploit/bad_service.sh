#!/usr/bin/env sh
# Copyright 2017 AverageSecurityGuy
#
# Simple script to find world writeable directories that are also present
# in bootup scripts. Executables in these directories may provide a way to
# escalate privileges.
#

search ()
{
    ires=$(grep -Rl $1 /etc/init.d/*)
    rres=$(grep -Rl $1 /etc/rc*)
    cres=$(grep -Rl $1 /etc/cron*)
    sres=$(grep -Rl $1 /etc/systemd/*)

    if [ -n "$ires" ] || [ -n "$rres" ] || [ -n "$cres" ] || [ -n "$sres" ]
    then
        echo "\n$1"
        echo "----"

        if [ -n "$ires" ]; then echo $ires | tr ' ' "\n"; fi
        if [ -n "$rres" ]; then echo $rres | tr ' ' "\n"; fi
        if [ -n "$cres" ]; then echo $cres | tr ' ' "\n"; fi
        if [ -n "$sres" ]; then echo $sres | tr ' ' "\n"; fi
        echo
    fi
}


files=$(find / -perm -0002 -type d -print 2>/dev/null)

for d in $files; do
    case "$d" in 
        */tmp*) continue ;;
        */run*) continue ;;
        */dev*) continue ;;
        */proc*) continue ;;
        *) search "$d" ;;
    esac
done;
