#Client
#Sources:
	#https://www.geeksforgeeks.org/primitive-root-of-a-prime-number-n-modulo-n/
	#https://en.wikipedia.org/wiki/Diffie%E2%80%93Hellman_key_exchange
	#https://stackoverflow.com/questions/15285534/isprime-function-for-python-language
	#https://asecuritysite.com/encryption/diffie_py
from socketserver import socket
import random
from math import sqrt
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

HEADERLENGTH = 10

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


def genPrime(min, max):
	primes = [i for i in range(min,max) if isPrime(i)]
	p = random.choice(primes)
	return p


  
# Utility function to store prime 
# factors of a number  
def findPrimefactors(s, n) : 
  
    # Print the number of 2s that divide n  
    while (n % 2 == 0) : 
        s.add(2)  
        n = n // 2
  
    # n must be odd at this po. So we can   
    # skip one element (Note i = i +2)  
    for i in range(3, int(sqrt(n)), 2): 
          
        # While i divides n, print i and divide n  
        while (n % i == 0) : 
  
            s.add(i)  
            n = n // i  
          
    # This condition is to handle the case  
    # when n is a prime number greater than 2  
    if (n > 2) : 
        s.add(n)  
  
# Function to find smallest primitive  
# root of n  

def findPrimitive( n) : 
    s = set()  

    # Check if n is prime or not  
    if (isPrime(n) == False):  
        return -1
  
    # Find value of Euler Totient function  
    # of n. Since n is a prime number, the  
    # value of Euler Totient function is n-1  
    # as there are n-1 relatively prime numbers. 
    phi = n - 1
  
    # Find prime factors of phi and store in a set  
    findPrimefactors(s, phi)  
  
    # Check for every number from 2 to phi  
    for r in range(2, phi + 1):  
  
        # Iterate through all prime factors of phi.  
        # and check if we found a power with value 1  
        flag = False
        for it in s:  
  
            # Check if r^((phi)/primefactors) 
            # mod n is 1 or not  
            if (pow(r, phi // it, n) == 1):  
  
                flag = True
                break
              
        # If there was no power with value 1.  
        if (flag == False): 
            return r  
  
    # If no primitive root found  
    return -1

#Used for Diffehellman
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

#Used for all communication after negotiation
def receiveMessageEncryptedCBC(clientSocket, sessionKey, IV):
	messageHeader = decryptMessageCBC(clientSocket.recv(256), sessionKey, IV)
	messageHeader = messageHeader.decode('utf-8')
	messageLength = int(messageHeader.strip())
	message = decryptMessageCBC(clientSocket.recv(messageLength), sessionKey, IV)
	message = message.decode('utf-8')
	message = str(message)
	return message


def sendMessageEncryptedCBC(clientSocket, message, sessionKey, IV):
	message = str(message)
	message = encryptMessageCBC(message.encode('utf-8'), sessionKey, IV)
	messageHeader = encryptMessageCBC(f"{len(message):<{HEADERLENGTH}}".encode('utf-8'), sessionKey, IV)
	clientSocket.send(messageHeader + message)
	return


def decryptMessageCBC(payload, sessionKey, IV):
	secret = sessionKey.encode('utf-8')
	IV = IV.encode('utf-8')
	cipher = AES.new(sessionKey, AES.MODE_CBC, IV)
	data = unpad(cipher.decrypt(payload), 256)
	return data


def encryptMessageCBC(data, sessionKey, IV):
	sessionKey = sessionKey.encode('utf-8')
	IV = IV.encode('utf-8')
	cipher = AES.new(sessionKey, AES.MODE_CBC, IV)
	data = pad(data,256)
	payload = cipher.encrypt(data)
	return payload

#Used for all communication for cryptosessionstart
def receiveMessageEncryptedECB(clientSocket, secret):
	messageHeader = decryptMessageECB(clientSocket.recv(256), secret)
	messageHeader = messageHeader.decode('utf-8')
	messageLength = int(messageHeader.strip())
	message = decryptMessageECB(clientSocket.recv(messageLength), secret)
	message = message.decode('utf-8')
	message = str(message)
	return message


def sendMessageEncryptedECB(clientSocket, message, secret):
	message = str(message)
	message = encryptMessageECB (message.encode('utf-8'), secret)
	messageHeader = encryptMessageECB(f"{len(message):<{HEADERLENGTH}}".encode('utf-8'), secret)
	clientSocket.send(messageHeader + message)
	return

def decryptMessageECB(payload, secret):
	secret = secret.encode('utf-8')
	cipher = AES.new(secret, AES.MODE_ECB)
	data = unpad(cipher.decrypt(payload), 256)
	return data

def encryptMessageECB(data, secret):
	secret = secret.encode('utf-8')
	cipher = AES.new(secret, AES.MODE_ECB)
	data = pad(data,256)
	payload = cipher.encrypt(data)
	return payload


def interpretConfig(file):
	file = open(file, "r")
	serverConfig = file.readlines()
	file.close()
	configDict = {}

	for x in serverConfig:
		try:
			element = x.split(":")
			key = element[0]
			value = element[1]
			configDict[key] = value

		except:
			continue
	return configDict


def diffeHellman(clientSocket):
	min = 100000
	max = 999999
	p = genPrime(min, max)
	g = findPrimitive(p)
	message =  f'{p},{g}'
	
	sendMessage(clientSocket, message)
	a = random.randint(0, 10000)
	A = (g**a) % p 
	
	sendMessage(clientSocket, A)
	B = int(receiveMessage(clientSocket)) 
	s = (B**a) % p
	
	secret = hashlib.sha256(str(s).encode()).hexdigest()
	x = slice(32)
	secret = secret[x]

	try:
		file = open("secret.txt", "w")

	except:
		open("secret.txt", "x")
		file = open("secret.txt", "w")

	file.write(secret)

	file.close()

	return secret


def cryptoSessionStart(clientSocket, secret, N1):
	#N2+N1, N2
	message = receiveMessageEncryptedECB(clientSocket, secret)
	variables = message.split(",")
	serverAuth = int(variables[0])
	N2 = int(variables[1])


	if (serverAuth - N1) != N2:
		return "fail"

	print ("Server Has Been Authed")

	N3 = random.getrandbits(128)
	message = f'{N2+N3},{N3}'
	sendMessageEncryptedECB(clientSocket, message, secret)

	IV = hashlib.sha256(str((N2 * N3)).encode()).hexdigest()
	N2 = hashlib.sha256(str(N2).encode()).hexdigest()
	N3 = hashlib.sha256(str(N2).encode()).hexdigest()
	x = slice(16)
	N2 = N2[x]
	N3 = N3[x]
	
	cryptoVariables = {}
	cryptoVariables["sessionKey"] = N2 + N3
	cryptoVariables["IV"] = IV[x]

	return cryptoVariables
	

def main(log):
	#clientConfig = interpretConfig("/var/Agent/Client/clientConfig.txt")
	#IP = clientConfig[ServerIP]
	#PORT = clientConfig[ServerPort]
	#hostname = clientConfig[Hostname]
	lIP = '192.168.163.130'
	PORTS = []
	PORTS.extend(range(10000, 11000))
	lPort = random.choice(PORTS)
	localAddress = (lIP, lPort, )
	IP = "192.168.163.131"
	PORT = 1337
	hostname = "client1"
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	clientSocket.bind((localAddress))
	clientSocket.connect((IP, PORT))
	N1 = random.getrandbits(128)

	try:
		file = open("/var/Agent/Secure/secret.txt", "r")
		status = "PHASE2"

	except:
		status = "PHASE1"


	message = f'{hostname},{N1},{status}'
	sendMessage(clientSocket, message)

	status = receiveMessage(clientSocket)

	if "PHASE1" in status:
		secret = diffeHellman(clientSocket)
		phase = receiveMessage(clientSocket)
		cryptoVariables = cryptoSessionStart(clientSocket, secret, N1)

	if "PHASE2" in status:
		secret = file.readline()
		cryptoVariables = cryptoSessionStart(clientSocket, secret, N1)

	if "fail" in cryptoVariables:
		print("Failed to authenticate with server")

	sendMessageEncryptedCBC(clientSocket, log, cryptoVariables["sessionKey"], cryptoVariables["IV"])

	print(f'Sent message: {log}')

	clientSocket.close()

main("This is a test")