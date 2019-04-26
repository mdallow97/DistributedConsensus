# process.py

# used by leader and follower
def processCommand(command, cluster_node):

    if command.getCommand() == "ClientCommit":
        # Command will have only one or two parameters
        # ClienCommit(!<var>) or ClientCommit(<var>, <value>)
        return ClientCommit(command, cluster_node)

    elif command.getCommand() == "AppendEntries":
        # Command will have only two or three parameters
        # AppendEntries(<index>, !<var>) or AppendEntries(<index>, <var>, <value>)
        return AppendEntries(command, cluster_node.commit_index)


    elif command.getCommand() == "RequestVote":
        # RequestVote(<term>, <id>)
        return RequestVote(command, cluster_node)

def ClientCommit(command, cluster_node):
    # ClienCommit(!<var>) or ClientCommit(<var>, <value>)
    # Process parameters
    params = command.getParams()

    file = open("log.txt", 'r+')
    contents = ""

    for line in file:
        contents = contents + line

    index = contents.find(params[0])
    var = contents[index:index+len(params[0])]

    start_index = index+len(params[0])+1
    temp = contents[start_index:len(contents)]

    end_index = temp.index('\n')+start_index
    val = contents[start_index:end_index]


    if command.shouldReturnVal():
        return val
    else:
        # Edit string and write to the file
        self.cluster_node.commit_index = self.cluster_node.commit_index + 1
        self.cluster_node.current_commit = val
        new_contents = ""

        if index > -1:

            for i in range(0, len(contents)):
                if i == start_index:
                    new_contents = new_contents + params[1]
                    continue

                if i > start_index and i < end_index:
                    continue

                new_contents = new_contents + contents[i]


            try:
                file.truncate(0)
                file.write(new_contents)
                file.close()
            except IOError:
                return "Failed!"

        else:
            try:
                file.write(params[0] + ":" + params[1] + "\n")
                file.close()

            except IOError:
                return "Failed!"

    return "Success!"

def AppendEntries(command, commit_index):
# AppendEntries(<index>, !<var>) or AppendEntries(<index>, <var>, <value>)
    log = open("log.txt", 'r+')
    params = command.getParams()
    assert commit_index == int(params[0])
    contents = ""

    i = 0
    for line in log:
        contents = contents + line
        i = i + 1

    if command.shouldReturnVal():
        index = contents.find(params[1])
        var = contents[index:index+len(params[1])]

        start_index = index+len(params[1])+1
        temp = contents[start_index:len(contents)]

        end_index = temp.index('\n')+start_index
        val = contents[start_index:end_index]

        return val
    else:
        # Edit string and write to the file
        new_contents = params[1] + ':' + params[2] + '\n'

        for i in range(0, len(contents)):
            new_contents = new_contents + contents[i]

        try:
            log.truncate(0)
            log.write(new_contents)
            log.close()

        except IOError:
            return "Failed!"

    return "Success!"

def RequestVote(command, cluster_node):
    # RequestVote(<term>, <id>)
    print("vote")
