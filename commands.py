all_commands = {"purchase"}
main_commands = {"purchase"}


def find_command(inpt, allowed_commands=None):
    commands = allowed_commands or all_commands

    commands.add("back")
    commands.add("quit")

    matching_commands = []

    for command in commands:
        if command.startswith(inpt):
            matching_commands.append(command)

    if len(matching_commands) == 1:
        # found a match
        return matching_commands[0]

    # found either no match or more than one
    return None
