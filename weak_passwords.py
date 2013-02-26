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
    adds = []

    adds.extend(['$', '123', '456', '789', '69', '6969', '89', '99', '1234'])
    adds.extend(['33', '44', '55', '66', '77', '88', '1977', '1978', '1979'])
    adds.extend(['1234', '4321', '007', '2112', '!', '@', '#', ])

    for i in xrange(0, 10):
        adds.append(str(i))
        adds.append("0" + str(i))

    for i in xrange(10, 23):
        adds.append(str(i))

    for i in xrange(1990, 2013):
        adds.append(str(i))

    tmp = []

    tmp.append(word)
    tmp.append(word + word)
    for a in adds:
        tmp.append(word + a)
        tmp.append(a + word)

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
                "spring", "summer", "fall", "security", "123456", "12345678",
                "abc123", "qwerty", "monkey", "letmein", "dragon", "111111",
                "baseball", "iloveyou", "trustno1", "1234567", "sunshine",
                "master", "123123", "shadow", "shad0w", "ashley", "football",
                "f00tball", "footb@ll", "f00tb@ll", "jesus", "michael", 
                "ninja", "mustang"])

pwds.extend(password_combos(comps))
pwds.extend(password_combos(words))

for u in users:
    for p in pwds:
        print '%s %s' % (u, p)
    for p in password_combos([u]):
        print '%s %s' % (u, p)
