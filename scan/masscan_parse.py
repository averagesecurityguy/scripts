#!/usr/bin/env python
# Copyright (c) 2016, LCI Technology Group
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  Redistributions of source code must retain the above copyright notice,
#  this list of conditions and the following disclaimer.
#
#  Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
#  Neither the name of LCI Technology Group, LLC., nor the names of its
#  contributors may be used to endorse or promote products derived from this
#  software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import xml.etree.ElementTree
import sys
import re
import os.path


#------------------------------------
# Object to hold Masscan host items
#------------------------------------
class HostItem():

    def __init__(self, ip):
        self.ip = ip
        self.ports = []

    def __str__(self):
        s  = '{0}\n'.format(self.ip)
        s += '{0}\n'.format('=' * len(self.ip))

        for port in self.ports:
            s += '{0}/{1}: '.format(port[0], port[1])
            if port[2] != '':
                s += 'Service: {0} '.format(port[2])
            if port[3] != '':
                s += 'Banner: {0}'.format(port[3])

        s += '\n'

        return s


def usage():
    print("masscan_parse.py masscan_xml_file")
    sys.exit()


def ip_key(ip):
    """
    Return an IP address as a tuple of ints.

    This function is used to sort IP addresses properly.
    """
    return tuple(int(part) for part in ip.split('.'))


def create_host(address, ports):
    """
    Create a new host object.
    """
    h = HostItem(address)

    for port in ports:
        name, banner = get_service(port.find('service'))
        h.ports.append((int(port.attrib['portid']), port.attrib['protocol'], name, banner))

    return h


def get_service(service):
    """
    Get the service name.

    If the product attribute it set then use it otherwise use the name
    attribute.
    """
    if service is None:
        name = ''
        banner = ''

    else:
        name = service.attrib.get('product', None)
        if name is None:
            name = service.attrib.get('name', '')

        banner = service.attrib.get('banner', '')

    return name, banner


def open_masscan_file(filename):
    """
    Open the given Masscan XML file and load it as an XML object.
    """
    if not os.path.exists(filename):
        print("{0} does not exist.".format(filename))
        sys.exit()

    if not os.path.isfile(filename):
        print("{0} is not a file.".format(filename))
        sys.exit()

    try:
        # Load Masscan XML file into the tree and get the root element.
        nf = xml.etree.ElementTree.ElementTree(file=filename)
        root = nf.getroot()

        # Make sure this is an Masscan XML file
        if root.tag == 'nmaprun' and root.attrib['scanner'] == 'masscan':
            return filename, root
        else:
            print('{0} is not a Masscan XML file.'.format(filename))
            sys.exit()

    except Exception as e:
        print('XML Parse Error: {0}'.format(e))
        sys.exit()


if __name__ == '__main__':
    ##
    # Process program arguments
    if len(sys.argv) != 2:
        usage()

    if sys.argv[1] == '-h':
        usage()
    else:
        file_name, mscan = open_masscan_file(sys.argv[1])

    ##
    # Find all the host objects in the Masscan file
    hosts = mscan.findall('host')

    ##
    # Process each of the hosts
    for host in hosts:
        address = host.find('address').attrib['addr']
        ports = host.findall('ports/port')

        if ports != []:
            h = create_host(address, ports)
            print(h)

