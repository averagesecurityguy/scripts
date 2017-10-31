#!/usr/bin/env python3

import hashlib
import sys
import threading
import queue
import time


THREADS = 400
TIMEOUT = 5
SLEEP = 5


def load_pwds(filename, cred_queue):
    # Load the password candidates into the queue.
    f = open(filename, 'rb')
    fail_count = 0
    for line in f:
        try:
            line = line.decode()
        except UnicodeDecodeError:
            fail_count += 1
            continue

        line = line.rstrip('\r\n')
        if line == '':
            continue

        cred_queue.put(line)

    print('Fail count: {0}'.format(fail_count))
    f.close()


def verify(hashes, cred_queue):
    while fin.isSet() is False:
        try:
            pwd = cred_queue.get(timeout=TIMEOUT)

        except queue.Empty:
            return

        for name, hash in hashes:
            pw = '{0}:mongo:{1}'.format(name, pwd)
            pwhash = hashlib.md5(pw.encode()).hexdigest()

            if pwhash == hash:
                print('{0}:{1}:{2}'.format(name, hash, pwd))


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print('Usage: mongodb_cr_crack.py hashfile wordfile')
        sys.exit(1)

    hashfile = sys.argv[1]
    wordfile = sys.argv[2]
    hashes = []
    cred_queue = queue.Queue()
    fin = threading.Event()

    # Get our hashes.
    for line in open(hashfile):
        line = line.rstrip('\r\n')
        if line != '' and line[0] != '#':
            hashes.append(line.split(':'))

    # Setup the threads for testing the hashes
    for i in range(THREADS):
        t = threading.Thread(target=verify, args=(hashes, cred_queue))
        t.start()

    # Load passwords using a thread.
    t = threading.Thread(target=load_pwds, args=(wordfile, cred_queue))
    t.start()

    # Launch the threads and kill them on Ctrl-C
    try:
        while threading.active_count() > 1:
            time.sleep(SLEEP)

    except KeyboardInterrupt:
        fin.set()
