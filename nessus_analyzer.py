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

def process_users(hn, text):
	users[hn] = []
	for line in text.split('\n'):
		if re.search(r'\$', line):
			pass
		elif re.match(r'^$', line):
			pass
		else:
			users[hn].append(line)

def process_vulnerability(host, item):
	id = item.attrib['pluginID']
	name = item.attrib['pluginName']
	desc = item.find('description').text
	if id in vulns.keys():
		vulns[id][2].append(host)
	else:
		vulns[id] = [name, desc, [host]]

def process_web_server(host, item):
	port = item.attrib['port']
	if port == '443' or port == '8443':
		webservers.append("https://{0}:{1}".format(host, port))
	else:
		webservers.append("http://{0}:{1}".format(host, port))

#-------------------------#
# Begin the main program. #
#-------------------------#
users = {}
vulns = {}
webservers = []

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
	print("Processing report {0}".format(report.attrib['name']))
	
	# Process each host in the report
	report_hosts = report.findall('ReportHost')
	for host in report_hosts:

		hn = host.attrib['name']
		print("Processing host {0}".format(hn))
		
		# Find and process all of the ReportItems
		report_items = host.findall('ReportItem')
		for item in report_items:
			plugin = item.attrib['pluginID']
			
			# Process the user accounts identified in plugin 56211
			if plugin == '56211' or plugin == '10860':
				process_users(hn, item.find('plugin_output').text)
				
			# Process MS08-067
			if plugin == '34477':
				process_vulnerability(hn, item)
				
			# Process Open Windows Shares
			if plugin == '42411':
				process_vulnerability(hn, item)
			
			# Process Web Servers
			if plugin == '10107':
				process_web_server(hn, item)

##
# Print a report summarizing the data
template = """
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
</style>
</head>
<body>
<div id="container">
<div id="banner">
<h1>Nessus Analyzer Summary</h1>
"""

template += "<h2>{0}</h2>\n".format(file_name)
template += "</div>\n"

if len(users) > 0:
	template += "<h1>User Accounts</h1>\n"
	
	for host in sorted(users.keys()):
		template += "<h2>{0}</h2>\n".format(host)
		template += "<pre>\n"
		for user in users[host]:
			template += "{0}\n".format(user)
		template += "</pre>\n"

if len(vulns) > 0:
	template += "<h1>Selected Vulnerabilities</h1>\n"
		
	for id in sorted(vulns.keys()):
		template += "<h2>{0}</h2>\n".format(vulns[id][0])
		template += "<p>{0}</p>\n".format(vulns[id][1])
		template += "<p><strong>Affected Hosts:</strong></p>\n"
		template += "<pre>\n"
		for host in vulns[id][2]:
			template += "{0}\n".format(host)
		template += "</pre>\n"
		
if len(webservers) > 0:
	template += "<h1>Web Servers</h1>\n"
	
	for server in webservers:
		template += "<p><a href=\"{0}\">{1}</a></p>".format(server, server)
		

template += "</div>\n</body>\n</html>"

summary = open("summary.html", "w")
summary.write(template)
