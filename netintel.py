#!/usr/bin/env python3

import requests
import sys
import time
import json


API_KEY = ""


def get_records(url):
    resp = ''    
    status = 0

    while status != 200:
        resp = requests.get(url)
        status = resp.status_code
        time.sleep(2)

    return resp.json()


def process_data(key, title):
    if data.get(key) is not None:
        print(title)
        print('=' * len(title))
        records = get_records(data[key])
        print(json.dumps(records, indent=2))
        print()


if len(sys.argv) != 2:
    print('Usage: netintel.py domain_name')
    sys.exit(1)


domain = sys.argv[1]
url = 'http://pro.netintel.net/lookup.php'

resp = requests.post(url, data={'domain': domain, 'apikey': API_KEY})
data = resp.json()

if 'error' in data:
    print('Could not query domain: {0}'.format(data['error']))
    sys.exit(1)

# Process our URLs
process_data('dns', 'DNS Servers')
process_data('mxs', 'MX Records')
process_data('axfr', 'Zone Transfer')
process_data('headers', 'HTTP Headers')
process_data('agents', 'User Agent Responses')
process_data('txts', 'TXT Records')
process_data('cnames', 'CNAME Records')
process_data('internals', 'Internal IP Addresses')
process_data('externals', 'External IPv4 Addresses')
process_data('ipv6s', 'IPv6 Addresses')
process_data('blocks', 'Network Blocks')

