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
		self.users = []
		self.open_shares = []
		self.web_servers = []
		self.snmp = []
		self.tomcat = []

	def name(self):
		if self.fqdn == "":
			return "{0}".format(self.ip)
		else:
			return "{0} ({1})".format(self.ip, self.fqdn)

class Vulnerability():

	def __init__(self, pid, name, desc):
		self.pid = pid
		self.name = name
		self.desc = desc
		self.hosts = []

def usage():
	print("lhf.py nessus_file")
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

##
# Extract usernames from plugin and add to vulnerability
def process_users(hid, item):
	text = item.find('plugin_output').text
	users = []
	for line in text.split('\n'):
		m = re.search(r' - (.*) \((.*)\)$', line)
		if m:
			if re.search(r'\$', m.group(1)):
				continue
			else:
				if re.search(r'id 500', m.group(2)):
					user = "{0} (Administrator)".format(m.group(1))
				else:
					user = m.group(1)

				users.append(user)

	note = ", ".join(users)
	add_vulnerability(hid, item, note)

##
# Extract the shared folder names and add them to the vulnerability note
def process_open_shares(hid, item):
	text = item.find('plugin_output').text
	shares = []
	for line in text.split('\n'):
		m = re.search(r'\+ (.*)$', line)
		if m:
			shares.append(m.group(1))

	note = ", ".join(shares)

	add_vulnerability(hid, item, note)

def process_snmp(hid, item):
	snmp = []
	if plugin == '41028':
		note = 'public'
	else:
		for line in text.split('\n'):
			m = re.search(r' - (.*)$', line)
			if m:
				snmp.append(m.group(1))

		note = ", ".join(snmp)

	add_vulnerability(hid, item, note)

##
# Process Apache Tomcat vulnerability. Extract URL and credentials
def process_apache_tomcat(hid, item):
	text = item.find('plugin_output').text
	u = re.search(r'Username : (.*)', text).group(1)
	p = re.search(r'Password : (.*)', text).group(1)
	url = re.search(r'(http://.*)', text).group(1)

	note = "URL: {0}, User: {1}, Pass: {2}".format(url, u, p)

	add_vulnerability(hid, item, note)
	
def add_vulnerability(hid, item, note=''):
	pid = item.attrib['pluginID']
	name = item.attrib['pluginName']
	desc = item.find('description').text
	
	if pid in vulns.keys():
		vulns[pid].hosts.append((hid, note))
	else:
		vulns[pid] = Vulnerability(pid, name, desc)
		vulns[pid].hosts.append((hid, note))

def process_web_server(hid, port):
	if (hid, port) in host_items[hid].web_servers:
		pass
	else:
		host_items[hid].web_servers.append((hid, port))

def check_metasploit_exploit(hid, item):
	metasploit = ''
	mname = ''
	risk_factor = ''
	
	if not item.find('exploit_framework_metasploit') is None:
		metasploit = item.find('exploit_framework_metasploit').text
		mname = item.find('metasploit_name').text
	
	if not item.find('risk_factor') is None:
		risk_factor = item.find('risk_factor').text

	if metasploit == 'true':
		if not risk_factor == 'None':
			add_vulnerability(hid, item, mname) 


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

		# if hid and fqdn are empty then the host scan did not complete or 
		# some other error has occured. Skip this host.
		if (hid == '') and (fqdn == ''):
			continue

		host_items[hid] = HostItem(hid, fqdn, os)
				
		print("Processing host {0}".format(hid))

		# Find and process all of the ReportItems
		report_items = host.findall('ReportItem')
		for item in report_items:
			process_port(hid, item.attrib['protocol'], item.attrib['port'])
			plugin = item.attrib['pluginID']
			
			# Process user accounts
			# 10860 == local users, 10399 == domain users, 56211 == 1ocal
			if plugin == '56211' or plugin == '10860' or plugin == '10399':
				process_users(hid, item)
				
			# Process MS08-067
			if plugin == '34477':
				add_vulnerability(hid, item)
				
			# Process Open Windows Shares
			if plugin == '42411':
				process_open_shares(hid, item)

			# Process Open NFS Shares
			if plugin == '11356':
				process_open_shares(hid, item)

			# Process Anonymous FTP
			if plugin == '10079':
				add_vulnerability(hid, item)

			# Process Apache Tomcat Common Credentials
			if plugin == '34970':
				process_apache_tomcat(hid, item)

			# Process SNMP Default Community Strings
			if plugin == '10264' or plugin == '41028':
				process_snmp(hid, item)
			
			# Process Web Servers
			if plugin == '10107':
				process_web_server(hid, int(item.attrib['port']))

			if plugin == '22964':
				if item.attrib['svc_name'] == 'www':
					process_web_server(hid, int(item.attrib['port']))

			# Process Vulnerabilities with a Metasploit Exploit module
			check_metasploit_exploit(hid, item)


