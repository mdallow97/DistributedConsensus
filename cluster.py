import socket, pickle
import threading
import time
import parse
import leader
import follower

class ClusterNode:

	def __init__(self, IP, port, state, follower_ips):
		# Initialize class variables
		self.IP 			= IP
		self.port			= port
		self.state 			= state
		self.current_term 	= 1
		# self.votedFor 		= null
		self.commit_index 	= 0
		self.current_commit = None
		self.BUFFER_SIZE 	= 1024
		self.followers 		= []
		self.follower_ips	= []
		self.shouldEnd 		= False
		self.rcvdHeartbeat	= False
		self.node_thread	= None

		self.log			= open("log.txt", 'w')
		self.log.truncate(0)
		self.log.close()

		for flr in follower_ips:
			self.follower_ips.append(flr)
		self.follower_ips.append(self.IP)

		# Open socket
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Initialize node type (leader or follower)
		if self.isLeader():
			self.node_thread = leader.Leader(s, self)
			self.rcvdHeartbeat = True
		else:
			self.node_thread = follower.Follower(s, self)

		# Timeout thread
		timer_thread = threading.Thread(target=self.timeoutTimer)
		timer_thread.setDaemon(True)

		self.node_thread.start()
		timer_thread.start()

		timer_thread.join()


	# Broadcast a command to all followers
	def broadcast(self, command):
		for follower in self.followers:
			follower.send(pickle.dumps(command))


	# Returns true if this node is a leader
	def isLeader(self):
		return self.state == "leader"


	# Timer thread function, handles a nodes timeout
	def timeoutTimer(self):
		while not self.shouldEnd:
			time.sleep(self.getTimeout())

			# If the node is a leader, and it timesout
			if self.isLeader():

				# End leader thread
				self.node_thread.end()
				self.node_thread.join()
				self.state = "follower"

				# Prepare new socket, and start follower thread
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.node_thread = follower.Follower(s, self)
				self.node_thread.start()
				continue

			else:

				if self.rcvdHeartbeat:
					self.rcvdHeartbeat = False
					continue

				else:
					# start new election
					self.newElection()


	def newElection(self):
		self.state = "candidate"
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.current_term = self.current_term + 1

		self.node_thread.join()
		self.node_thread = candidate.Candidate(s, self)



	def getTimeout(self):
		if self.isLeader():
			return 10 # 60 #seconds
		elif (self.state == "candidate"):
			return 10 # seconds
		elif (self.state == "follower"):
			return 31
		else:
			print("Invalid state on server with IP ", self.IP)
			exit()
