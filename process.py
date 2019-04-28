# process.py
import parse

# Delegate processing of command to below functions
def processCommand(command, cluster_node):

    # FOLLOWER COMMANDS
    if command.getCommand() == "ClientCommit":
        # ClienCommit(!<var>) or ClientCommit(<var>, <value>)
        return ClientCommit(command, cluster_node)

    elif command.getCommand() == "dumpLog":
        # dumpLog(<id>)
        return dumpLog(command, cluster_node)

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
    else:

        new_entry = parse.Command("AppendEntries", [cluster_node.commit_index, params[0], params[1]], False)
        cluster_node.broadcast(new_entry)

        new_entry = parse.Command("AppendEntries!", [cluster_node.commit_index, params[0], params[1]], False)
        if cluster_node.isLeader():
            return AppendEntries(new_entry, cluster_node)

        else:
            return None


# Returns either value at index, or Success!/Failed!
def AppendEntries(command, cluster_node):
    # AppendEntries(<index>, !<var>) or AppendEntries(<index>, <var>, <value>)
    log = open("log.txt", 'r+')
    params = command.getParams()

    # Need to make sure that the commit index is the same as the followers
    assert cluster_node.commit_index == int(params[0])

    # Copy file contents into a string
    contents = ""
    for line in log:
        contents = contents + line

    # If it should return a value at a specific <var>
    if command.shouldReturnVal():
        # Find start and end indexes for <value>
        if params[1] not in contents:
            return "Failed!"

        index = contents.find(params[1])
        var = contents[index:index+len(params[1])]

        start_index = index+len(params[1])+1
        temp = contents[start_index:len(contents)]

        end_index = temp.index('\n')+start_index
        val = contents[start_index:end_index]

        return val

    else:
        # New value to be added to the beginning of the file
        # Edit string and write to the file
        new_contents = params[1] + ':' + params[2] + '\n'

        for i in range(0, len(contents)):
            new_contents = new_contents + contents[i]

        try:
            log.truncate(0)
            log.write(new_contents)
            log.close()

        except IOError:
            if command.getCommand() == "AppendEntries!":
                return "Failed!"

    if command.getCommand() == "AppendEntries!":
        return "Success!"


def RequestVote(command, cluster_node):
    # RequestVote(<term>, <id>)
    print("vote")


def dumpLog(command, cluster_node):
    # dumpLog(<id>)
    id = command.getParams()[0]
    log = open("log.txt", 'r')

    contents = "\n\tMOST RECENT INDEX (TOP)\n"

    for line in log:
        contents += line

    contents += "\n\tOLDEST INDEX (BOTTOM)\n"

    return contents
