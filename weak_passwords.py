#!/usr/bin/python
#Copyright (C) 2011 Stephen Haywood aka Averagesecurityguy
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import sys
import argparse

#------------------------------------------------------------------------------
# Functions
#------------------------------------------------------------------------------

def list_from_file(filename):
    tmp = []
    try:
        f = open(filename, 'r')
    except:
        print "Could not open file: %s" % f.name()

    for line in f:
        tmp.append(line.rstrip('\r\n'))

    return tmp
	
def combos(word):
    tmp = []
    tmp.append(word)
    tmp.append(word + word)
    tmp.append(word + "123")

    for i in xrange(0,10):
        tmp.append(word + str(i))
        tmp.append(word + "0" + str(i))

	tmp.append(word + "10")

    for i in xrange(2000,2016):
        tmp.append(word + str(i))

    return tmp

def password_combos(plist):
    pwd = []
    for p in plist:
        pwd.extend(combos(p))
        pwd.extend(combos(p.capitalize()))
        
    return pwd
    
#------------------------------------------------------------------------------
# Main Program
#------------------------------------------------------------------------------

#Parse command line arguments using argparse
desc = """weak_passwords.py takes a username or userlist, a company name or
company list (optional) and a wordlist (optional) and creates username and 
password combinations formatted for use in Metasploit. The script includes 
some common passwords cited by Chris Gates (carnal0wnage) and Rob Fuller 
(mubix) in their talk "The Dirty Little Secrets They Didn't Teach You In 
Pentesting Class" presented at Derbycon 2011. The passwords are transformed
using some of the best64 rules from hashcat.
"""
parser = argparse.ArgumentParser(description=desc)
usergroup = parser.add_mutually_exclusive_group(required=True)
usergroup.add_argument('-u', action='store', default=None, metavar="USERS",
                    help='Comma delimited list of usernames')
usergroup.add_argument('-U', action='store', default=None, metavar="USERFILE",
                    help='File with list of Usernames.')
compgroup = parser.add_mutually_exclusive_group(required=False)
compgroup.add_argument('-c', action='store', default=None, metavar="COMPANIES",
                    help='Comma delimited list of company names')
compgroup.add_argument('-C', action='store', default=None, metavar="COMPANYFILE",
                    help='File with list of company names.')
wordgroup = parser.add_mutually_exclusive_group(required=False)
wordgroup.add_argument('-w', action='store', default=None, metavar="WORDS",
                    help='Comma delimited list of words')
wordgroup.add_argument('-W', action='store', default=None, metavar="WORDFILE", 
                    help='File with list of words to transform.')

args = parser.parse_args()
users = []
comps = []
pwds = []
words = []

if args.u:
    users.extend(args.u.split(","))
if args.U:
    users = list_from_file(args.U)
if args.c:
    comps.extend(args.c.split(","))
if args.C:
    comps = list_from_file(args.C)
if args.w:
    words.extend(args.w.split(","))
if args.W:
    words = list_from_file(args.W)

words.extend ([ "password", "passw0rd", "p@ssword", "p@ssw0rd", "welcome",
                "welc0me", "w3lcome", "w3lc0me", "changeme", "winter", 
                "spring", "summer", "fall", "security"])

pwds.extend(password_combos(comps))
pwds.extend(password_combos(words))

for u in users:
    for p in pwds:
        print '%s %s' % (u, p)
    for p in password_combos([u]):
        print '%s %s' % (u, p)
