import requests

URL = ''
USER_VAR = 'user_id'
PASS_VAR = 'user_pw'


def get_users():
    return ['admin']


def get_pwds():
    return ['Test1', 'Test2', 'Camera1']


for user in get_users():
    for pwd in get_pwds():
        auth = {USER_VAR: user, PASS_VAR: pwd}
        resp = requests.post(URL, data=auth)
        print resp.text
