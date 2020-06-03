#Main Connection Handler
from socketserver import socket
import select
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import KeyExchangeServer
import CryptoSessionStart

#Need to import database.py, KeyExchangeServer.py, CryptoSessionStart.py
HEADERLENGTH = 10

sessionKeys = {}
IVs = {}

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



#Used for all conversation pre CryptoSessionStart
def receiveMessage(clientSocket):
	messageHeader = clientSocket.recv(HEADERLENGTH)
	if not len(messageHeader):
		return False
	messageLength = int(messageHeader.decode('utf-8').strip())
	message = clientSocket.recv(messageLength)
	message = message.decode('utf-8')
	message = str(message)
	return message

def sendMessage(clientSocket, message):
	message = str(message)
	message = message.encode('utf-8')
	messageHeader = f"{len(message):<{HEADERLENGTH}}".encode('utf-8')
	clientSocket.send(messageHeader + message)
	return


#Used for all conversation post CryptoSessionStart
def receiveMessageEncrypted(clientSocket, source):
	IV = IVs[source]
	sessionKey = sessionKeys[source]
	messageHeader = decryptMessage(clientSocket.recv(256), sessionKey, IV)
	messageHeader = messageHeader.decode('utf-8')
	messageLength = int(messageHeader.strip())
	message = decryptMessage(clientSocket.recv(messageLength), sessionKey, IV)
	message = message.decode('utf-8')
	message = str(message)
	return message

#Used for all conversation post CryptoSessionStart
def sendMessageEncrypted(clientSocket, message, source):
	IV = IVs[source]
	sessionKey = sessionKeys[source]
	message = str(message)
	message = encryptMessage(message.encode('utf-8'), sessionKey, IV)
	messageHeader = encryptMessage(f"{len(message):<{HEADERLENGTH}}".encode('utf-8'), sessionKey, IV)
	clientSocket.send(messageHeader + message)
	return

def decryptMessage(payload, sessionKey, IV):
	sessionKey = sessionKey.encode('utf-8')
	IV = IV.encode('utf-8')
	cipher = AES.new(sessionKey, AES.MODE_CBC, IV)
	data = unpad(cipher.decrypt(payload), 256)
	return data

def encryptMessage(data, sessionKey, IV):
	sessionKey = sessionKey.encode('utf-8')
	IV = IV.encode('utf-8')
	cipher = AES.new(sessionKey, AES.MODE_CBC, IV)
	data = pad(data,256)
	payload = cipher.encrypt(data)
	return payload


def main():

	#serverConfig = interpretConfig("/var/Agent/Server/serverConfig.txt")
	#lIP = serverConfig[ServerIP]
	#lPort = serverConfig[ServerPort]
	lIP = "192.168.163.131"
	lPort = 1337
	localAddress = (lIP,lPort, )
	serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	serverSocket.bind((localAddress))
	serverSocket.listen()
	sockets_list = [serverSocket]
	clients = {}
	#secrets = database.secretTable()
	secrets = {}
	print ("\n")



	while True:

		read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
		for notified_socket in read_sockets:
			# If notified socket is a server socket - new connection, accept it
			if notified_socket == serverSocket:
				clientSocket, clientAddress = serverSocket.accept()
                #First message format is (Hostname, N1)
				message = receiveMessage(clientSocket)
				variables = message.split(",")
				source = variables[0]
                #N1 is used for CryptoSessionStart
				N1 = int(variables[1])
				status = variables[2]
				if source in secrets and "PHASE2" in status:
             		#If a long-term secret exists in the database
					sockets_list.append(clientSocket)
					clients[clientSocket] = source
					print('Accepted new connection from {}:{}, source: {}'.format(*clientAddress, source))
	                #Retrieve secret
					sourceSecret = secrets[source]
	                #Generate session key and n2, n3 for source
					cryptoVariables = CryptoSessionStart.main(clientSocket, sourceSecret, N1)
					sessionKeys[source] = cryptoVariables["sessionKey"]
					IVs[source] = cryptoVariables["IV"]
	                 
				else:
	        		#If no long-term secret exists, create one
					sourceSecret = KeyExchangeServer.main(clientSocket)
	            	#Enter secret in database for next restart
					#database.createEntry(table = sources, source = source, secret = sourceSecret)
	            	#Update current dictonary
					secrets[source] = sourceSecret
					sockets_list.append(clientSocket)
					clients[clientSocket] = source
					print('Accepted new connection from {}:{}, source: {}'.format(*clientAddress, source))
					cryptoVariables = CryptoSessionStart.main(clientSocket, sourceSecret, N1)
					if  "abort connection" in cryptoVariables:
						print ("Connection Aborted")
						return
					sessionKeys[source] = cryptoVariables["sessionKey"]
					IVs[source] = cryptoVariables["IV"]

					print(f'sessionKey: {sessionKeys[source]}, IV: {IVs[source]}')





			else:
             	# Get source by notified socket, so we will know who sent the message
				source = clients[notified_socket]
				message = receiveMessageEncrypted(notified_socket, source)

				if message is False:
					print('Closed connection from: {}'.format(clients[notified_socket]))

                    # Remove from list for socket.socket()
					sockets_list.remove(notified_socket)

                    # Remove from our list of users
					del clients[notified_socket]

					continue

                
				print(f'Received message from {source}: {message}\n')



                #database.formatLog(source = source, logData = message)

				sockets_list.remove(notified_socket)
				del clients[notified_socket]



		for notified_socket in exception_sockets:


            # Remove from list for socket.socket()
			sockets_list.remove(notified_socket)

            # Remove from our list of users
			del clients[notified_socket]

main()