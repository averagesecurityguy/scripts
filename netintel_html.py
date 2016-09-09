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
    count = 0

    # Wait a maximum of two minutes for one piece of data
    while (status != 200) and (count != 60):
        resp = requests.get(url)
        status = resp.status_code
        time.sleep(2)
        count += 1

    if count >= 60:
        msg = '''
The data at {0}
could not be read so this data will not be in the report. You can try building
the report again in a few minutes as some domains take a while to process. If
you have tried multiple times and are still unsuccessful in getting a complete
report, please contact stephen@averagesecurityguy.info.
        '''
        print(msg.format(url))
        return {}

    else:
        return resp.json()


def header(heading, text):
    return '<{0}>{1}</{0}>\n'.format(heading, text)


def ul(items, links=False):
    h  = '<ul>\n'
    for item in items:
        if links is True:
            h += '<li><a href="{0}">{0}</a></li>\n'.format(item)
        else:
            h += '<li>{0}</li>\n'.format(item)

    h += '</ul>\n'

    return h


def paragraph(text):
    return '<p>{0}</p>\n'.format(text)


def dns_to_html(key, title):
    h = ''
    if data.get(key) is not None:
        h += header('h2', title)
        records = get_records(data[key])
        if records != {}:
            h += header('h3', 'SOA')
            h += paragraph(records['soa'])
            h += header('h3', 'Name Servers')
            h += ul(records['servers'])

    return h


def list_to_html(key, title, name):
    h = ''
    if data.get(key) is not None:
        h += header('h2', title)
        records = get_records(data[key])
        if records != {}:
            if key in ['links', 'dorks']:
                h += ul(records[name], links=True)
            else:
                h += ul(records[name])

    return h


def axfr_to_html(key, title):
    h = ''
    if data.get(key) is not None:
        h += header('h2', title)
        records = get_records(data[key])
        if records != {}:
            h += header('h3', 'AXFR Servers')
            h += ul(records['servers'])
            h += header('h3', 'AXFR Records')
            h += ul(records['records'])

    return h


def fv_to_html(key, title):
    h = ''
    if data.get(key) is not None:
        h += header('h2', title)
        records = get_records(data[key])
        if records != {}:
            txts = ['{0} ({1})'.format(t['fqdn'], t['value']) for t in records['records']]
            h += ul(sorted(set(txts)))

    return h


def addresses_to_html(key, title):
    h = ''
    if data.get(key) is not None:
        h += header('h2', title)
        records = get_records(data[key])
        if records != {}:
            txts = ['{0} ({1})'.format(t['address'], t['fqdn']) for t in records['addresses']]
            h += ul(sorted(set(txts)))

    return h


def externals_to_html(key, title):
    h = ''
    if data.get(key) is not None:
        h += header('h2', title)
        records = get_records(data[key])
        if records != {}:
            items = []
            for addr in records['addresses']:
                l = '{0} - {1}'.format(addr['address'], addr['fqdn'])
                for link in addr['links']:
                    name = ''
                    if 'shodan' in link:
                        name = 'Shodan'
                    if 'censys' in link:
                        name = 'Censys'
                    if 'mxtoolbox' in link:
                        name = 'MXToolbox'
                    if 'bing' in link:
                        name = 'Bing'

                    l += ' (<a href="{0}">{1}</a>)'.format(link, name)
                items.append(l)

            h += ul(sorted(set(items)))

    return h


def blocks_to_html(key, title):
    h = ''
    if data.get(key) is not None:
        h += header('h2', title)
        records = get_records(data[key])
        if records != {}:
            items = []
            for block in records['blocks']:
                l = '{0} - {1}'.format(block['block'], block['name'])
                for link in block['links']:
                    name = ''
                    if 'shodan' in link:
                        name = 'Shodan'
                    if 'censys' in link:
                        name = 'Censys'
                    l += ' (<a href="{0}">{1}</a>)'.format(link, name)
                items.append(l)

            h += ul(sorted(set(items)))

    return h


