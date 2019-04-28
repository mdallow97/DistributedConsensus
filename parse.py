# parse.py

# This class is passed back and forth from followers to leader.
# It simplifies parsing and receiving the commands
class Command:
	def __init__(self, command, params=[], returns_val=False):
		self.command = command
		self.params = params
		self.returns_val = returns_val

	def getParams(self):
		return self.params

	def getCommand(self):
		return self.command

	def shouldReturnVal(self):
		return self.returns_val

	def addParam(self, param):
		self.params.append(param)

	def toString(self):
		str = self.command + "("
		for param in self.params:
			str = str + param + " "

		str = str + ')'

		return str

def printErrorMessage(command):
	print("Invalid command: ", command)
	print("\nAvailable commands:")
	print("ClientCommit(!<var>)\nClientCommit(<var>, <value>)")
	print("dumpLog(<id>)")
	print("exit()\n")

def parseClientMessage(message):

	if len(message) == 0:
		return Command("error")

	# Parse command
	command = ""
	for i in range(0, len(message)):
		if message[i] == '(':
			break
		else:
			command = command + message[i]

	if not message[i] == '(':
		printErrorMessage(command)
		return Command("error")

	param = ""
	params = []
	returns_val = False


	# Parse parameters
	while i < len(message)-1:
		i = i+1
		if message[i] == '!':
			returns_val = True
			continue

		elif message[i] == ' ' and message[i-1] == ',':
			continue

		elif message[i] == ',':
			nextParam = True
			params.append(param)
			param = ""
			continue

		elif message[i] == ')':
			params.append(param)
			param = ""
			break

		param = param + message[i]

	# CHECK PARAMETERS
	if command == "ClientCommit":
		# Command will have only one or two parameters
		# ClienCommit(!<var>) or ClientCommit(<var>, <value>)

		if len(params) != 1 and len(params) != 2:
			printErrorMessage(command)
			return Command("error")

		if len(params) == 1 and not returns_val:
			printErrorMessage(command)
			return Command("error")

	elif command == "dumpLog":
		#dumpLog(<id>)
		if len(params) != 1:
			printErrorMessage(command)
			return Command("error")

		num_periods = 0
		for c in params[0]:
			if c == '.':
				num_periods += 1

		if num_periods != 3:
			print("dumpLog: Invalid IP address")
			return Command("error")


	elif command == "exit":
		return Command(command)
	else:
		printErrorMessage(command)
		return Command("error")

	return Command(command, params, returns_val)
