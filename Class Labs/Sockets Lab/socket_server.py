from socketserver import socket
import random
import select

HEADERLENGTH = 10

def openFile(fileName):
		try:
			file = open(fileName, 'a')
		except:
			open(fileName, 'x')
			file = open(fileName, 'a')
		return file

def Send_Message(client_socket,message):
	#Sending a message
	message = str(message)

	#step one, encode message using utf-8 (Q3)
	message = message.encode('utf-8')
	#step two, create header to say what the message length is
	message_header = f"{len(message):<{HEADERLENGTH}}".encode('utf-8')

	#step three, send message_header + message (Q4)
	#hint use the .send method
	client_socket.send(message_header + message)

	return

def Receive_Message(client_socket):
	#Collecting a response...

	#Figuring out the lenght of the message
	message_header = client_socket.recv(HEADERLENGTH)

	if not len(message_header):
		return False

	message_length = int(message_header.decode('utf-8').strip())

	#Receive the message using the .recv method and the message_length(Q6)
	message = client_socket.recv(message_length)

	#Decode the message using utf-8 (Q7)
	message = message.decode('utf-8')

	return str(message)


local_address = "192.168.86.44"
local_port = 1337
local_binding = (local_address,local_port)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(local_binding)
server_socket.listen()

while True:

	client_socket, client_address = server_socket.accept()
	print(f'Received message from:{client_address}')
	message = Receive_Message(client_socket)
	print(message)

	try:
		name = message.split(":")[1].strip()

		filename = name + ".txt"

		answer = random.randint(100000,999999)

		file = openFile(filename)

		file.write(f'{answer}\n')

		file.close()

		response = f'Nice to meet you {name}, the answer you seek is {answer}'

	except Exception as error:

		print (error)

		response = f"I can't understand your name as stated: {message}"

	Send_Message(client_socket, response)