def dict_to_html(key, title, name):
    h = ''
    if data.get(key) is not None:
        h += header('h2', title)
        records = get_records(data[key])
        if records != {}:
            h += header('h3', records['url'])
            items = ['{0}: {1}'.format(k, v) for k, v in records[name].items()]
            h += ul(items)

    return h


#-----------------------------------------------------------------------------
# Main Program
#-----------------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("query_type", help="Must be either domain or report.")
parser.add_argument("query_value", help="Should be a domain name or a report name.")
args = parser.parse_args()

if args.query_type.lower() not in ['domain', 'report']:
    print(parser.usage)
    sys.exit(1)


# Get our data from a new query or from an existing report.
data = {}
domain = ''
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
        domain = data['domain']
        data = data['urls']
    else:
        print('Could not find report: {0}'.format(report))
        sys.exit(1)

# Create our HTML report
html = """
<html>
<head>
<head>
  <meta charset="UTF-8">
  <title>NetIntel Pro</title>
  <style>
    *, *:before, *:after {
      -moz-box-sizing: border-box; -webkit-box-sizing: border-box; box-sizing: border-box;
     }

    html {
      margin: 0;
      padding: 0;
    }

    body {
      margin: 0 auto;
      padding: 0;
      width: 95%;
      background-color: #fff;
      font-family: "Century Gothic", Calibri, Tahoma, sans-serif;
      font-size: 16px;
      color: #000;
    }

    h1, h2, h3, h4 {
      margin: 1.65em 0 0 0;
      padding: 0;
      font-family: Copperplate, Cambria, Georgia, serif;
      color: #000;
      font-weight: bold;
    }

    h1 {
      color: #ffcc33;
      text-align: center;
      font-size: 2.5em;
    }

    h2 {
      font-size: 2.0em;
    }

    h3 {
      margin: .75em 0 0 0;
      font-size: 1.5em;
    }

    h4 {
      font-size: 1em;
    }

    p {
      font-size: 1em;
      color: #000;
      margin: 0 0 .5em 0;
      padding: 0;
    }

    a {
      color: #f00;
      text-decoration: none;
      -webkit-transition: opacity 0.2s linear;
      -moz-transition: opacity 0.2s linear;
      -o-transition: opacity 0.2s linear;
      transition: opacity 0.2s linear;
    }

    a:hover {
      opacity: .5;
    }

    ul {
      margin: 0;
      padding: 0;
      list-style-type: none;
    }

    footer {
        margin: 1em 0 0 0;
    }
</style>
</head>
<body>
"""
html += '<header><h1>NetIntel Pro Report for {0}</h1></header>'.format(domain)
html += dns_to_html('dns', 'DNS Servers')
html += list_to_html('mxs', 'MX Records', 'servers')
html += axfr_to_html('axfr', 'Zone Transfer')
html += fv_to_html('txts', 'TXT Records')
html += fv_to_html('cnames', 'CNAME Records')
html += addresses_to_html('internals', 'Internal IP Addresses')
html += externals_to_html('externals', 'External IPv4 Addresses')
html += addresses_to_html('ipv6s', 'External IPv6 Addresses')
html += blocks_to_html('blocks', 'Network Blocks')
html += dict_to_html('headers', 'HTTP Headers', 'headers')
html += dict_to_html('agents', 'User Agent Responses', 'responses')
html += list_to_html('links', 'Domain Links', 'links')
html += list_to_html('dorks', 'Google Dorks', 'links')
html += """
<footer>
<p>Report produced from data at <a href="https://pro.netintel.net">NetIntel Pro</a></p>
</footer>
</body>
</html>
"""

report_name = 'report_{0}.html'.format(int(time.time()))
with open(report_name, 'w') as f:
    f.write(html)

print('HTML report saved in {0}'.format(report_name))
