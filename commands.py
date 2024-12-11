from rich_console import console

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
        # found 1 match
        return matching_commands[0]
    elif len(matching_commands) == 0:
        return find_command(console.input(f"Valid commands: {commands}"), commands)
    else:  # found either no match or more than one
        return find_command(console.input(f"Command matches: {matching_commands}"), commands)