##
# Print a report summarizing the data
t = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" 
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
<title>Low Hanging Fruit Nessus Summary</title>
<style>
body {
	margin: 0;
	padding: 0;
	text-align: center;
	font-family: Calibri, Helvetica, sans-serif;
	font-size: 12pt;
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

#menu {
	width: 100%;
	float: left;
	background-color: #ffffff;
	margin: 8px 0px;
	border-bottom: 2px solid #1f1f1f;
}

#menu ul{
	margin: 0;
	padding: 0;
} 

#menu ul li {
	list-style-type: none;
	display: inline;
}

#menu a {
	display: block;
	float: left;
	padding: 4px 8px;
	color: #1f1f1f;
	font-size: 1.25em;
	text-decoration: none;
	font-weight: bold;
}

#menu a:active {
	color: #1f1f1f;
}

#menu a:visited {
	color: #1f1f1f;
}

#menu a:hover {
	color: #f40000;
}

p {
	margin: 0 0 4px 0;
	padding: 0;
}

h1 {
	margin: 24px 0 0 0;
	padding: 0;
	font-size: 1.5em;
}

h2 {
	margin: 12px 0 0 0;
	padding: 0;
	font-size: 1.25em;
	color: #e40000;
}

table { border-collapse: collapse; }
table, td, th { border: 1px solid #000000; vertical-align: top;}
th { text-align: center; background-color: #f1f1f1; }
td { padding: 0 4px 0 4px }
th#ip { width: 130px; }
th#os { width: 230px; }
th#tcp { width: 300px; }
th#udp { width: 300px; }
th#notes { width: 830px; }
</style>
</head>
<body>
<div id="container">
<a name="top"></a>
<div id="banner">
<h1>Low Hanging Fruit</h1>
"""

t += "<h2>{0}</h2>\n".format(file_name)
t += """</div>
<div id="menu">
<ul>
<li><a href="#vulns">Vulnerabilities</a></li>
<li><a href="#ports">Port List</a></li>
<li><a href="#web">Web Servers</a></li>
</ul>
</div>"""

if len(host_items) > 0:

	##
	# Print out the list of vulnerabilities
	t += "<a name=\"vulns\"></a><h1>Vulnerabilities</h1>\n"
	t += "<a href=\"#top\">(Back to Top)</a>\n"
	if len(vulns) > 0:
		for pid in sorted(vulns.keys()):
			t += "<h2>{0}</h2>\n".format(vulns[pid].name)
			t += "<p>{0}</p>\n".format(vulns[pid].desc)
			t += "<p><table>\n"
			t += "<tr><th id=\"ip\">IP Address</th>"
			t += "<th id=\"notes\">Notes</th></tr>\n"
			for host, note in sorted(vulns[pid].hosts, key=lambda x: ip_key(x[0])):
				t += "<tr><td>{0}</td>".format(host)
				t += "<td>{0}</td></tr>\n".format(note)
			t += "</table></p>\n"

	##
	# Print out the port list
	t += "<a name=\"ports\"></a><h1>Port List</h1>\n"
	t += "<a href=\"#top\">(Back to Top)</a>\n"
	t += "<table>"
	t += "<tr><th id=\"ip\">IP Address</th><th id=\"os\">Operating System</th>"
	t += "<th id=\"tcp\">Open TCP Ports</th><th id=\"udp\">Open UDP Ports</th></tr>\n"
	for hid in sorted(host_items.keys(), key=ip_key):
		if len(host_items[hid].tcp_ports) == 0 and len(host_items[hid].udp_ports) == 0:
			continue

		t += "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>\n".format(
			host_items[hid].ip,
			host_items[hid].os,
			", ".join(str(x) for x in host_items[hid].tcp_ports),
			", ".join(str(x) for x in host_items[hid].udp_ports))
	
	t += "</table>"

	##
	# Print out the web server list
	t += "<a name=\"web\"></a><h1>Web Servers</h1>\n"
	t += "<a href=\"#top\">(Back to Top)</a>\n"
	t += "<p>\n"
	for hid in sorted(host_items.keys(), key=ip_key):

		if len(host_items[hid].web_servers) > 0:
			for host, port in sorted(host_items[hid].web_servers):
				if port == 443 or port == 8443:
					prot = "https://"
				else:
					prot = "http://"
				t += "<a href=\"{0}{1}:{2}\">{0}{1}:{2}</a><br />\n".format(
					prot, host, str(port))

	t += "</p>\n"


t += "</div>\n</body>\n</html>"

summary_file = file_name + "_summary.html"
print("Saving report to {0}".format(summary_file))
summary = open(summary_file, "w")
summary.write(t)
