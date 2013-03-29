import multiprocessing
import sys


def check_ssh(password):
    pass


def worker(ip, password):
    """
    The worker function, invoked in a process. 'nums' is a
    list of numbers to factor. The results are placed in
    a dictionary that's pushed to a queue.
    """
    if check_ssh(ip, password) is True:
        print 'Success: {0} - {1}'.format(ip, password)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage: multi_ssh.py server_file password_file'
        sys.exit()

    servers = [line.strip() for line in open(sys.argv[1], 'r')]
    passwords = [line.strip() for line in open(sys.argv[2], 'r')]

    threads = len(servers)
    chunksize = int(len(passwords)/float(threads))
    procs = []

    for i in range(threads):
        p = multiprocessing.Process(
            target=worker,
            args=(passwords[chunksize * i:chunksize * (i + 1)]))
        procs.append(p)
        p.start()

    # Wait for all worker processes to finish
    for p in procs:
        p.join()
