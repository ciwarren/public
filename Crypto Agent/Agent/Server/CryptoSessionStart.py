#Crypto Session Start


from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
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


def main(socket, secret, N1):
	cryptoVariables = {}
	message = f'PHASE2'
	sendMessage(socket, message)
	N2 = random.getrandbits(128)
	message = f'{N2+N1},{N2}'
	sendMessageEncryptedECB(socket, message, secret)

	#N2+N3, N3
	message = receiveMessageEncryptedECB(socket, secret)
	variables = message.split(",")
	clientAuth = int(variables[0])
	N3 = int(variables[1])

	if (clientAuth - N2) != N3:
		return "abort connection"
	print ("Client Has Been Authed")
	IV = hashlib.sha256(str((N2 * N3)).encode()).hexdigest()
	N2 = hashlib.sha256(str(N2).encode()).hexdigest()
	N3 = hashlib.sha256(str(N2).encode()).hexdigest()
	x = slice(16)
	N2 = N2[x]
	N3 = N3[x]

	cryptoVariables["sessionKey"] = N2 + N3
	cryptoVariables["IV"] = IV[x]

	return cryptoVariables