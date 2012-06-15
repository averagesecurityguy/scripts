#!/usr/bin/env python
#-----------------------------------------------------------------------------
# 
#-----------------------------------------------------------------------------

import xml.etree.ElementTree
import sys
import re
import os.path

def usage():
	print("nessus-analyzer.py nessus_file")
	sys.exit()
	
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

def process_host_info(hn, properties):

	hid = ''
	ip, os = process_host_properties(properties)

	if not ip == '':
		hid = ip
	else:
		hid = hn

	return hid, os

def process_host_properties(host_properties):
	ip = ''
	os = 'Unknown'
	for tag in host_properties.findall('tag'):
		if tag.attrib['name'] == 'host-ip':
			ip = tag.text
		if tag.attrib['name'] == 'operating-system':
			os = tag.text

	return ip, os

def process_users(hid, text):
	users[hid] = []

	for line in text.split('\n'):
		m = re.search(r' - (.*)$', line)
		if m:
			if re.search(r'\$', m.group(1)):
				pass
			else:
				if not (m.group(1) in users[hid]):
					users[hid].append(m.group(1))

def process_snmp(hid, plugin, text):
	snmp[hid] = []

	if plugin == '41028' and not ('public' in snmp[hid]):
		snmp[hid].append('public')

	for line in text.split('\n'):
		m = re.search(r' - (.*)$', line)
		if m:
			if not (m.group(1) in snmp[hid]):
				snmp[hid].append(m.group(1))

def process_vulnerability(hid, item):
	pid = item.attrib['pluginID']
	name = item.attrib['pluginName']
	desc = item.find('description').text
	if pid in vulns.keys():
		vulns[pid][2].append(hid)
	else:
		vulns[pid] = [name, desc, [hid]]

def process_web_server(hid, item):
	port = item.attrib['port']
	if port == '443' or port == '8443':
		webservers.append("https://{0}:{1}".format(hid, port))
	else:
		webservers.append("http://{0}:{1}".format(hid, port))


#-------------------------#
# Begin the main program. #
#-------------------------#
users = {}
vulns = {}
webservers = []
hosts = {}
ports = {}
snmp = {}

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

		hid, os = process_host_info(host.attrib['name'], host.find('HostProperties'))
				
		print("Processing host {0}".format(hid))

		hosts[hid] = os
		tcp = {}
		udp = {}
		
		# Find and process all of the ReportItems
		report_items = host.findall('ReportItem')
		for item in report_items:

			if item.attrib['protocol'] == 'tcp' and item.attrib['port'] != '0':
				tcp[item.attrib['port']] = 1
			if item.attrib['protocol'] == 'udp' and item.attrib['port'] != '0':
				udp[item.attrib['port']] = 1

			plugin = item.attrib['pluginID']
			
			# Process the user accounts identified in plugin 56211
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
				process_web_server(hid, item)

		ports[hid] = [sorted(tcp.keys()), sorted(udp.keys())]

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
}

pre {
	margin: 0;
	padding: 0;
	font-size: .9em;
}

p {
	margin: 0 0 4px 0;
	padding: 0;
}

p#mono {
	font-family: Courier New, monospace;
	font-size: .75em;
}

h2 {
	margin: 8px 0 0 0;
	padding: 0;
	font-size: 1em
}

h1 {
	margin: 24px 0 0 0;
	padding: 0;
	font-size: 1.75em;
}


table { border-collapse: collapse; }
table, td, th { border: 1px solid #000000; }
th { text-align: center; background-color: #f1f1f1; }
td { padding-left: 4px; }
th#ip { width: 100px; }
th#os { width: 320px; }
th#tcp { width: 540px; }
th#udp { width: 540px; }

</style>
</head>
<body>
<div id="container">
<div id="banner">
<h1>Nessus Analyzer Summary</h1>
"""

t += "<h2>{0}</h2>\n".format(file_name)
t += "</div>\n"

if len(ports) > 0:
	t += "<h1>Open TCP Ports</h1>\n"
	t += "<table>\n"
	t += "<tr><th id=\"ip\">IP</th><th id=\"os\">OS</th>"
	t += "<th id=\"tcp\">TCP ports</th></tr>\n"

	for hid in sorted(ports.keys()):
		if len(ports[hid][0]) > 0:
			t += "<tr><td>{0}</td>".format(hid)
			t += "<td>{0}</td>".format(hosts[hid])
			t += "<td>{0}</td></tr>\n".format(", ".join(ports[hid][0]))

	t += "</table>\n"

if len(ports) > 0:
	t += "<h1>Open UDP Ports</h1>\n"
	t += "<table>\n"
	t += "<tr><th id=\"ip\">IP</th><th id=\"os\">OS</th>"
	t += "<th id=\"udp\">UDP Ports</th></tr>\n"

	for hid in sorted(ports.keys()):
		if len(ports[hid][1]) > 0:
			t += "<tr><td>{0}</td>".format(hid)
			t += "<td>{0}</td>".format(hosts[hid])
			t += "<td>{0}</td></tr>\n".format(", ".join(ports[hid][1]))

	t += "</table>\n"

if len(users) > 0:
	t += "<h1>User Accounts</h1>\n"
	
	for hid in sorted(users.keys()):
		t += "<h2>{0}</h2>\n".format(hid)
		t += "<p>\n"
		for user in users[hid]:
			t += "{0}<br />\n".format(user)
		t += "</p>\n"

if len(snmp) > 0:
	t += "<h1>SNMP Community Strings</h1>\n"
	
	for hid in sorted(snmp.keys()):
		t += "<h2>{0}</h2>\n".format(hid)
		t += "<p>\n"
		for txt in snmp[hid]:
			t += "{0}<br />\n".format(txt)
		t += "</p>\n"

if len(vulns) > 0:
	t += "<h1>Selected Vulnerabilities</h1>\n"
		
	for id in sorted(vulns.keys()):
		t += "<h2>{0}</h2>\n".format(vulns[id][0])
		t += "<p>{0}</p>\n".format(vulns[id][1])
		t += "<p><strong>Affected Hosts:</strong></p>\n"
		t += "<p>\n"
		for host in vulns[id][2]:
			t += "{0}\n".format(host)
		t += "</p>\n"
		
if len(webservers) > 0:
	t += "<h1>Web Servers</h1>\n"
	
	for server in webservers:
		t += "<p><a href=\"{0}\">{1}</a></p>".format(server, server)
		

t += "</div>\n</body>\n</html>"

summary_file = file_name + "_summary.html"
print("Saving report to {0}".format(summary_file))
summary = open(summary_file, "w")
summary.write(t)
