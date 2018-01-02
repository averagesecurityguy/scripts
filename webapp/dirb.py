#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2014, LCI Technology Group, LLC
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
import subprocess
import re

#
# Define the paths to dirb, the wordlists to use, and the file to save the
# enumerated resources into. These paths are based on Kali Linux; if dirb and
# the word lists are installed in a different location on your computer, you
# will need to modify these paths.
#
DIRB_PATH = '/usr/bin/dirb'
WORD_PATH = '/usr/share/wordlists/dirb'
WORD_LIST = '{0}/small.txt'.format(WORD_PATH)
EXT_LIST = '{0}/extensions_common.txt'.format(WORD_PATH)
RESOURCES = 'dirb_resources.txt'

#
# Compiled regular expressions use to parse the dirb output.
#
dir_re = re.compile(r'==> DIRECTORY: (.*?)')
relo_re = re.compile(r'\+ (.*?) \(CODE:3')
file_re = re.compile(r'\+ (.*?) \(CODE:^[3]')
fatal_re = re.compile(r'FATAL: (.*?)')


def run_command(cmd):
    """
    Run the command specified and search for any FATAL errors in the output.
    If there are errors, then print them and exit. If not, return the
    response.
    """
    p = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    resp = p.stdout.read()
    p.stdout.close()

    m = fatal_re.search(resp)
    if m is not None:
        print '[-] {0}'.format(m.group(1))
        sys.exit(1)

    return resp


def find_directories(url):
    """
    Launch the dirb command against the specified url to find directories.
    """
    print '[*] Searching for directories at {0}.'.format(url)
    cmd = '{0} {1} {2} -Slrsiw'.format(DIRB_PATH, url, WORD_LIST)
    resp = run_command(cmd)

    dirs = dir_re.findall(resp)
    files = file_re.findall(resp)
    files.extend(relo_re.findall(resp))

    dirs = ['{0}/'.format(d.rstrip('/')) for d in dirs]

    for dir in dirs:
        print '[+] {0}'.format(dir)

    return dirs, files


def find_files(url):
    """
    Launch the dirb command against the specified URL to find files.
    """
    print '[*] Searching for files in {0}.'.format(url)
    cmd = '{0} {1} {2} -x {3} -Srsiw'.format(DIRB_PATH, url, WORD_LIST, EXT_LIST)
    resp = run_command(cmd)

    files = file_re.findall(resp)
    files.extend(relo_re.findall(resp))

    for f in files:
        print '[+] {0}'.format(f)

    return files


def enumerate(target):
    """
    Use dirb to enumerate content on the target.
    """
    target = '{0}/'.format(target.rstrip('/'))
    to_search = [target]
    directories = []
    resources = []

    print '\n[*] Recursively searching for directories.'
    while len(to_search) != 0:
        base_url = to_search.pop(0)
        dirs, files = find_directories(base_url)
        to_search.extend(dirs)
        directories.append(base_url)
        resources.append(base_url)
        resources.extend(files)

    print '\n[*] Searching for files.'
    for url in directories:
        resources.extend(find_files(url))

    return resources


def save(resources):
    """
    Save the resources to a file.
    """
    with open('dirb_resources.txt', 'w') as f:
        for resource in resources:
            f.write('{0}\n'.format(resource))


def main():
    # Parse command line options
    usage = """
    Dirb.py is a wrapper script for the dirb enumeration tool written by
    The Dark Raver. The script uses mulitple calls to dirb to recursively
    enumerate directories and file on a web server. All searches are case
    insensitive.

    Usage:
    dirb.py target_url
    """

    if len(sys.argv) != 2:
        print usage
        sys.exit(1)

    resources = enumerate(sys.argv[1])
    save(set(resources))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
