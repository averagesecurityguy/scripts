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

import argparse
import requests
import sys

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------

def load_file(filename, insensitive):
    """
    Load each line of a file into a list and then convert the list to a set to
    get only unique items. The list may be case insensitive.
    """
    items = [line.rstrip('\r\n') for line in open(filename)]
    items = [i.lstrip('/') for i in items]

    if insensitive is True:
        items = [line.lower() for line in items]

    items = set(items)

    print '[+] Loaded {0} items.'.format(len(items))
    return items


def build_filenames(name_list, ext_list):
    """
    Build a list of filnames using the name list and extention list.
    """
    if len(ext_list) == 0:
        names = set(name_list)
    else:
        # Force our extension to start with a dot (.)
        ext_list = ['.{0}'.format(ext.lstrip('.')) for ext in ext_list]
        names = set(['{0}{1}'.format(n, e) for n in name_list for e in ext_list])

    print '[+] Built {0} filenames.'.format(len(names))
    return names


def build_lists(args):
    """
    Load our directory, name, and extensions lists into memory.
    """
    print '[*] Getting enumeration lists.'
    print '[+] Loading directory file {0}.'.format(args.directory_file)
    directory_list = load_file(args.directory_file, args.i)

    name_list = []
    ext_list = []
    filenames = []

    if args.n is not None:
        print '[+] Loading name file {0}.'.format(args.n)
        name_list = load_file(args.n, args.i)

        # Only load extensions if filenames are loaded.
        if args.e is not None:
            print '[+] Loading extension file {0}.'.format(args.e)
            ext_list = load_file(args.e, args.i)

    # Only build filnames if we have a file name list.
    filenames = []
    if args.n is not None:
        print '[+] Building filenames from names and extensions.'
        filenames = build_filenames(name_list, ext_list)

    return directory_list, filenames


def head(url):
    """
    Make a HEAD request to the URL. If we do not get a 404 then the URL is
    valid. If there are any exceptions then return False.
    """
    try:
        resp = s.head(url, timeout=5, verify=False)

    except requests.exceptions.RequestException:
        return False
    
    if resp.status_code in [301, 302]:
        print '[+] Found {0} --> {1} ({2})'.format(url, resp.headers['location'], resp.status_code)
        return url
    elif resp.status_code != 404:
        print '[+] Found {0} ({1})'.format(url, resp.status_code)
        return url
    else:
        return None


def check(base_url, path_list, dir=True):
    """
    Request each of the items in the path list to see if they exist.
    """
    resources = []
    base_url = base_url.rstrip('/')

    # If we have a list of directories force them to end with a forward slash.
    if dir is True:
        path_list = ['{0}/'.format(p.rstrip('/')) for p in path_list]

    for path in path_list:
        url = '{0}/{1}'.format(base_url, path)
        url = head(url)

        if url is not None:
            resources.append(url)

    return resources


def enumerate(server, directory_list, filenames):
    """
    Enumerate directories and files on the web server.
    """
    print '\n[*] Enumerating resources.'
    to_search = [server]
    directories = []
    resources = []

    print '[*] Recursively searching for directories.'
    while len(to_search) != 0:
        base_url = to_search.pop(0)
        print '[*] Searching for directories in {0}'.format(base_url)
        to_search.extend(check(base_url, directory_list))
        directories.append(base_url)
        resources.append(base_url)

    if len(filenames) > 0:
        print '\n[*] Searching for files.'
        for url in directories:
            resources.extend(check(url, filenames, False))

    return resources


def save_resources(filename, resources):
    """
    Save the identified resources to a file.
    """
    with open(filename, 'w') as f:
        for resource in resources:
            f.write('{0}\n'.format(resource))


#-----------------------------------------------------------------------------
# Main Program
#-----------------------------------------------------------------------------

# Parse command line options
desc = """
Web_discover.py enumerates web content using the supplied word lists.
Directories are enumerated recursively. Once all the directories are
enumerated, the script will attempt to enumerate files as well.
"""
parser = argparse.ArgumentParser(description=desc)
parser.add_argument('base_url', action='store',
                    help='Target web server to enumerate.')
parser.add_argument('directory_file', action='store',
                    help="List of directories to enumerate. One per line.")
parser.add_argument('-n', action='store', default=None, metavar='name_file',
                    help="List of filenames to enumerate. One per line.")
parser.add_argument('-e', action='store', default=None, metavar='extension_file',
                    help='List of extensions to append to filenames. One per line.')
parser.add_argument('-i', action='store_true', default=False,
                    help='Use case insensitive directory and filenames.')
parser.add_argument('-o', action='store', default='resources.txt', metavar='output_file',
                    help='Write enumerated resources to a file.')

args = parser.parse_args()

try:
    # Make sure we can connect to the server.
    s = requests.session()
    if head(args.base_url) is None:
        print 'Unable to connect to {0}.'.format(args.base_url)
        sys.exit(1)

    directory_list, filenames = build_lists(args)
    resources = enumerate(args.base_url, directory_list, filenames)
    save_resources(args.o, resources)
except KeyboardInterrupt:
    pass
