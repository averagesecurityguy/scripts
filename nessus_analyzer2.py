#!/usr/bin/env python
#-----------------------------------------------------------------------------
# 
#-----------------------------------------------------------------------------

import xml.etree.ElementTree
import sys
import re
import os.path

#------------------------------------
# Object to hold Nessus host items
#------------------------------------

class HostItem():

	def __init__(self, ip, fqdn, os):
		self.ip = ip
		self.fqdn = fqdn
		self.os = os
		self.tcp_ports = []
		self.udp_ports = []
		self.vulns = []
		self.users = []
		self.webservers = []
		self.snmp = []

class Vulnerability():

	def __init__(self, pid, name, desc):
		self.pid = pid
		self.name = name
		self.desc = desc
		self.hosts = []

def usage():
	print("nessus-analyzer.py nessus_file")
	sys.exit()

def ip_key(ip):
    return tuple(int(part) for part in ip.split('.'))
	
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

def process_host_properties(host_properties):
	ip = ''
	os = 'Unknown'
	fqdn = ''
	for tag in host_properties.findall('tag'):
		if tag.attrib['name'] == 'host-ip':
			ip = tag.text
		if tag.attrib['name'] == 'operating-system':
			os = tag.text
		if tag.attrib['name'] == 'host-fqdn':
			fqdn = tag.text

	return ip, fqdn, os

def process_port(hid, protocol, port):
	p = int(port)

	if protocol == 'tcp' and p != 0:
		if not p in host_items[hid].tcp_ports:
				host_items[hid].tcp_ports.append(p)
	
	if protocol == 'udp' and p != 0:
		if not p in host_items[hid].udp_ports:
			host_items[hid].udp_ports.append(p)

def process_users(hid, text):
	for line in text.split('\n'):
		m = re.search(r' - (.*)$', line)
		if m:
			if re.search(r'\$', m.group(1)):
				pass
			else:
				if not (m.group(1) in host_items[hid].users):
					host_items[hid].users.append(m.group(1))

def process_snmp(hid, plugin, text):
	if plugin == '41028' and not ('public' in host_items[hid].snmp):
		host_items[hid].snmp.append('public')

	for line in text.split('\n'):
		m = re.search(r' - (.*)$', line)
		if m:
			if not (m.group(1) in host_items[hid].snmp):
				host_items[hid].snmp.append(m.group(1))

def process_vulnerability(hid, item):
	pid = item.attrib['pluginID']
	name = item.attrib['pluginName']
	desc = item.find('description').text
	
	if pid in vulns.keys():
		vulns[pid].hosts.append(hid)
	else:
		vulns[pid] = Vulnerability(pid, name, desc)
		vulns[pid].hosts.append(hid)

def process_web_server(hid, port):
	host_items[hid].webservers.append((hid, port))

def host_name_html(ip, name):
	if name == '':
		return "<h2>{0}</h2>\n".format(ip)
	else:
		return "<h2>{0}({1})</h2>\n".format(ip, name)


#-------------------------#
# Begin the main program. #
#-------------------------#
host_items = {}
vulns = {}


##
# Process program arguments
if len(sys.argv) != 2:
	usage()
	
if sys.argv[1] == '-h':
	usage()
else:
	file_name, nessus = open_nessus_file(sys.argv[1])

##
# Find all the reports in the Nessus file
reports = nessus.findall('Report')

##
# Process each of the reports
for report in reports:
	report_name = report.attrib['name']
	print("Processing report {0}".format(report_name))
	
	# Process each host in the report
	report_hosts = report.findall('ReportHost')
	for host in report_hosts:

		hid, fqdn, os = process_host_properties(host.find('HostProperties'))
		host_items[hid] = HostItem(hid, fqdn, os)
				
		print("Processing host {0}".format(hid))

		# Find and process all of the ReportItems
		report_items = host.findall('ReportItem')
		for item in report_items:
			
			process_port(hid, item.attrib['protocol'], item.attrib['port'])
			plugin = item.attrib['pluginID']
			
			# Process the user accounts identified in plugin 56211
			# 10860 == local users, 10399 == domain users, 56211 == 1ocal
			if plugin == '56211' or plugin == '10860' or plugin == '10399':
				process_users(hid, item.find('plugin_output').text)
				
			# Process MS08-067
			if plugin == '34477':
				process_vulnerability(hid, item)
				
			# Process Open Windows Shares
			if plugin == '42411':
				process_vulnerability(hid, item)

			# Process Open NFS Shares
			if plugin == '11356':
				process_vulnerability(hid, item)

			# Process Anonymous FTP
			if plugin == '10079':
				process_vulnerability(hid, item)

			# Process Apache Tomcat Common Credentials
			if plugin == '34970':
				process_vulnerability(hid, item)

			# Process SNMP Default Community Strings
			if plugin == '10264' or plugin == '41028':
				process_snmp(hid, plugin, item.find('plugin_output').text)
			
			# Process Web Servers
			if plugin == '10107':
				process_web_server(hid, item.attrib['port'])


