from socketserver import socket
import random

#Assign a message header length
HEADERLENGTH = 10

#Assign a local address
local_address = "192.168.86.42"

#Assign a random local port
PORTS = []
#Create a random list of ports(Q1)
#put your code here!
local_port= random.choice(PORTS)

#Assign variables remote_address and remote_port per the lab instructions (Q2)
#put your code here!

#Create bindable tuple
local_bindings = (local_address,local_port)
remote_bindings = (remote_address,remote_port)

#Create socket instance
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Bind to local address and port
client_socket.bind(local_bindings)

#Connect to server
client_socket.connect(remote_bindings)



def Send_Message(client_socket,message):
	#Sending a message
	message = str(message)

	#step one, encode message using utf-8 (Q3)
	#put your code here!

	#step two, create header to say what the message length is
	message_header = f"{len(message):<{HEADERLENGTH}}".encode('utf-8')

	#step three, send message_header + message (Q4)
	#hint use the .send method
	#put your code here!

	return


#Create your message variable, send "Hello, my name is:...", but actually put your name in :) (Q5)
#put your code here!

#This is the actual function call that will use the function written above.
Send_Message(client_socket,message)



def Receive_Message(client_socket):
	#Collecting a response...

	#Figuring out the lenght of the message
	message_header = client_socket.recv(HEADERLENGTH)

	if not len(message_header):
		return False

	message_length = int(message_header.decode('utf-8').strip())

	#Receive the message using the .recv method and the message_length(Q6)
	#put your code here!

	#Decode the message using utf-8 (Q7)
	#put your code here!

	return str(message)

#This is the function call that will use the function written above.
message = Receive_Message(client_socket)

print(message)

client_socket.close()
