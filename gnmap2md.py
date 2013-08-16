#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, AverageSecurityGuy
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#   Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
#   Neither the name of AverageSecurityGuy nor the names of its contributors may
#   be used to endorse or promote products derived from this software without
#   specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
# OF SUCH DAMAGE.

import re
import sys

#-----------------------------------------------------------------------------
# Compiled Regular Expressions
#-----------------------------------------------------------------------------
gnmap_re = re.compile('Host: (.*)Ports:')
version_re = re.compile('# Nmap 6.25 scan initiated')
host_re = re.compile('Host: (.*) .*Ports:')
ports_re = re.compile('Ports: (.*)\sIgnored State:')
os_re = re.compile('OS: (.*)\sSeq Index:')


#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------
def parse_ports(port_str, broken=False):
    '''
    The 6.25 version of Nmap broke the port format by dropping a field. If
    broken is True then assume we have 6.25 output otherwise do not.
    '''
    ports = []
    for port in port_str.split(','):
        if broken == True: 
            num, stat, proto, x, sn, serv, y = port.split('/')
        else:
            num, stat, proto, x, sn, y, serv, z = port.split('/')

        if serv == '':
            service = sn
        else:
            service = serv

        s = '{0}/{1} ({2}) - {3}'.format(proto, num.strip(), stat, service)
        ports.append(s)

    return ports


def parse_gnmap(file_name):
    hosts = {}
    broken = False
    gnmap = open('{0}'.format(file_name), 'r')
    for line in gnmap:
        m = version_re.search(line)
        if m is not None:
            broken = True

        m = gnmap_re.search(line)
        if m is not None:
            # Get Hostname
            h = host_re.search(line)
            if h is None:
                host = 'Unknown'
            else:
                host = h.group(1)

            # Get Ports
            p = ports_re.search(line)
            if p is not None:
                ports = parse_ports(p.group(1), broken)
            else:
                ports = ''

            # Get OS
            o = os_re.search(line)
            if o is None:
                os = 'Unknown'
            else:
                os = o.group(1) 

            hosts[host] = {'os': os,
                           'ports': ports}

    gnmap.close()

    return hosts


#-----------------------------------------------------------------------------
# Main Program
#-----------------------------------------------------------------------------

#
# Parse command line options
#
usage = '''
USAGE:

gnmap2md.py gnmap_file_name md_file_name

Converts a Nmap gnmap formatted file into a Markdown formatted file.
'''

if len(sys.argv) != 3:
    print usage
    sys.exit()

#
# Setup global variables
#
gnmap_fname = sys.argv[1]
result_fname = sys.argv[2]

#
# Parse full scan results and write them to a file.
#
print '[*] Parsing Scan results.'
hosts = parse_gnmap(gnmap_fname)

print '[*] Saving results to {0}'.format(result_fname)
out = open(result_fname, 'w')
for host in hosts:
    out.write(host + '\n')
    out.write('=' * len(host) + '\n\n')
    out.write('OS\n')
    out.write('--\n')
    out.write(hosts[host]['os'] + '\n\n')
    out.write('Ports\n')
    out.write('-----\n')
    out.write('\n'.join(hosts[host]['ports']))
    out.write('\n\n\n')

out.close()
print '[*] Parsing results is complete.'
