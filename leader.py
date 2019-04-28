# leader.py
import threading
import process
import parse
import socket, pickle

class Leader(threading.Thread):
    def __init__(self, s, cluster_node):

        # Initialize class variables
        self.s = s
        self.cluster_node = cluster_node
        self.shouldEnd = False

        threading.Thread.__init__(self)


    def end(self):
        self.shouldEnd = True

    # This thread is responsible for handling new clients and broadcasting the heartbeat
    def run(self):
        # Heartbeat thread handles broadcasting the heartbeat to all followers
        heartbeat_thread 	= threading.Thread(target=self.heartbeatTimer)

        # Initialize incoming TCP connections
        self.s.bind((self.cluster_node.IP, self.cluster_node.port))
        self.cluster_node.port = self.s.getsockname()[1]
        self.s.listen(5) # number of connections to server

        print("Connection IP address: ", self.cluster_node.IP)
        print("Connection opened on port: ", self.s.getsockname()[1])

        # Handles new connections until it should end
        while not self.shouldEnd:
            # Accept connection
            conn, addr = self.s.accept()
            print("Connection from address:", addr)

            # Log replication for new followers
            log = open("log.txt", 'r')
            contents = ""
            for line in log:
                contents += line
            log.close()

            conn.send(pickle.dumps(parse.Command("log", [contents])))

            # Append new follower to followers
            self.cluster_node.followers.append(conn)

            # Handles adding clients and receiving messages
            add_client_thread = threading.Thread(target=self.receiveFromClient, args=(conn, addr))

            add_client_thread.start()


        add_client_thread.join()
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
        heartbeat_cmd = parse.Command("heartbeat", self.cluster_node.follower_ips)
        while not self.shouldEnd:
            time.sleep(7) # should be 30 seconds
            self.cluster_node.broadcast(heartbeat_cmd)
