#portscanning.py

import socket

LOW_PORT = 22
HIGH_PORT = 80
HOST = ''

portList = range(LOW_PORT, HIGH_PORT+1)
resultDict = {}

for x in portList:
	s = socket.socket()
	s.settimeout(2)

	print (f'Scanning: {x}')

	status = s.connect_ex((HOST, x))

	if(status == 0):
		resultDict[str(x)] = 'open'

	else:
		resultDict[str(x)] = 'closed'

	s.close()

print(resultDict)  






