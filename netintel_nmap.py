#!/usr/bin/env python3

import requests
import sys
import time
import json
import argparse


API_KEY = ""


def get_records(url):
    resp = ''
    status = 0

    while status != 200:
        resp = requests.get(url)
        status = resp.status_code
        time.sleep(2)

    return resp.json()


def get_ipv6s():
    if data.get('ipv6s') is not None:
        records = get_records(data['ipv6s'])
        return '\n'.join(set([ipv6['address'] for ipv6 in records['addresses']]))
    else:
        print('IPv6 address data set not found.')
        sys.exit(1)


def get_externals():
    if data.get('externals') is not None:
        records = get_records(data['externals'])
        return '\n'.join(set([addr['address'] for addr in records['addresses']]))
    else:
        print('External address data set not found.')
        sys.exit(1)


def get_blocks():
    if data.get('blocks') is not None:
        records = get_records(data['blocks'])
        return '\n'.join(set([block['block'] for block in records['blocks']]))

    else:
        print('Network blocks data set not found.')
        sys.exit(1)


#-----------------------------------------------------------------------------
# Main Program
#-----------------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("address_type", help="Must be one of all, ipv6, external, or block.")
parser.add_argument("query_type", help="Must be either domain or report.")
parser.add_argument("query_value", help="Should be a domain name or a report name.")
args = parser.parse_args()

if args.address_type.lower() not in ['all', 'ipv6', 'external', 'block']:
    print(parser.usage)
    sys.exit(1)

if args.query_type.lower() not in ['domain', 'report']:
    print(parser.usage)
    sys.exit(1)

data = {}
if args.query_type == 'domain':
    domain = args.query_value
    url = 'https://pro.netintel.net/lookup.php'

    resp = requests.post(url, data={'domain': domain, 'apikey': API_KEY})
    data = resp.json()
    report_name = data.get('report')[33:-12]
    print('Use this report name for future queries: {0}.'.format(report_name))

    if 'error' in data:
        print('Could not query domain: {0}'.format(data['error']))
        sys.exit(1)
else:
    report = args.query_value
    url = 'https://pro.netintel.net/reports/{0}/report.json'.format(report)
    resp = requests.get(url)

    if resp.status_code == 200:
        data = resp.json()
    else:
        print('Could not find report: {0}'.format(report))
        sys.exit(1)

if args.address_type.lower() == 'ipv6':
    print(get_ipv6s())

elif args.address_type.lower() == 'external':
    print(get_externals())

elif args.address_type.lower() == 'block':
    print(get_blocks())

else:
    print(get_ipv6s())
    print(get_externals())
    print(get_blocks())
