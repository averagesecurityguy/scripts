#!/usr/bin/env python
# Copyright (c) 2013, LCI Technology Group, LLC
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

#
# Gravatar.py takes a file with a list of email address, one on each line, and
# searches Gravatar for information about the email address. If address is
# registered with Gravatar, then selected data points are extracted from the
# Gravatar profile.
#
import sys
import hashlib
import requests

#------------------------------------------------------------------------------
# Functions
#------------------------------------------------------------------------------
def get_gravatar(email):
    '''
    Generate an MD5 hash of the email address and query the Gravatar server
    for the profile associated with that hash. Return the associated data in
    JSON format.
    '''
    email_hash = hashlib.md5(email).hexdigest()
    resp = requests.get('http://en.gravatar.com/{0}.json'.format(email_hash))
    data = {}
    if resp.status_code == 200:
        try:
            print '[+] Found email address {0}.'.format(email) 
            data = resp.json()
        except ValueError:
            print '[-] Could not convert response to JSON.'
    elif resp.status_code == 404:
        pass
    else:
        print '[-] Received status {0}'.format(resp.status_code)

    return data


def get_profile(email):
    '''
    Parse the Gravatar JSON profile to extract specific data points if they
    exist. Return the list of parsed profile entries.
    '''
    prof = get_gravatar(email)
    
    entries = []
    if prof != {}:
        for e in prof['entry']:
            entry = {}
            entry['email'] = email
            entry['username'] = e.get('preferredUsername', '')
            entry['location'] = e.get('currentLocation', '')
            entry['name'] = get_name(e.get('name'))
            entry['accounts'] = get_accounts(e.get('accounts'))
            entries.append(entry)

    return entries


def get_name(name):
    '''
    Extract the formatted name from a name dictionary.
    '''
    if name is None:
        return ''
    elif name == []:
        return ''
    else:
        return name.get('formatted', '')


def get_accounts(data):
    '''
    Build a list of accounts by extracting specific data points if they exist.
    Return the list of accounts extracted.
    '''
    accounts = []
    if data is None:
        return accounts
    else:
        for a in data:
            account = {}
            account['username'] = a.get('username', '')
            account['url'] = a.get('url', '')
            accounts.append(account) 

    return accounts


def print_profile(profile):
    '''
    Print the profile in a readable format.
    '''
    for p in profile:
        print p['email']
        print '-' * len(p['email'])
        print 'Name: {}'.format(p['name'])
        print 'Username: {}'.format(p['username'])
        print 'Location: {}'.format(p['location'])
        print 'Accounts:'
        for account in p['accounts']:
            print '  Username: {}'.format(account['username'])
            print '  URL: {}'.format(account['url'])
        print



#-----------------------------------------------------------------------------
# Main Program
#-----------------------------------------------------------------------------

#
# Parse command line arguments using argparse
#
if len(sys.argv) != 2:
    print 'Usage: gravatar.py email_file'
    sys.exit(1)

email_file = sys.argv[1]

profiles = []
with open(sys.argv[1]) as emails:
    for email in emails:
        email = email.rstrip('\r\n')
        profile = get_profile(email)
        if profile != []:
            profiles.append(profile)

for profile in profiles:
    print_profile(profile)
