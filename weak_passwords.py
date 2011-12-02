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

def password_combos(plist):
    tmp = []
    for p in plist:
        tmp.append(p)
        tmp.append(p + "123")
        tmp.append(p.capitalize())
        tmp.append(p.capitalize() + "123")

    return tmp

#------------------------------------------------------------------------------
# Main Program
#------------------------------------------------------------------------------

#Parse command line arguments using argparse
desc = """weak_passwords.py takes a username or userlist, a company name or
company list and creates a username:password list using commom passwords
cited by Chris Gates (carnal0wnage) and Rob Fuller (mubix) in their talk
"The Dirty Little Secrets They Didn't Teach You In Pentesting Class"
presented at Derbycon 2011.
"""
parser = argparse.ArgumentParser(description=desc)
usergroup = parser.add_mutually_exclusive_group(required=True)
usergroup.add_argument('-u', action='store', default=None,
                    help='Username')
usergroup.add_argument('-U', action='store', default=None,
                    help='List of Usernames')
compgroup = parser.add_mutually_exclusive_group(required=True)
compgroup.add_argument('-c', action='store', default=None,
                    help='Company name')
compgroup.add_argument('-C', action='store', default=None,
                    help='List of potential company names')

args = parser.parse_args()


users = []
comps = []

if args.u:
    users.append(args.u)
if args.U:
    users = list_from_file(args.U)
if args.c:
    comps.append(args.c)
if args.C:
    comps = list_from_file(args.C)

pwds = ["password",
        "password123",
        "Password",
        "Password123",
        "p@ssw0rd",
        "p@ssw0rd123",
        "P@ssw0rd",
        "P@ssw0rd123",
        "p@ssword",
        "p@ssword123",
        "P@ssword",
        "P@ssword123",
        "passw0rd",
        "passw0rd123",
        "Passw0rd",
        "Passw0rd123",
        "welcome",
        "welcome123",
        "Welcome",
        "Welcome123",
        "welc0me",
        "welc0me123",
        "Welc0me",
        "Welc0me123",
        "changeme",
        "changeme123",
        "Changeme",
        "Changeme123"]

pwds.extend(password_combos(comps))
pwds.extend(password_combos(users))

for u in users:
    for p in pwds:
        print '%s:%s' % (u, p)
        

        

