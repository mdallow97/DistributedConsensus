# process.py
import parse

# Delegate processing of command to below functions
def processCommand(command, cluster_node, addr=None):

    # FOLLOWER COMMANDS
    if command.getCommand() == "ClientCommit":
        # ClienCommit(!<var>) or ClientCommit(<var>, <value>)
        return ClientCommit(command, cluster_node)

    elif command.getCommand() == "dumpLog" or command.getCommand() == "LogRequest":
        # dumpLog(<id>)
        return dumpLog(command, cluster_node)

    elif command.getCommand() == "LogReturn":
        return LogReturn(command, cluster_node, addr)

    elif command.getCommand() == "RequestVote":
        # RequestVote(<term>, <id>)
        return RequestVote(command, cluster_node)

    # LEADER COMMAND
    elif command.getCommand() == "AppendEntries":
        # AppendEntries(<index>, !<var>) or AppendEntries(<index>, <var>, <value>)
        return AppendEntries(command, cluster_node)



# Returns Success! or Failed!
def ClientCommit(command, cluster_node):
    # ClienCommit(!<var>) or ClientCommit(<var>, <value>)
    # Process parameters

    params = command.getParams()
    if command.shouldReturnVal():
        # Broadcast
        read_entry = parse.Command("AppendEntries", [cluster_node.commit_index, params[0]], True)
        return AppendEntries(read_entry, cluster_node)
    elif cluster_node.isLeader():
        new_entry = parse.Command("AppendEntries", [cluster_node.commit_index, params[0], params[1]])

        cluster_node.broadcast(new_entry)
        new_entry = parse.Command("LeaderAppend", [cluster_node.commit_index, params[0], params[1]])

        return AppendEntries(new_entry, cluster_node)

    else:
        return None


# Returns either value at index, or Success!/Failed!
def AppendEntries(command, cluster_node):
    # AppendEntries(<index>, !<var>) or AppendEntries(<index>, <var>, <value>)
    log = open("log.txt", 'r+')
    params = command.getParams()



    print("This node's index: ", cluster_node.commit_index)
    print("Leaders index: ", int(params[0]))

    # Need to make sure that the commit index is the same as the leader
    if cluster_node.commit_index != int(params[0]):
        # Replicate log and set commit_index

        return parse.Command("print", ["Failed!"])

    # Copy file contents into a string
    contents = ""
    for line in log:
        contents = contents + line

    # If it should return a value at a specific <var>
    if command.shouldReturnVal():
        # Find start and end indexes for <value>
        if params[1] not in contents:
            return  parse.Command("print", ["Failed!"])

        index = contents.find(params[1])
        var = contents[index:index+len(params[1])]

        start_index = index+len(params[1])+1
        temp = contents[start_index:len(contents)]

        end_index = temp.index('\n')+start_index
        val = contents[start_index:end_index]

        return  parse.Command("print", [val])

    else:
        # New value to be added to the beginning of the file
        # Edit string and write to the file
        cluster_node.commit_index += 1

        new_contents = params[1] + ':' + params[2] + '\n'

        for i in range(0, len(contents)):
            new_contents = new_contents + contents[i]

        try:
            log.truncate(0)
            log.write(new_contents)
            log.close()

        except IOError:
            if command.getCommand() == "LeaderAppend":
                return parse.Command("print", ["Failed!"])

    if command.getCommand() == "LeaderAppend":
        return parse.Command("print", ["Success!"])


def RequestVote(command, cluster_node):
    # RequestVote(<term>, <id>)
    print("vote")


def dumpLog(command, cluster_node):
    # dumpLog(<id>)
    id = command.getParams()[0]

    original_id = ""
    if len(command.getParams()) == 1:
        command.addParam(cluster_node.IP)
        original_id = cluster_node.IP
    else:
        original_id = command.getParams()[1]

    if id == cluster_node.IP:
        log = open("log.txt", 'r')
        contents = "\n\tMOST RECENT INDEX (TOP)\n"

        for line in log:
            contents += line

        contents += "\n\tOLDEST INDEX (BOTTOM)\n"

        return parse.Command("print", [contents, original_id])

    elif cluster_node.isLeader():
        isFollower = False

        for ip in cluster_node.follower_ips:
            if ip == id:
                isFollower = True

        if isFollower:
            logRequest = parse.Command("LogRequest", [id, original_id])
            cluster_node.broadcast(logRequest)

            return None
        else:
            return parse.Command("print", ["Failed!"])
    else:
        return None

def ReturnLog(command, cluster_node, addr):
    params = command.getParams()

    if params[1] != addr:
        return
    else:
        return params[0]
