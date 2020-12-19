import pymongo
import os
import time
import urllib
import paramiko
'''
Dependencies:
pip install pymongo

Config File Map:
host:localhost
port:27017
username:insights
password:(password)
database:insights
collection:jobs
'''

def interpret_config(filename):
	file = open(filename, "r")
	serverConfig = file.readlines()
	file.close()
	configDict = {}
	for x in serverConfig:
		x = x.strip("\n")
		x = x.replace(" ", "")
		try:
			element = x.split(":")
			key = str(element[0])
			value = ":".join(element[1:])
			configDict[key] = value

		except:
			continue
	return configDict



git_commands = ["git fetch --git-dir /home/ansible/ncsiem_deploy/ansible", "git pull --git-dir /home/ansible/ncsiem_deploy/ansible"]
config_dict = interpret_config("/var/insights/worker.conf")

class Mongo:
	def __init__(self, host, port, username, password, database):

		username = urllib.parse.quote_plus(username)
		password = urllib.parse.quote_plus(password)
		self.client = pymongo.MongoClient(f"mongodb://{username}:{password}@{host}:{int(port)}/{database}")
	
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

os.system("git clone git@gitlab.ncsa.tech:systems-team/ansible.git")
os.system("git config --global user.email deploy@ncsa.tech")

class Queue:
	def __init__(self):
		print("Starting Queue")
		self.mongo = Mongo(host = config_dict["host"], port = config_dict["port"], username = config_dict["username"], password = config_dict["password"], database	= config_dict["database"])
		self.mongo.set_db(config_dict["database"])
		self.mongo.set_collection(config_dict["collection"])
		self.todo = self.mongo.collection.find({"job_status":"not started"})

	def finish(self, job):
		self.mongo.update(job["_id"],"job_status","finished") 
		print(f"Finished Job:{job['_id']}")

	def update(self):
		self.todo = self.mongo.collection.find({"job_status":"not started"})
		print (self.todo)
	def categorize(self):
		self.to_remove = []
		self.to_add = {}

		#Queue Actions
		for document in self.todo:
			if "remove" in document["action"]:
				self.to_remove.append(document["hostname"])  
				self.finish(document)


			if "add" in document["action"]: 
				self.to_add[document["hostname"]]= document





queue = Queue()


client = paramiko.client.SSHClient()

client.load_system_host_keys()
k = paramiko.RSAKey.from_private_key_file("/var/insights/ssh.pem")

while True:

	
	queue.categorize()
	original = open("/var/insights/ansible/hosts.ini", "r")
	hosts_file = open("/var/insights/ansible/hosts.ini", "r")
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
	hosts_file = open("/var/insights/ansible/hosts.ini", "w")

	#Adding hosts

	print(queue.to_add)
	for host in queue.to_add:
		document = queue.to_add[host]
		print(f"added {host}")
		if "windows" in document["OS_family"]:
			try:
				groups["[winbeats]"].append(host)
			except:
				groups["[winbeats]"] = []
				groups["[winbeats]"].append(host)

			try:
				groups["[windows]"].append(host)
			except:
				groups["[windows]"] = []
				groups["[windows]"].append(host)
		
		elif "linux" in document["OS_family"]:
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
		
		elif "cisco" in document["OS_family"]:
			try:
				groups["[cisco]"].append(host)
			except:
				groups["[cisco]"] = []
				groups["[cisco]"].append(host)

		else:
			print (f'unknown OS family: {document["OS_family"]}')
	
	queue.finish(document)

	#Writing a .ini
	print(groups)
	for group in groups:

		hosts_file.write(f'{group}\n')

		for host in groups[group]:
			hosts_file.write(f'{host}\n') 

	hosts_file.close()

	new = open("/var/insights/ansible/hosts.ini", "r")
	if new.readlines() not in original.readlines():

		for host in queue.to_add:
			document = queue.to_add[host]
			os.system(f'mkdir /var/insights/ansible/host_vars/{host}')
			open(f'/var/insights/ansible/host_vars/{host}/ncsiem-vars.yml','x')
			host_vars = open('ncsiem-vars.yml','w')
			host_vars.write("#THIS FILE IS MANAGED BY AN EXTERNAL NCSA-INSIGHTS / NCSIEM\n")
			host_vars.write(f'objectType:{document["object_type"]}\n')
            host_vars.write(f'objectId:{document["object_id"]}\n')
            host_vars.write(f'objectVersion:{document["object_version"]}\n')
			host_vars.close()


		os.chdir("/var/insights/ansible")
		os.system("git stage /var/insights/ansible/")
		os.system('git commit -m "updated by insights_worker"')
		os.system('git push')

	elif queue.to_remove:
		os.chdir("/var/insights/ansible	")
		os.system("git stage /var/insights/ansible/")
		os.system('git commit -m "updated by insights_worker"')
		os.system('git push')

	else:
		time.sleep(60)
		queue.update()
		continue

		

	client.connect(hostname ="ansible.ncsa.tech", username = "ansible", pkey = k)
	

	for command in git_commands:
		stdin , stdout, stderr = client.exec_command(command)
		print (stdout.read())
		print("Errors")
		print (stderr.read())




	client.close()

	time.sleep(60)

	queue.update()
