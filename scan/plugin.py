#!/usr/bin/env python
# Copyright (c) 2012, AverageSecurityGuy
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#  Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#
#  Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
#  Neither the name of AverageSecurityGuy nor the names of its contributors may
#  be used to endorse or promote products derived from this software without
#  specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
# OF SUCH DAMAGE.

import xml.etree.ElementTree
import sys
import re
import os.path

#------------------------------------
# Object to hold Nessus host items
#------------------------------------

class VulnItem():
    def __init__(self, ip, fqdn, op, port):
        self.ip = ip
        self.fqdn = fqdn
        self.os = op
        self.port = port


class Vulnerability():
    def __init__(self, pid):
        self.pid = pid
        self.name = ''
        self.desc = ''
        self.hosts = []


def usage():
    print("plugin.py nessus_file plugin_id")
    sys.exit()


##
# function to return an IP address as a tuple of ints. Used for sorting by
# IP address.
def ip_key(ip):
    return tuple(int(part) for part in ip.split('.'))


##
# Take the filename and confirm that it exists, is not empty, and is a Nessus
# file.
def open_nessus_file(filename):
    if not os.path.exists(filename):
        print("{0} does not exist.".format(filename))
        sys.exit()

    if not os.path.isfile(filename):
        print("{0} is not a file.".format(filename))
        sys.exit()

    # Load Nessus XML file into the tree and get the root element.
    nf = xml.etree.ElementTree.ElementTree(file=filename)
    root = nf.getroot()

    # Make sure this is a Nessus v2 file
    if root.tag == 'NessusClientData_v2':
        return filename, root
    else:
        print("{0} is not a Nessus version 2 file.".format(filename))
        sys.exit()


#-------------------------#
# Begin the main program. #
#-------------------------#

if len(sys.argv) != 3:
    usage()

if sys.argv[1] == '-h':
    usage()
else:
    file_name, nessus = open_nessus_file(sys.argv[1])
    plugin = sys.argv[2]

vuln = Vulnerability(plugin)

##
# Find all the reports in the Nessus file
reports = nessus.findall('Report')

##
# Process each of the reports
for report in reports:
    report_name = report.attrib['name']

    # Process each host in the report
    report_hosts = report.findall('ReportHost')
    for host in report_hosts:
        hid = ''
        host_properties = host.find('HostProperties')

        for tag in host_properties.findall('tag'):
            if tag.attrib['name'] == 'host-ip':
                hid = tag.text

        # if hid is empty then the host scan did not complete or
        # some other error has occured. Skip this host.
        if (hid == ''):
            continue

        # Find and process all of the ReportItems
        report_items = host.findall('ReportItem')
        for item in report_items:
            item_plugin = item.attrib['pluginID']

            if item_plugin == plugin:
                vuln.name = item.attrib['pluginName']
                vuln.desc = item.find('description').text
                port = '{0}/{1}'.format(item.attrib['port'], item.attrib['protocol'])

                vuln.hosts.append((hid, port))
                continue


print("{0} ({1})".format(vuln.name, vuln.pid))
print("{0}\n".format(vuln.desc))

if len(vuln.hosts) > 0:
    for vi in sorted(vuln.hosts, key=lambda x: ip_key(x[0])):
        print('{0}\t{1}'.format(vi[0], vi[1]))
else:
    print("No vulnerable hosts found.")
