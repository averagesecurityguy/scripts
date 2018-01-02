#!/usr/bin/env python
import requests
import urllib
import sys
import re
import multiprocessing
import Queue

cookie_re = re.compile(r'.*?=([0-9A-Za-z%]+)--([0-9a-f]+);')

def unquote(data):
    udata = urllib.unquote(data)
    if data == udata:
        return udata.replace('\n', '%0A')
    else:
        return unquote(udata)


def extract_session_digest(cookie):
    m = cookie_re.match(cookie)
    if m is not None:
        return unquote(m.group(1)), m.group(2)
    else:
        return None, None


def worker(url_queue, cookie_queue):
    print '[*] Starting new worker thread.'
    while True:
        # If there are no urls to access, stop the thread
        try:
            url = url_queue.get(timeout=10)
            if verbose: print '[*] Accessing {0}'.format(url)
        except Queue.Empty:
            print '[-] URL queue is empty, quitting.'
            return

        # Access the URL and process the set-cookie header value.
        try:
            resp = requests.get(url, timeout=5)
        except:
            print '[-] Could not access {0}'.format(url)
            continue

        try:
            cookie = resp.headers['set-cookie']
        except KeyError:
            cookie = None

        if cookie is not None:
            session, digest = extract_session_digest(cookie)
            if session is not None:
                print '[*] Found matching cookie for {0}.'.format(url)
                cookie_queue.put('{0}::{1}::{2}'.format(url, session, digest))


def process_file(filename):
    url_queue = multiprocessing.Queue()
    cookie_queue = multiprocessing.Queue()
    procs = []

    # Create one thread for each processor.
    for i in range(4):
        p = multiprocessing.Process(target=worker, args=(url_queue,
                                                         cookie_queue))
        procs.append(p)
        p.start()

    # Load the URLs into the queue
    for line in open(filename):
        url = 'http://' + line.rstrip('\r\n')
        url_queue.put(url)

    # Wait for all worker processes to finish
    for p in procs:
        p.join()

    # Write the cookies to a file.
    outfilename = 'results_' + filename
    outfile = open(outfilename, 'w')
    while not cookie_queue.empty():
        outfile.write(cookie_queue.get() + '\n')

    outfile.close()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: rails_find.py url_file'
        sys.exit()

    verbose = False
    filename = sys.argv[1]
    print '[*] processing file {0}'.format(filename)
    process_file(filename)