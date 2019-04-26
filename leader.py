# leader.py
import threading
import process
import parse
import socket, pickle

class Leader(threading.Thread):
    def __init__(self, s, cluster_node):
        self.s = s
        self.cluster_node = cluster_node
        self.shouldEnd = False

        threading.Thread.__init__(self)

    def end(self):
        self.shouldEnd = True

    def run(self):
        heartbeat_thread 	= threading.Thread(target=self.heartbeatTimer)


        self.s.bind((self.cluster_node.IP, self.cluster_node.port))
        self.cluster_node.port = self.s.getsockname()[1]
        self.s.listen(5) # number of connections to server
        print("Connection IP address: ", self.cluster_node.IP)
        print("Connection opened on port: ", self.s.getsockname()[1])


        while 1:

            conn, addr = self.s.accept()
            print("Connection from address:", addr)

            self.cluster_node.followers.append(conn)

            add_client_thread = threading.Thread(target=self.addNewClient, args=(conn, addr))

            add_client_thread.start()
            add_client_thread.join()
            if self.shouldEnd:
                break

        conn.close()
        print("Connection closed")

    def addNewClient(self, conn, addr):
        threading.Thread(target=self.quitThread, args=(conn,)).start()

        while 1:
            if self.shouldEnd:

                conn.close()
                self.cluster_node.followers.remove(conn)
                break

            command = parse.Command(None, None, None)
            try:
                data = conn.recv(self.cluster_node.BUFFER_SIZE)
                if not data: continue

                command = pickle.loads(data)
            except:
                break

            status = process.processCommand(command, self.cluster_node)
            print(status)
            conn.send(pickle.dumps(parse.Command("print", [status], False)))

            if not command.shouldReturnVal():
                self.cluster_node.broadcast(command)

    def quitThread(self, conn):
        while 1:
            if self.shouldEnd:
                conn.close()

    def heartbeatTimer(self):
        heartbeat_cmd = parse.Command("heartbeat", self.cluster_node.follower_ips, False)
        while not self.shouldEnd:
            time.sleep(7)
            self.cluster_node.broadcast(heartbeat_cmd)
