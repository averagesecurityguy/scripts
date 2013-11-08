Scripts
=======

Introduction
------------
This is a collection of scripts I have written to use in pentests. Let me know if there are any problems with the scripts. If you have any suggestions for new scripts let me know as well; I am always looking for new ideas.

Scripts
-------
* `bypass.c` - A c++ program that attempts to download a payload and execute it. I haven't been able to make the execution work properly yet. I would appreciate anyone that wants to tell me what I have done wrong.
* `bypass.exe` - Compiled version of bypass.c
* `cfneo.rb` - Ruby script to exploit a directory traversal flaw in ColdFusion and download the neo-datasource.xml file. It will also decrypt any passwords found in the neo-datasource.xml file and write them to stdout
* `cfpwn.rb` - Ruby script to exploit a directory traversal flaw in ColdFusion to get the admin password hash and salt and then log into the server and get an admin authentication cookie. This cookie can be manually added to Firefox to gain admin access to the ColdFusion server.
* `firewarebf.py` - Python script to conduct a bruteforce password attack on fireware firewalls.
* `gpx_view.rb` - Ruby script to parse an inSSIDer gpx file and output the identified wireless access points. It uses the rextable.rb script which provides nice table output.
* `ishell.py` - Python script to provide an interactive shell. It can be run as a python script or compiled to an executable and run.
* `ishell.exe` - Compiled version of ishell.py. Compiled with PyInstaller.
* `lhf.py` - Analyze a Nessus v2 XML file for easily exploitable vulnerabilities.
* `nessus_analyzer.py` - Python script to read a Nessus v2 file and extract data useful for a penetration tester. This is not meant to be a full functioning Nessus parser.
* `passfilter.py` - Python script that reads a wordlist and outputs words that match certain length and complexity requirements.
* `rextable.rb` - Text table module from the metasploit REX library. I pulled it out as a separate module to be used more easily in small scripts.
* `set_index.html` - Custom index.html file to be used with SET credential harvester attack when victim doesn't have a login form.
* `setmail.rb` - Ruby script to provide an open mail relay to be used with the Social Engineering Toolkit (set). I didn't want to install sendmail and I didnt' want to use gmail.
* `setmail.py` - Python port of setmail.rb. Depends on dnspython library.
* `shell.py` - Python shell (non interactive).
* `ssh_pwn.py` - Python script to exploit unprotected SSH private keys and harvest data from the exploited machine. 
* `ssh_super_virus.py` - Python script to test logins with SSH keys.
* `texttable.py` - Python module for creating text tables.
* `weak_passwords.py` - Pythons script to generate a user pass file. By default it will create password combinations from common passwords. You can also give it a list of words or a word file and it will create password combinations from that list as well.
