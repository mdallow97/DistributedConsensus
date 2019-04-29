# follower.py
import threading
import ctypes
import process
import time
import parse
import socket, pickle

class Follower(threading.Thread):
    def __init__(self, s, cluster_node):

        # Initialize class variables
        self.s              = s
        self.cluster_node   = cluster_node
        self.shouldEnd      = False
        self.candidate_port = 0

        threading.Thread.__init__(self)

    def get_id(self):

        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

    def run(self):

        #MOVE TO NEW FUNCTION, ACCEPTS INCOMING CONNECTIONS
        # Connect to socket
        try:
            self.s.connect((self.cluster_node.leader_IP, self.cluster_node.leader_port))
            self.cluster_node.port = self.s.getsockname()[1]

            print("Follower addr: ", self.cluster_node.IP, "\tport: ", str(self.cluster_node.port))

            # Get the log from the leader when first connecting
            data = self.s.recv(self.cluster_node.BUFFER_SIZE)
            if (data):
                response = pickle.loads(data)

                if response.getCommand() == "log":
                    log = open("log.txt", 'r+')
                    log.truncate(0)
                    log.write(response.getParams()[0])

                    self.commit_index = int(response.getParams()[1])

                    log.close()



            # Threads for receiving user commands and leader messages
            usr_msg_thread  = threading.Thread(target=self.parseConsoleCommand)
            ldr_msg_thread  = threading.Thread(target=self.rcvLeaderMessage)
            candidate_thread = threading.Thread(target=self.acceptConnection)

            usr_msg_thread.start()
            ldr_msg_thread.start()
            candidate_thread.start()

        except:
            print("Follower has ended")



    # Delegates parsing of a user command
    def parseConsoleCommand(self):

        print("Enter command: ")
        while not self.shouldEnd:

            message = input()
            command = parse.parseClientMessage(message)

            if command.getCommand() == "error":
                continue

            # End follower if 'exit' is entered
            elif command.getCommand() == "exit":
                self.shouldEnd = True
                self.s.send(pickle.dumps(command))
                break

            # Send parsed command to leader
            data_bytes = pickle.dumps(command)
            self.s.send(data_bytes)


    # Receive and process leader command
    def rcvLeaderMessage(self):
        while not self.shouldEnd:

            # Receive message
            data = None
            data = self.s.recv(self.cluster_node.BUFFER_SIZE)


            if data:
                response = pickle.loads(data)
                if response.getCommand() == "print":
                    print(response.getParams()[0])

                elif response.getCommand() == "heartbeat":
					# reset timeout

                    self.cluster_node.follower_addrs = response.getParams()[0]
                    self.cluster_node.candidate_ports = response.getParams()[1]
                    self.cluster_node.rcvdHeartbeat = True

                # Requesting the log from this node
                elif response.getCommand() == "LogRequest":
                    returnLog = process.processCommand(response, self.cluster_node)
                    if returnLog != None:
                        self.s.send(pickle.dumps(returnLog))

                elif response.getCommand() == "invalidip":
                    print("Invalid IP")
                    break

                else:
                    process.processCommand(response, self.cluster_node)


    def acceptConnection(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.cluster_node.IP, self.candidate_port))
        self.candidate_port = s.getsockname()[1]

        command = parse.Command("candidatePort", [self.cluster_node.IP, self.cluster_node.port, self.candidate_port])
        self.s.send(pickle.dumps(command))

        s.listen(5)
        conn, addr = s.accept()
        print("Accepted...") # Candidate has successfully contacted this follower


        self.cluster_node.rcvdHeartbeat = True

        while 1:
            data = conn.recv(self.cluster_node.BUFFER_SIZE)

            if data:
                command = pickle.loads(data)

                if command.getCommand() == "RequestVote":
                    conn.send(pickle.dumps(parse.Command("vote")))
                    response = conn.recv(self.cluster_node.BUFFER_SIZE)

                    new_addr = pickle.loads(response)
                    if new_addr.getCommand() == "leaderip":
                        print("NEW LEADER")
                        print("IP: ", self.cluster_node.leader_IP, "\tPORT: ", self.cluster_node.leader_port)

                        self.cluster_node.leader_IP = new_addr.getParams()[0]
                        self.cluster_node.port = new_addr.getParams()[1]

                        self.s.close()
                        self.s.connect((self.cluster_node.leader_IP, self.cluster_node.leader_port))
