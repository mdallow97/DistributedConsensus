# candidate.py
import parse
import threading

class Candidate(threading.Thread):
    def __init__(self, s, cluster_node):
        self.s = s
        self.cluster_node = cluster_node

        threading.Thread.__init__(self)

    def run(self):
        print("gets here")
        self.s.bind((self.cluster_node.IP, self.cluster_node.port))


        election_cmd = parse.Command("election", self.IP, False)
        self.cluster_node.broadcast(election_cmd)
