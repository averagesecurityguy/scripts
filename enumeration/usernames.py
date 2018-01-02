#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2016, LCI Technology Group, LLC
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#
#  Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
#  Neither the name of LCI Technology Group, LLC nor the names of its
#  contributors may be used to endorse or promote products derived from this
#  software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import sys


def get_names(filename):
    items = []
    with open(filename) as f:
        for line in f:
            line = line.rstrip('\r\n')
            if line[0] == '#': continue
            if line == '': continue
            items.append(line)

    return items


#------------------------------------------------------------------------------
# Main Program
#------------------------------------------------------------------------------
patterns = ['flast', 'firstl', 'first.last']

if len(sys.argv) not in [4, 5]:
    print('Usage: usernames.py firsts lasts pattern [domain]')
    print('Valid patterns include {0}'.format(', '.join(patterns)))
    sys.exit()

# Get our pattern and verify it.
p = sys.argv[3]
if p not in patterns:
    print('Pattern must be one of {0}'.format(', '.join(patterns)))
    sys.exit()

# Get the domain if it exists
d = None
if len(sys.argv) == 5:
    d = sys.argv[4]

# Get name lists
fnames = get_names(sys.argv[1])
lnames = get_names(sys.argv[2])


# Build usernames
usernames = []
if p == 'flast':
    for f in 'abcdefghijklmnopqrstuvwxyz':
        for l in lnames:
            usernames.append("{0}{1}".format(f, l))

if p == 'firstl':
    for f in fnames:
        for l in 'abcdefghijklmnopqrstuvwxyz':
            usernames.append("{0}{1}".format(f, l))

if p == 'first.last':
    for f in fnames:
        for l in lnames:
            usernames.append("{0}{1}".format(f, l))

# Add domain if provided.
if d is not None:
    for u in usernames:
        print("{0}@{1}".format(u, d))
else:
    for u in usernames:
        print(u)
