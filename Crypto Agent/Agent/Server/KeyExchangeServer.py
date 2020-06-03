#Key Exchange Client

from socketserver import socket
import random
import hashlib

HEADERLENGTH = 10

def sendMessage(clientSocket, message):
	message = str(message)
	message = message.encode('utf-8')
	messageHeader = f"{len(message):<{HEADERLENGTH}}".encode('utf-8')
	clientSocket.send(messageHeader + message)
	return

def receiveMessage(clientSocket):
	messageHeader = clientSocket.recv(HEADERLENGTH)
	if not len(messageHeader):
		return False
	messageLength = int(messageHeader.decode('utf-8').strip())
	message = clientSocket.recv(messageLength)
	message = message.decode('utf-8')
	message = str(message)
	return message
 
def isPrime(n):
	if n == 2 or n == 3: return True
	if n < 2 or n%2 == 0: return False
	if n < 9: return True
	if n%3 == 0: return False
	r = int(n**0.5)
	f = 5
	while f <= r:
		if n%f == 0: return False
		if n%(f+2) == 0: return False
		f +=6
	return True

def main(clientSocket):
	message = f'PHASE1'
	sendMessage(clientSocket, message)
	message = receiveMessage(clientSocket)
	diffeVars = message.split(",")
	p = int(diffeVars[0])
	g = int(diffeVars[1])

	try:
		isPrime(p)

	except: 
		print("Invalid Parameters Received!")
	
	b = random.randint(10001, 20001)
	B = (g**b) % p

	sendMessage(clientSocket, B)

	A = int(receiveMessage(clientSocket))

	s = (A**b) % p

	secret = hashlib.sha256(str(s).encode()).hexdigest()
	x = slice(32)
	
	secret = secret[x]

	return secret