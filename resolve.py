#!/usr/bin/env python3

import sys
import dns.resolver
import dns.reversename
import dns.zone
import dns.exception
import netaddr
import ipwhois


atypes = ['A', 'AAAA']
otypes = ['CNAME']


def resolve(fqdn, rtype='A'):
    """
    Resolve a DNS query.

    Query the DNS server for a record of type rtype. The default is A records.
    """
    # Resolve our query and return a list of answers. If there are any
    # exceptions, print the exception and return an empty list.
    ips = []
    try:
        ans = dns.resolver.query(fqdn, rtype)
        ips = [a.to_text() for a in ans]

    except dns.exception.DNSException:
        pass

    return ips


def axfr(domain):
    """
    Zone transfer

    Attempt a zone transfer and process any records found.
    """
    for ns in records['nservers']:
        names = []

        # Try a zone transfer with the specified name server.
        try:
            z = dns.zone.from_xfr(dns.query.xfr(ns, domain))
            names = [z[n].to_text(n) for n in sorted(z.nodes.keys())]
            records['axfr'].append('AXFR request for {0} at {1} was successful.'.format(domain, ns))

        except:
            records['axfr'].append('AXFR request for {0} at {1} was unsuccessful.'.format(domain, ns))

        # Process any records found.
        if names != []:
            process_axfr(ns, domain, names)


def process_axfr(ns, domain, names):
    """
    Process the AXFR records.

    If the AXFR output contains A records add them to the records dictionary.
    If the output contains other relevant records such as CNAMEs attempt to
    find the A records associated with those relevant records.
    """
    for name in names:
        name = name.split()
        n = name[0]
        t = name[3]
        v = ' '.join(name[4:])

        # Parse A and AAAA records from AXFR output
        if t in atypes:
            ip = netaddr.IPAddress(v)
            records['forward'].append(('{0}.{1}'.format(n, domain), ip))

        # Parse CNAME and possibly other records in future from AXFR output.
        if t in otypes:
            if v.endswith('.'):
                fqdn = v  # We already have a fully qualified domain name
            else:
                fqdn = '{0}.{1}'.format(v, domain)  # Build our fqdn

            ips = resolve(fqdn)
            for ip in ips:
                records['forward'].append((fqdn, netaddr.IPAddress(ip)))


def get_words(filename):
    """
    Get the wordlist from the file.
    """
    wordlist = []
    with open(filename) as f:
        for line in f:
            line = line.rstrip()

            if (line != '') and (line[0] != '#'):
                wordlist.append(line)

    return wordlist


def brute(domain, words):
    """
    Brute domain names from a word list.

    Open the wordlist and look for A, AAAA, and CNAME records associated with
    each word in the list.
    """
    count = 0
    all = len(words)
    for word in words:
        # Get A and AAAA records
        fqdn = '{0}.{1}'.format(word, domain)

        ips = resolve(fqdn)
        ips.extend(resolve(fqdn, rtype='AAAA'))
        for ip in ips:
            records['forward'].append((fqdn, netaddr.IPAddress(ip)))

        # Look for CNAME records
        names = resolve(fqdn, rtype='CNAME')

        for name in names:
            ips = resolve(name)
            for ip in ips:
                records['forward'].append((name, netaddr.IPAddress(ip)))

        count += 1
        if (count % 500) == 0:
            print('[+] Processed {0} of {1}.'.format(count, all))


def rev_lookup(addr):
    """
    Reverse lookup

    Perform a reverse lookup of an IP address and update the reverse dict.
    """
    revip = dns.reversename.from_address(addr)
    names = resolve(revip, 'PTR')
    for name in names:
        records['reverse'].append((addr, name))


def reverse(addresses, netblocks):
    """
    Reverse lookups

    Perform a reverse lookup on all of the IP addresses identified so far.
    In addition perform reverse lookups on small Netblocks.
    """
    for addr in set([a[1] for a in addresses]):
        rev_lookup(str(addr))

    for block in netblocks:
        if block[0].size <= 256:
            for addr in block[0]:
                rev_lookup(str(addr))


def netblock(addresses):
    """
    Find the netblocks that our IP addresses belong to.

    Before doing a whois lookup for the netblock see if the IP address is
    already in our current netblocks.
    """
    for ip in set([a[1] for a in addresses]):
        found = False
        for block in records['netblocks']:
            if ip in block[0]:
                found = True
                break

        if found is False:
            resp = None
            try:
                resp = ipwhois.IPWhois(ip).lookup()
            except ipwhois.exceptions.IPDefinedError:
                continue

            for net in resp['nets']:
                name = net['name']
                for c in net['cidr'].split(', '):
                    records['netblocks'].append((netaddr.IPNetwork(c), name))


def usage():
    print('Usage: resolve.py domain.name wordlist')
    sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        usage()

    wordlist = get_words(sys.argv[2])

    records = {'domain': sys.argv[1], 'soa': [], 'nservers': [],
               'mailex': [], 'axfr': [], 'forward': [], 'reverse': [],
               'netblocks': []}

    print('Gathering Data')
    print('==============')
    print('[*] Get SOA record.')
    ans = resolve(records['domain'], rtype='SOA')
    if ans != []:
        ans = ans[0].split()
        records['soa'] = ans[0].rstrip('.')

    print('[*] Getting name servers.')
    records['nservers'] = [n.rstrip('.') for n in resolve(records['domain'], rtype='NS')]

    print('[*] Getting MX records.')
    records['mailex'] = sorted(resolve(records['domain'], rtype='MX'))

    print('[*] Attempting AXFR against name servers.')
    axfr(records['domain'])

    print('[*] Brute forcing domain names. This could take a while.')
    brute(records['domain'], wordlist)

    print('[*] Getting Net blocks for IP addresses.')
    netblock(records['forward'])

    print('[*] Doing reverse lookups on IP addresses.')
    reverse(records['forward'], records['netblocks'])

    print()
    print('Domain Report')
    print('=============')
    print('Start of Authority')
    print('------------------')
    print(records['soa'])
    print()
    print('Name Servers')
    print('------------')
    print('\n'.join(records['nservers']))
    print()
    print('Mail Exchange Records')
    print('---------------------')
    print('\n'.join(records['mailex']))
    print()
    print('Zone Transfer')
    print('-------------')
    print('\n'.join(records['axfr']))
    print()
    print('Forward Lookups')
    print('---------------')
    for rec in sorted(set(records['forward'])):
        print('{0} - {1}'.format(rec[0], rec[1]))
    print()
    print('Reverse Lookups')
    print('---------------')
    for rec in sorted(set(records['reverse'])):
        print('{0} - {1}'.format(rec[0], rec[1]))
    print()
    print('Network Blocks')
    print('--------------')
    for rec in sorted(set(records['netblocks'])):
        print('{0} - {1}'.format(rec[0], rec[1]))
    print()
