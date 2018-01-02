#!/usr/bin/env python3

import sys
import dns.resolver
import dns.reversename
import dns.exception
import netaddr
import ipwhois
import threading
import queue
import time


THREAD_COUNT = 256  # Minimum number of threads.
BLOCK_SIZE = 1024  # Smallest netblock on which we will do reverse lookups.
LIFETIME = 10.0  # Total time in seconds we will wait for a DNS response.


# Configure the resolver to use throughout the script.
resolver = dns.resolver.Resolver()
resolver.lifetime = LIFETIME


def parallel(func, items):
    """
    Run the given function in parallel.

    Use multithreading to run the given function and arguments in parallel.
    """
    # Setup the work and results queues and the finish event.
    item_queue = queue.Queue()
    fin = threading.Event()

    # Load the ports into the queue
    for i in items:
        item_queue.put(i)

    # Setup and launch threads.
    for i in range(THREAD_COUNT):
        t1 = threading.Thread(target=func, args=(fin, item_queue))
        t1.start()

    # Wait for threads to complete. Handle Ctrl-C if necessary.
    try:
        old_len = item_queue.qsize()
        while threading.active_count() > 1:
            time.sleep(2)
            new_len = item_queue.qsize()
            if (old_len - new_len) >= 1000:
                print('[+] {0} items remaining.'.format(new_len))
                old_len = new_len

    except KeyboardInterrupt:
        fin.set()


def resolve(fqdn, rtype='A'):
    """
    Resolve a DNS query.

    Query the DNS server for a record of type rtype. The default is A records.
    """
    # Resolve our query and return a list of answers. If there are any
    # exceptions, print the exception and return an empty list.
    try:
        ans = resolver.query(fqdn, rtype)
        return [a.to_text() for a in ans]

    except dns.exception.DNSException:
        return []


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


def brute(fin, word_queue):
    """
    Brute force DNS records for a name.

    Look for A, AAAA, and CNAME records associated with the given word.
    """
    while not fin.isSet():
        # Get a new word to test, if there are no more words exit the thread.
        try:
            word = word_queue.get(timeout=1)

        except queue.Empty:
            return

        # Get A and AAAA records
        fqdn = '{0}.{1}'.format(word, records['domain'])

        ips = resolve(fqdn)
        ips.extend(resolve(fqdn, rtype='AAAA'))
        for ip in ips:
            records['forward'].append((fqdn, netaddr.IPAddress(ip)))

        # Look for CNAME records
        names = resolve(fqdn, rtype='CNAME')

        for name in names:
            # Skip FQDN CNAMEs
            if name.endswith('.'):
                continue

            ips = resolve(name)
            for ip in ips:
                records['forward'].append((name, netaddr.IPAddress(ip)))


def rev_lookup(fin, address_queue):
    """
    Reverse lookup

    Perform a reverse lookup of an IP address and update the reverse dict.
    """
    while not fin.isSet():
        # Get a new address to test, if there are no more addresses exit the
        # thread.
        try:
            addr = address_queue.get(timeout=1)

        except queue.Empty:
            return  # No more addresses, exit thread.

        # Convert the IP to a PTR name.
        revip = dns.reversename.from_address(str(addr))

        # Resolve the PTR name.
        names = resolve(revip, 'PTR')
        for name in names:
            records['reverse'].append((addr, name))


def reverse(addresses, netblocks):
    """
    Reverse lookups

    Perform a reverse lookup on all of the IP addresses identified so far.
    In addition perform reverse lookups on small Netblocks.
    """
    addresses = [a[1] for a in addresses]

    for block in netblocks:
        if block[0].size <= BLOCK_SIZE:
            addresses.extend(block[0])

    parallel(rev_lookup, set(addresses))


def netblock(addresses):
    """
    Find the netblocks that our IP addresses belong to.

    Before doing a whois lookup for the netblock see if the IP address is
    already in our current netblocks.
    """
    for ip in set([a[1] for a in addresses]):
        # If the IP is in one of our netblocks then move on.
        found = False
        for block in records['netblocks']:
            if ip in block[0]:
                found = True
                break

        if found is True:
            continue

        # If the ip is not in one of our netblocks then look up the netblock
        # associated with the IP.
        network = None
        try:
            resp = ipwhois.IPWhois(ip).lookup_rdap()
            network = resp['network']

        except:
            continue

        if network is None:
            continue

        # Process the whois response
        name = network['name']
        if name is None:
            name = 'Unknown'

        # If cidr is present then process it. If it is not present then
        # build the cidr from the range created by the start and end
        # addreses.
        if 'cidr' in network:
            cidr = network['cidr'].split(', ')
            records['netblocks'].extend([(netaddr.IPNetwork(c), name) for c in cidr])
            
        else:
            range = netaddr.IPRange(network['start_address'], network['end_address'])
            records['netblocks'].append((range.cidrs()[0], name))


def usage():
    print('Usage: resolve_mt.py domain.name wordlist')
    sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        usage()

    wordlist = get_words(sys.argv[2])

    records = {'domain': sys.argv[1], 'soa': '', 'nservers': [],
               'mailex': [], 'axfr': [], 'forward': [], 'reverse': [],
               'netblocks': []}

    print(records['domain'].upper())
    print('=' * len(records['domain']))
    print('[*] Get SOA record.')
    ans = resolve(records['domain'], rtype='SOA')
    if ans != []:
        ans = ans[0].split()
        records['soa'] = ans[0].rstrip('.')
 
    print('[*] Getting name servers.')
    records['nservers'] = [n.rstrip('.') for n in resolve(records['domain'], rtype='NS')]

    # Use all name servers to resolve queries
    nservers = []
    for ns in records['nservers']:
        nservers.extend(resolve(ns))
    resolver.nameservers = nservers

    print('[*] Brute forcing domain names.')
    parallel(brute, wordlist)

    print('[*] Getting Net blocks for IP addresses.')
    netblock(records['forward'])

    print('[*] Doing reverse lookups on IP addresses.')
    reverse(records['forward'], records['netblocks'])

    report = []
    report.append(records['domain'].upper())
    report.append('=' * len(records['domain']))
    report.append('Start of Authority')
    report.append('------------------')
    report.append(records['soa'])
    report.append('')
    report.append('Name Servers')
    report.append('------------')
    report.extend(records['nservers'])
    report.append('')
    report.append('Forward Lookups')
    report.append('---------------')
    report.extend(['{0} - {1}'.format(r[0], r[1]) for r in sorted(set(records['forward']))])
    report.append('')
    report.append('Reverse Lookups')
    report.append('---------------')
    report.extend(['{0} - {1}'.format(r[0], r[1]) for r in sorted(set(records['reverse']))])
    report.append('')

    f = open('{0}.txt'.format(records['domain']), 'w')
    f.write('\n'.join(report))
    f.close()
