# follower.py
import threading
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

        threading.Thread.__init__(self)

    def end(self):
        self.shouldEnd = True

    def run(self):
        # Connect to socket
        self.s.connect((self.cluster_node.IP, self.cluster_node.port))
        print("Follower addr: ", self.cluster_node.IP, "\tport: ", str(self.cluster_node.port))

        # Get the log from the leader when first connecting
        data = self.s.recv(self.cluster_node.BUFFER_SIZE)
        if (data):
            response = pickle.loads(data)

            if response.getCommand() == "log":
                log = open("log.txt", 'r+')
                log.truncate(0)
                log.write(response.getParams()[0])
                log.close()



        # Threads for receiving user commands and leader messages
        usr_msg_thread  = threading.Thread(target=self.parseConsoleCommand)
        ldr_msg_thread  = threading.Thread(target=self.rcvLeaderMessage)

        usr_msg_thread.start()
        ldr_msg_thread.start()

        usr_msg_thread.join()
        ldr_msg_thread.join()


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


            if (data):
                response = pickle.loads(data)

                if response.getCommand() == "print":
                    print(response.getParams()[0])

                elif response.getCommand() == "heartbeat":
					# reset timeout
                    # for follower in response.getParams():

                    self.cluster_node.follower_ips = response.getParams()
                    self.cluster_node.rcvdHeartbeat = True

                # Requesting the log from this node
                elif response.getCommand() == "LogRequest":
                    returnLog = process.processCommand(response, self.cluster_node)
                    if returnLog != None:
                        self.s.send(pickle.dumps(returnLog))

                else:
                    process.processCommand(response, self.cluster_node)
