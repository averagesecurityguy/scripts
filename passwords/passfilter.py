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
import re
import sys

#------------------------------------------------------------------------------
# Function Definitions
#------------------------------------------------------------------------------

def parse_word(word, s):
    """Parses the word and counts the number of digits, lowercase letters,
    uppercase letters, and symbols. Returns a dictionary with the results.
    If any character in the word is not in the set of digits, lowercase
    letters, uppercase letters, or symbols it is marked as a bad character.
    Words with bad characters are not output."""

    count = {'d': 0, 'l': 0, 'u': 0, 's': 0, 'x':0}
    d = '0123456789'
    l = 'abcdefghijklmnopqrstuvwxyz'
    u = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
    for c in word:
        if c in d:
            count['d'] += 1
        elif c in l:
            count['l'] += 1
        elif c in u:
            count['u'] += 1
        elif c in s:
            count['s'] += 1
        else:
            count['x'] += 1

    return count

def parse_requirements(r):
    """Determine which characters are required and the number of them that
    are required."""
    
    req = {'d': 0, 'l': 0, 'u': 0, 's': 0}
    for c in r:
        if c == 'd':
            req['d'] += 1
        elif c == 'l':
            req['l'] += 1
        elif c == 'u':
            req['u'] += 1
        elif c == 's':
            req['s'] += 1
        else:
            continue

    return req
            
def complex_pass(count):
    """Windows complexity requires a password to contain three of the four
    groups: digits, lowercase letters, uppercase letters, or symbols."""

    if count['d'] and count['l'] and count['u']:
        return True
    elif count['d'] and count['l'] and count['s']:
        return True
    elif count['d'] and count['u'] and count['s']:
        return True
    elif count['l'] and count['u'] and count['s']:
        return True
    else:
        return False


def meets_requirements(count, r):
    """Does the password have enough of each type of character to meet the
    requirements?"""
    
    if (count['d'] >= r['d'] and count['l'] >= r['l'] and
    count['u'] >= r['u'] and count['s'] >= r['s']):
        return True
    else:
        return False

    
#------------------------------------------------------------------------------
# Main Program
#------------------------------------------------------------------------------

desc = """Passfilter.py reads a file or stdin and returns words that meet the
defined requirements. For most password policies the set of allowed letters
and numbers is the same. The set of allowed symbols varies widely between
policies. Passfilter.py defines a default set of symbols which can be
overridden using the -s flag.

Examples:
Return all words 3 to 10 characters long.
    passfilter.py -f wordlist

Return all words 3 to 10 characters long that meet the windows complexity
requirements.
    passfilter.py -w -f wordlist

Return all words 5 to 9 characters long that have at least two lowercase
letters and at least one digit.
    passfilter.py -m 5 -x 9 -r lld -f wordlist
"""

parser = argparse.ArgumentParser(prog="Passfilter.py",
                        formatter_class=argparse.RawDescriptionHelpFormatter,
                        description=desc)
group = parser.add_mutually_exclusive_group()
group.add_argument('-w', action='store_true', default=False,
                    help='Passwords must meet Windows complexity requirements.')
group.add_argument('-r', action='store', default='', metavar='string',
                    help='''String representing the character groups and count
                    required.''')
parser.add_argument('-m', action='store', type=int, default='3', metavar='min',
                    help='Minimum password length. (default: 3)')
parser.add_argument('-x', action='store', type=int, default='10', metavar='max',
                    help='Maximum password length. (default: 10)')
parser.add_argument('-s', action='store', default=''' !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~''',
                    help='''Symbols allowed in the password.
(default:  !"#$%%&'()*+,-./:;<=>?@[\]^_`{|}~)''',
                    metavar='symbols')
parser.add_argument('-f', metavar='wordlist',
                    help='Wordlist to parse (default: stdin).')

args = parser.parse_args()

# Open the file or stdin
if args.f:
    try:
        wordlist = open(args.f, 'r')
    except IOError:
        print "Could not open file %s" % args.f
        sys.exit()
else:
    wordlist = sys.stdin

for line in wordlist:

    # Skip blank lines and comments in the word list
    if re.match('^$', line):
        continue
    if re.match('^#.*$', line):
        continue

    # Strip the new line character and check the word for length requirements
    word = line.rstrip('\r\n')
    if len(word) < args.m:
        continue
    if len(word) > args.x:
        continue

    # Count the occurrance of each type of character. 
    count = parse_word(word, args.s)

    # If any character did not match the allowed characters, skip the word
    if count['x'] > 0:
        continue

    # If requirements were provided then check to see if the word meets the
    # requirements. If it does then keep it, if not, move to the next word.
    if args.r:
        if meets_requirements(count, parse_requirements(args.r)):
            print word
            continue
        else:
            continue

    # If we require Windows complexity then check to see if the word meets the
    # windows complexity requirements. If it does then keep it, if not, move to
    # the next word.
    if args.w:
        if complex_pass(count):
            print word
            continue
        else:
            continue
        
    else:
        print word

if wordlist is not sys.stdin:
    wordlist.close()
