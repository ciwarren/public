import pymongo
import os
import time
import urllib
'''
Dependencies:
pip3 install pymongo

Config File Map:
host:localhost
port:27017
username:insights
password:(password)
database:insights
collection:jobs
'''

def interpretConfig(filename):
	file = open(filename, "r")
	serverConfig = file.readlines()
	file.close()
	configDict = {}
	for x in serverConfig:
		x = x.strip("\n")
		try:
			element = x.split(":")
			key = str(element[0])
			value = element[1]
			configDict[key] = value

		except:
			continue
	return configDict



config_dict = interpretConfig("/var/insights/worker.conf")
class Mongo:
	def __init__(self, host, port, username, password):

		username = urllib.parse.quote_plus(username)
		password = urllib.parse.quote_plus(password)
		self.client = pymongo.MongoClient(f"mongodb://{username}:{password}@{host}:{int(port)}/")
		self.client = pymongo.MongoClient(f"mongodb://{host}:{int(port)}/")
		self.databases = self.client.list_database_names()

	def set_db(self, db):
		if db in self.databases:
			print("Database Found!")
			self.db = self.client[db]
		else:
			print("Database Created!")
			self.db = self.client[db]

	def set_collection(self, collection):
		self.collections = self.db.list_collection_names()
		if collection in self.collections:
			print("Collection Found!")
			self.collection = self.db[collection]
		else:
			print("Collection Created!")
			self.collection = self.db[collection]

	def update(self, id, attr, value):
		query = {"_id": id}
		newvalue = {"$set":{attr:value}}
		self.collection.update_one(query,newvalue)
			
class Queue:
	def __init__(self):
		print("Starting Queue")
		self.mongo = Mongo(host = config_dict["host"], port = config_dict["port"], username = config_dict["username"], password = config_dict["password"])
		self.mongo.set_db(config_dict["database"])
		self.mongo.set_collection(config_dict["collection"])
		self.todo = self.mongo.collection.find({"job_status":"not started"})

	def finish(self, job):
		self.mongo.update(job["_id"],"job_status","finished") 
		print(f"Finished Job:{job['_id']}")

	def update(self):
		self.todo = mongo.collection.find({"job_status":"not started"})
		print (self.todo)
	def categorize(self):
		self.to_remove = []
		self.to_add = {}

		#Queue Actions
		for x in self.todo:
			print(x)
			if "remove" in x["action"]:
				self.to_remove.append(x["hostname"])  


			if "add" in x["action"]: 
				self.to_add[x["hostname"]]= x["OS_family"]

			self.finish(x)

queue = Queue()

while True:

	
	queue.categorize()
	original = open("/var/ansible/hosts.ini", "r")
	hosts_file = open("/var/ansible/hosts.ini", "r")
	groups = {}

	#Read and Group
	for line in hosts_file:
		line = line.strip("\n")
		if "[" in line:
			groups[line] = []
			current_group = line
		else:
			if line in queue.to_remove:
				print(f"removed {line}")
			else:
				groups[current_group].append(line)

	hosts_file.close()
	hosts_file = open("/var/ansible/hosts.ini", "w")

	#Adding hosts

	print(queue.to_add)
	for host in queue.to_add:
		OS = queue.to_add[host]
		if "windows" in OS:
			try:
				groups["[winbeats]"].append(host)
			except:
				groups["[winbeats]"] = []
				groups["[winbeats]"].append(host)

			try:
				groups["[windows]"].append(host)
			except:
				groups["[windows"] = []
				groups["[windows]"].append(host)
		
		if "linux" in OS:
			try:
				groups["[filebeats]"].append(host)
			except:
				groups["[filebeats]"] = []
				groups["[filebeats]"].append(host)

			try:
				groups["[linux]"].append(host)
			except:
				groups["[linux]"] = []
				groups["[linux]"].append(host)
		
		if "cisco" in OS:
			try:
				groups["[cisco]"].append(host)
			except:
				groups["[cisco]"] = []
				groups["[cisco]"].append(host)

		else:
			print (f'unknown OS family: {OS}')

	#Writing a .ini
	print(groups)
	for group in groups:

		hosts_file.write(f'{group}\n')

		for host in groups[group]:
			hosts_file.write(f'{host}\n') 

	

	hosts_file.close()

	new = open("/var/ansible/hosts.ini", "r")
	if new.readlines() not in original.readlines():
		os.system("git stage /var/insights/hosts.ini")
		os.system('git commit -m "updated by insights_worker"')
		os.system('git push')
	
	time.sleep(60)

	queue.update()








