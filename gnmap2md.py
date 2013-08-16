import re
import sys

#-----------------------------------------------------------------------------
# Compiled Regular Expressions
#-----------------------------------------------------------------------------
gnmap_re = re.compile('Host: (.*)Ports:')
version_re = re.compile('# Nmap 6.25 scan initiated')
host_re = re.compile('Host: (.*) .*Ports:')
ports_re = re.compile('Ports: (.*)\sIgnored State:')
os_re = re.compile('OS: (.*)\sSeq Index:')


#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------
def parse_ports(port_str, broken=False):
    '''
    The 6.25 version of Nmap broke the port format by dropping a field. If
    broken is True then assume we have 6.25 output otherwise do not.
    '''
    ports = []
    for port in port_str.split(','):
        if broken == True: 
            num, stat, proto, x, sn, serv, y = port.split('/')
        else:
            num, stat, proto, x, sn, y, serv, z = port.split('/')

        if serv == '':
            service = sn
        else:
            service = serv

        s = '{0}/{1} ({2}) - {3}'.format(proto, num.strip(), stat, service)
        ports.append(s)

    return ports


def parse_gnmap(file_name):
    hosts = {}
    broken = False
    gnmap = open('{0}'.format(file_name), 'r')
    for line in gnmap:
        m = version_re.search(line)
        if m is not None:
            broken = True

        m = gnmap_re.search(line)
        if m is not None:
            h = host_re.search(line)
            p = ports_re.search(line)
            o = os_re.search(line)

            if p is not None:
                ports = parse_ports(p.group(1), broken)
            else:
                ports = ''

            hosts[h.group(1)] = {'os': o.group(1),
                                 'ports': ports}

    gnmap.close()

    return hosts


#-----------------------------------------------------------------------------
# Main Program
#-----------------------------------------------------------------------------

#
# Parse command line options
#
usage = '''
USAGE:

gnmap2md.py gnmap_file_name md_file_name

Converts a Nmap gnmap formatted file into a Markdown formatted file.
'''

if len(sys.argv) != 3:
    print usage
    sys.exit()

#
# Setup global variables
#
gnmap_fname = sys.argv[1]
result_fname = sys.argv[2]

#
# Parse full scan results and write them to a file.
#
print '[*] Parsing Scan results.'
hosts = parse_gnmap(gnmap_fname)

print '[*] Saving results to {0}'.format(result_fname)
out = open(result_fname, 'w')
for host in hosts:
    out.write(host + '\n')
    out.write('=' * len(host) + '\n\n')
    out.write('OS\n')
    out.write('--\n')
    out.write(hosts[host]['os'] + '\n\n')
    out.write('Ports\n')
    out.write('-----\n')
    out.write('\n'.join(hosts[host]['ports']))
    out.write('\n\n\n')

out.close()
print '[*] Parsing results is complete.'
