# leader.py
import threading
import process
import parse
import socket, pickle
from time import sleep

class Leader(threading.Thread):
    def __init__(self, s, cluster_node):

        # Initialize class variables
        self.s = s
        self.cluster_node = cluster_node
        self.shouldEnd = False
        self.client_threads = []

        threading.Thread.__init__(self)


    def end(self):
        self.shouldEnd = True

    # This thread is responsible for handling new clients and broadcasting the heartbeat
    def run(self):

        # Heartbeat thread handles broadcasting the heartbeat to all followers
        heartbeat_thread 	= threading.Thread(target=self.heartbeatTimer)
        heartbeat_thread.start()

        # Initialize incoming TCP connections
        self.s.bind((self.cluster_node.leader_IP, self.cluster_node.leader_port))

        self.cluster_node.port = self.s.getsockname()[1]
        self.leader_port = self.cluster_node.port

        self.s.listen(5) # number of connections to server

        print("Connection IP address: ", self.cluster_node.leader_IP)
        print("Connection opened on port: ", self.s.getsockname()[1])

        # Handles new connections until it should end
        while not self.shouldEnd:
            # Accept connection
            conn, addr = self.s.accept()
            print("Connection from address:", addr)


            isFollowerIP = False
            for ip in self.cluster_node.follower_ips:
                if ip == addr[0]:
                    isFollowerIP = True
                    break

            # Follower info replication
            if isFollowerIP:
                self.cluster_node.follower_addrs.append(addr)
            else:
                print("Invalid IP")
                conn.send(pickle.dumps(parse.Command("invalidip")))
                break

            # Log replication for new followers
            log = open("log.txt", 'r')
            contents = ""
            for line in log:
                contents += line
            log.close()

            conn.send(pickle.dumps(parse.Command("log", [contents, str(self.cluster_node.commit_index)])))

            # Append new follower to followers
            self.cluster_node.followers.append(conn)

            # Handles adding clients and receiving messages
            add_client_thread = threading.Thread(target=self.receiveFromClient, args=(conn, addr))
            self.client_threads.append(add_client_thread)
            add_client_thread.start()

        heartbeat_thread.join()
        for thread in self.client_threads:
            thread.join()


        conn.close()
        print("Connection closed")


    def receiveFromClient(self, conn, addr):
        threading.Thread(target=self.quitThread, args=(conn,)).start()

        while not self.shouldEnd:
            # Get command from follower/client
            command = parse.Command(None, None, None)
            try:
                data = conn.recv(self.cluster_node.BUFFER_SIZE)
                if not data: continue

                command = pickle.loads(data)
            except:
                break

            # Returns something to be printed on both leader and followers
            ret_cmd = process.processCommand(command, self.cluster_node, addr)

            if ret_cmd:
                print(ret_cmd.getParams()[0])
                conn.send(pickle.dumps(ret_cmd))

            # Once leader has finished the operation, all followers must do the same (as long as it is not a retrieval)
            if not command.shouldReturnVal():
                self.cluster_node.broadcast(command)

        conn.close()
        self.cluster_node.followers.remove(conn)


    # Constantly checking to see if the leader thread should end
    def quitThread(self, conn):
        while 1:
            if self.shouldEnd:
                conn.close()


    # Sends out heartbeat to all followers
    def heartbeatTimer(self):
        heartbeat_cmd = parse.Command("heartbeat", [self.cluster_node.follower_addrs, self.cluster_node.candidate_ports])
        while not self.shouldEnd:
            sleep(30) # should be 30 seconds
            self.cluster_node.broadcast(heartbeat_cmd)
