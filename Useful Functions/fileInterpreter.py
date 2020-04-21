#Dictonary File Interpreter
#Part of a project I am working on to develop a SIEM, most of it will be open source, figured someone might find this useful.

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