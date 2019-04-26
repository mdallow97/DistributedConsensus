import cluster
import socket
import sys

hostname = socket.gethostname()
host = socket.gethostbyname(hostname)

if len(sys.argv) < 2:
    print("Formats: ")
    print("\tLeader: python raft.py <list_of_node_IP's>")
    print("\tFollowers: python raft.py <leader_ip> <leader_port>")
    exit()

if len(sys.argv) == 2:
    # Only possibility: P1 <follower_IP>
    node = cluster.ClusterNode(host, 0, "leader", sys.argv[1])

elif len(sys.argv) == 3:
    # can be either leader or follower command
    # P1 <ip> <port> OR P1 <follower_ip> <follower_ip>
    isPort = True
    for c in sys.argv[2]:
        if c == '.':
            isPort = False

    if isPort:
        node = cluster.ClusterNode(sys.argv[1], int(sys.argv[2]), "follower", [])
    else:
        followers = [sys.argv[1], sys.argv[2]]
        node = cluster.ClusterNode(host, 0, "leader", followers)

else:
    followers = []
    for i in range(1,len(sys.argv)-1):
        followers.append(sys.argv[i])

    node = cluster.ClusterNode(host, 0, "leader", followers)
