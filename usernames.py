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

#------------------------------------------------------------------------------
# Main Program
#------------------------------------------------------------------------------
patterns = ['flast', 'firstl', 'first.last']

if len(sys.argv) != 4:
    print 'Usage: usernames.py firsts lasts pattern'
    print 'Valid patterns include {0}'.format(', '.join(patterns))
    sys.exit()

p = sys.argv[3]

if p not in patterns:
    print 'Pattern must be one of {0}'.format(', '.join(patterns))
    sys.exit()

for last in open(sys.argv[2]):
    last = last.rstrip('\r\n')
    for first in open(sys.argv[1]):
        first = first.rstrip('\r\n')
        if p == 'flast':
            print '{0}{1}'.format(first[0], last)
        if p == 'firstl':
            print '{0}{1}'.format(first, last[0])
        if p == 'first.last':
            print '{0}.{1}'.format(first, last)
