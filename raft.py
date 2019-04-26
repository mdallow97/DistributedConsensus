import cluster
import socket
import sys

# Get local host name (IP)
hostname = socket.gethostname()
host = socket.gethostbyname(hostname)

# Parse arguments
if len(sys.argv) < 2:
    print("Formats: ")
    print("\tLeader: python raft.py <list_of_node_IP's>")
    print("\tFollowers: python raft.py <leader_ip> <leader_port>")
    exit()

if len(sys.argv) == 2:
    # Only possibility: P1 <follower_IP>
    node = cluster.ClusterNode(host, 0, "leader", sys.argv[1])

elif len(sys.argv) == 3:
    # can be either follower or leader command
    # P1 <leader_ip> <port> OR P1 <follower_ip> <follower_ip>
    isPort = True
    for c in sys.argv[2]:
        # If the argument contains a period, it is an IP address
        if c == '.':
            isPort = False

    # If it contains a port, then it is a follower
    if isPort:
        node = cluster.ClusterNode(sys.argv[1], int(sys.argv[2]), "follower", [])
    else:
        followers = [sys.argv[1], sys.argv[2]]
        node = cluster.ClusterNode(host, 0, "leader", followers)

# If it is none of the above, then it is a leader with a list of follower IPs
else:
    followers = []
    for i in range(1,len(sys.argv)-1):
        followers.append(sys.argv[i])

    node = cluster.ClusterNode(host, 0, "leader", followers)