##
# Print a report summarizing the data
t = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" 
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
<title>Nessus Analyzer Summary</title>
<style>
body {
	margin: 0;
	padding: 0;
	text-align: center;
	font-family: Calibri, Helvetica, sans-serif;
	font-size: 16px;
	background-color: #ffffff;
	color: #1f1f1f;
}

#container {
	margin: 16px auto;
	padding: 0;
	width: 960px;
	text-align: left;
}

#banner {
	margin 0;
	padding 0;
	background-color: #f1f1f1;
	border: 1px solid #1f1f1f;
	text-align: center;
}

#banner h1 {
	font-size: 2.75em;
	line-height: 1.5;
	color: #e40000;
	margin: 0;
	padding: 0;
}

#banner h2 {
	font-size: 1.5em;
	line-height: 1.25;
	margin: 0;
	padding: 0;
	color: #000000;
}

p {
	margin: 0 0 4px 16px;
	padding: 0;
}

h1 {
	margin: 24px 0 0 0;
	padding: 0;
	font-size: 1.5em;
}

h2 {
	margin: 24px 0 0 0;
	padding: 0;
	font-size: 1.25em;
	color: #e40000;
}

h3 {
	margin: 0;
	padding: 0;
	font-size: 1em;
}


table { border-collapse: collapse; }
table, td, th { border: 1px solid #000000; }
th { text-align: center; background-color: #f1f1f1; }
td { padding-left: 4px; }
th#ip { width: 120px; }
th#os { width: 320px; }
th#tcp { width: 520px; }
th#udp { width: 520px; }

</style>
</head>
<body>
<div id="container">
<div id="banner">
<h1>Nessus Analyzer Summary</h1>
"""

t += "<h2>{0}</h2>\n".format(file_name)
t += """</div>
<div id="menu"><ul>
<li><a href="#ports">Port List</a></li>
<li><a href="#Web">Web Servers</a></li>
<li><a href="#Users">User List</a></li>
<li><a href="#Vulns">Vulnerabilities</a></li>
</ul>
</div>"""

if len(host_items) > 0:

	t += "<a name=\"ports\"></a><h1>Port List</h1>\n"
	for hid in sorted(host_items.keys(), key=ip_key):

		t += host_name_html(hid, host_items[hid].fqdn)
	
		if len(host_items[hid].tcp_ports) > 0:
			t += "<h3>Open TCP Ports</h3>\n"
			t += "<p>{0}</p>\n".format(
				", ".join(str(x) for x in host_items[hid].tcp_ports))
		
		if len(host_items[hid].udp_ports) > 0:
			t += "<h3>Open UDP Ports</h3>\n"
			t += "<p>{0}</p>\n".format(
				", ".join(str(x) for x in host_items[hid].udp_ports))


	for hid in sorted(host_items.keys(), key=ip_key):
		t += "<a name=\"Users\"></a><h1>User List</h1>\n"

		if len(host_items[hid].users) > 0:
			t 

			t += "<p>{0}</p>\n".format(
				"<br />\n".join(host_items[hid].users))
		else:
			t += "<p>No User Accounts Identified</p>\n"

	for hid in sorted(host_items.keys(), key=ip_key):
		t += "<a name=\"snmp\"></a><h1>SNMP Community Strings</h1>\n"

		if len(host_items[hid].snmp) > 0:
			t += host_name_html(hid, host_items[hid].fqdn)
			t += "<p>{0}</p>\n".format(
				"<br />\n".join(host_items[hid].snmp))

		if len(host_items[hid].webservers) > 0:
			t += "<h3>Web Servers</h3>\n"
			t += "<p>\n"
			for host, port in host_items[hid].webservers:
				if port == '443' or port == '8443':
					prot = "https://"
				else:
					prot = "http://"
				t += "<a href=\"{0}{1}:{2}\">{0}{1}:{2}</a><br />\n".format(
					prot, host, port)

			t += "</p>\n"

if len(vulns) > 0:
	t += "<h1>Vulnerability List</h1>\n"

	for pid in sorted(vulns.keys()):
		t += "<h2>{0}</h2>\n".format(vulns[pid].name)
		t += "<p>{0}</p>\n".format(vulns[pid].desc)
		t += "<p>{0}</p>\n".format(
			"<br />\n".join(sorted(vulns[pid].hosts, key=ip_key)))

t += "</div>\n</body>\n</html>"

summary_file = file_name + "_summary.html"
print("Saving report to {0}".format(summary_file))
summary = open(summary_file, "w")
summary.write(t)
