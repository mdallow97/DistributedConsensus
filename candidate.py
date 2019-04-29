# candidate.py
import parse
import threading
import socket, pickle

class Candidate(threading.Thread):
    def __init__(self, s, cluster_node):
        self.s = s
        self.cluster_node = cluster_node

        threading.Thread.__init__(self)

    def run(self):
        self_address = [self.cluster_node.IP, self.cluster_node.port]
        self.cluster_node.votedFor = 0

        for cand_port in self.cluster_node.candidate_ports:
            addr = [cand_port[0], cand_port[1]]
            if self_address != addr:
                print("My port: ", self.cluster_node.port, "\tFollower port: ", cand_port[2])
                self.s.connect((cand_port[0], cand_port[2]))
                self.s.send(pickle.dumps(parse.Command("RequestVote", [self.cluster_node.current_term, self_address])))

                data = self.s.recv(self.cluster_node.BUFFER_SIZE)

                if not data:
                    continue
                else:
                    vote = pickle.loads(data)
                    if vote.getCommand() == "vote":
                        self.cluster_node.votedFor += 1
                        self.s.send(pickle.dumps(parse.Command("leaderip", [self.cluster_node.IP, self.cluster_node.port])))
