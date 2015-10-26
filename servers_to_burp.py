import requests
import sys


PROXIES = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080",
}


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'USAGE: servers_to_burp.py hostfile'
        sys.exit()

    for url in open(sys.argv[1]):
        url = url.rstrip('\r\n')
        resp = requests.get(url, timeout=15, proxies=PROXIES, verify=False)
