import cmd
import sys
from typing import override

import ingredients
from rich_console import console

# TODO: Make "buy" work outside ingredient volumes screen
all_commands = {"shop", "buy", "save", "quit"}
main_commands = {"shop"}


# TODO: Help info on command logic
class BarCmd(cmd.Cmd):
    intro = 'Welcome to the bar. Type help or ? to list commands.\n'
    prompt = '> '

    def __init__(self, bar_instance):  # Pass your Bar instance
        super().__init__()
        self.bar = bar_instance

    @override
    def onecmd(self, cmd):

        if isinstance(cmd, list):  # Check if find_command returned a tuple
            cmd, args = cmd  # Unpack the tuple
            if cmd == 'buy':
                if isinstance(args[0], str):
                    # Join ingredient name parts (excluding the last element which is the quantity)
                    ingredient_name = ' '.join(args[:-1])
                    quantity = args[-1]  # Get the last element as the quantity

                    ingredient = ingredients.get_ingredient(ingredient_name)
                    if ingredient:
                        if self.do_buy(ingredient, quantity):  # Call do_buy with ingredient and quantity
                            return True
                    else:
                        console.print(f"Ingredient '{ingredient_name}' not found.")
                        return False
                elif isinstance(args[0], ingredients.Ingredient):
                    self.do_buy(args[0], args[1])
                    return True

        else:
            return super().onecmd(cmd)

    '''
    @override
    def onecmd(self, line):
        cmd, arg, line = self.parseline(line)
        if not line:
            return self.emptyline()
        if cmd is None:
            return self.default(line)
        self.lastcmd = line

        if cmd == 'buy':  # Special handling for 'buy'
            parts = []
            current_part = ""
            in_quote = False

            for char in arg:  # Iterate through the argument string
                if char == '"':
                    in_quote = not in_quote
                    if not in_quote:  # End of quoted part
                        parts.append(current_part)
                        current_part = ""
                elif char == ' ' and not in_quote:
                    if current_part:
                        parts.append(current_part)
                        current_part = ""
                else:
                    current_part += char

            if current_part:  # Add the last part
                parts.append(current_part)

            if len(parts) > 1:  # Check if ingredient and quantity are provided
                ingredient_name = parts[0]
                quantity = parts[1] if len(parts) > 1 else None
                ingredient = ingredients.get_ingredient(ingredient_name)  # Get Ingredient object
                if ingredient:
                    self.do_buy(ingredient, quantity)  # Call do_buy with ingredient and quantity
                else:
                    console.print(f"Ingredient '{ingredient_name}' not found.")
                return

        super().onecmd(line)
    '''

    def do_buy(self, ingredient: ingredients.Ingredient = None, arg: str = ""):  # buy jameson 24
        parts = arg.split()
        if len(parts) == 3:
            if parts[0] == "buy":
                parts.remove("buy")

        if len(parts) == 2:
            ingredient = ingredients.get_ingredient(str(parts[0]))
            oz = parts[1]

        elif len(parts) == 1:
            oz = arg

        else:
            console.print("Incorrect number of arguments. Invalid buy command. Usage: buy <quantity>")
            return False

        try:
            oz = int(oz)
        except ValueError:
            console.print("Invalid quantity. Please enter a number.")
            return False

        if ingredient:
            price = ingredient.volumes[oz]
            balance = self.bar.balance
            if balance >= price:
                self.bar.balance -= price
                self.bar.inventory[ingredient] = self.bar.inventory.get(ingredient, 0) + oz
                # TODO: Give this return message a place on the fitted shop screen
                console.print(
                    f"Bought {oz}oz of {ingredient.name}. Current stock: {self.bar.inventory[ingredient]}")
                return True
            else:
                console.print(f"Insufficient funds. Bar balance: [money]${balance}")
                return False

        else:
            console.print("No ingredient selected. Please select an ingredient first.")
            return False

    def do_save(self, arg):
        """Save the current game state."""
        self.bar.save_game()  # Call the save_game() method of the Bar instance

    def do_quit(self, arg):
        """Exit the application."""
        self.bar.save_game()
        print("Exiting...")  # Optional: Print a message before exiting
        sys.exit(0)  # Terminate the application with exit code 0 (success)


def find_command(inpt, allowed_commands=None, force_beginning=False):
    # TODO: Make "jose silver" return "Jose Cuervo Especial Silver"
    # Because "jose" and "silver" on their own will both return multiple products
    # Currently entire input match must be sequential so "especial silver" or "ial sil" is required
    inpt = inpt.strip().lower()

    # <editor-fold desc="Splitting logic allowing for spaces in quotes">
    parts = []
    current_part = ""
    in_quotes = False

    for char in inpt:
        if char == '"':  # At quotes, flip space-allowing condition and end current part
            in_quotes = not in_quotes
            if not in_quotes:
                parts.append(current_part)
                current_part = ""
        elif char == ' ' and not in_quotes:  # When not inside quotes, end part at space
            if current_part:
                parts.append(current_part)
                current_part = ""
        else:  # Any other characters are part of the current part
            current_part += char

    if current_part:  # Add the last part at end of input
        parts.append(current_part)
    # </editor-fold>

    primary_command = parts[0]
    commands = allowed_commands or all_commands
    commands.add("quit")

    # <editor-fold desc="Find matching commands">
    matching_commands = []
    for command in commands:
        if len(primary_command) < 4 or force_beginning:  # Short inputs likely to be only the beginning of a word
            if command.startswith(primary_command):
                matching_commands.append(command)
        # Match to any part of command when input > 3, e.g. so "gold" can return "Jose Cuervo Especial Gold"
        if not matching_commands:
            if primary_command in command:
                matching_commands.append(command)
    # </editor-fold>

    if len(matching_commands) == 1:
        # found 1 match
        if len(parts) > 1:  # If arguments are present along the primary command
            return matching_commands[0], parts[1:]
        else:
            return matching_commands[0]
    elif len(matching_commands) == 0:
        # TODO: Sort valid commands
        return find_command(console.input(f"Valid commands: {commands} > "), commands)
    else:  # found either no match or more than one
        return find_command(console.input(f"Command matches: {matching_commands}"), commands)
