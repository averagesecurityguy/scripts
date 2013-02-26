#!/usr/bin/env python

import sys
import subprocess

if len(sys.argv) != 2:
    print 'USAGE: sw_ike.py target_file'

for line in open(sys.argv[1], 'r'):
    target = line.strip()
    cmd = 'ike-scan {0} -A -id GroupVPN -Ppsk_{0}.txt'.format(target)
    subprocess.call(cmd)
