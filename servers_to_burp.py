import requests
import sys


PROXIES = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080",
}


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'USAGE: find_web_servers.py hostfile'
        sys.exit()

    for url in open(sys.argv[1]):
        resp = requests.get(url, timeout=15, proxies=PROXIES, verify=False)
