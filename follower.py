# follower.py
import threading
import process
import time
import parse
import socket, pickle

class Follower(threading.Thread):
    def __init__(self, s, cluster_node):
        self.s              = s
        self.cluster_node   = cluster_node
        self.shouldEnd      = False

        threading.Thread.__init__(self)

    def end(self):
        self.shouldEnd = True

    def run(self):
        self.s.connect((self.cluster_node.IP, self.cluster_node.port))
        print("Follower addr: ", self.cluster_node.IP, "\tport: ", str(self.cluster_node.port))
        print("Enter command: ")

        get_msg_thread  = threading.Thread(target=self.parse)
        rcv_msg_thread  = threading.Thread(target=self.receiveMessage)

        get_msg_thread.start()
        rcv_msg_thread.start()

        rcv_msg_thread.join()
        get_msg_thread.join()


    #used by follower
    def parse(self):
        while 1:
            if self.shouldEnd:
                break

            message = input()

            command = parse.parseClientMessage(message)

            if command.getCommand() == "error":
                continue

            elif command.getCommand() == "exit":
                self.shouldEnd = True
                self.s.send(pickle.dumps(command))
                break

            data_bytes = pickle.dumps(command)
            self.s.send(data_bytes)

    # used by follower
    def receiveMessage(self):
        while not self.shouldEnd:
            data = None
            data = self.s.recv(self.cluster_node.BUFFER_SIZE)


            if (data):
                response = pickle.loads(data)

                if response.getCommand() == "print":
                    print(response.getParams()[0])

                elif response.getCommand() == "heartbeat":
					# reset timeout
                    for follower in response.getParams():
                        self.cluster_node.follower_ips.append(follower)

                        self.cluster_node.rcvdHeartbeat = True
                else:
                    process.processCommand(response, self.cluster_node)
