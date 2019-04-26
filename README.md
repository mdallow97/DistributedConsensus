# DistributedConsensus
Implements a simplified version of the Raft algorithm

parse.py:  parses all incoming client commands
process.py:  process all commands coming from the leader or client:
    AppendEntries()
    ClientCommit()
    RequestVote()
    
follower.py:  handles the follower class, threads for receiving and parsing commands and sending them to the leader

candidate.py:  handles the candidate class, it is not fully implemented

cluster.py: handles the ClusterNode class, which supports the node timeouts and election process

raft.py: main program, finds addresses and port numbers

log.txt: contains the entry log for whatever node is running there
