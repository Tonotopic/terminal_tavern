import cmd
import sys
from typing import override, Iterable
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from unidecode import unidecode
import warnings

import ingredients
import recipe
import rich_console
from rich_console import console
import bar

# TODO: Make "buy" work outside ingredient volumes screen
# TODO: Help info on command logic

warnings.filterwarnings("ignore", category=SyntaxWarning)

persistent_commands = {"shop", "buy", "menu", "save"}
main_commands = {"shop", "menu"}


def find_command(inpt, commands=None, force_beginning=False):
    """Takes an input string and a command list, and either returns a single command match,
    prints multiple matching commands for the user to choose between,
    or prints all valid commands if no valid command is found.

        Args:
          :param inpt: The string from user input.
          :param commands: Optional list of commands to match to. all_commands if None
          :param force_beginning: Can be set to True to disallow matching to the middle of a command.
        """
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
    commands = commands or persistent_commands
    sorted_commands = sorted(commands)
    sorted_commands.append("quit")
    if inpt == "":
        console.print(f"Valid commands: {sorted_commands}")
        return None

    # <editor-fold desc="Find matching commands">
    matching_commands = []
    for command in sorted_commands:
        if len(primary_command) < 4 or force_beginning:  # Short inputs likely to be only the beginning of a word
            if command.startswith(primary_command):
                matching_commands.append(command)
        # If it hasn't already matched to startswith
    if not matching_commands:
        for command in sorted_commands:
            # Match to any part of command when input > 3, e.g. so "gold" can return "Jose Cuervo Especial Gold"
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

        console.print(f"[error]Valid commands: {sorted_commands}")
        return None
    else:  # found either no match or more than one
        console.print(f"Command matches: {matching_commands}")
        return None


def parse_input(prompt, commands=None, force_beginning: bool = False):
    """Prints prompt, takes, standardizes, and validates input, handles spaces logic,
    and distinguishes primary commands from arguments.

        Args:
          :param prompt: Message printed just before the user's input cursor in the console.
          :param commands: Optional list of commands to pass to find_command. all_commands if None
          :param force_beginning: Can be set to True to disallow matching to the middle of a command.
        """
    inpt = console.input(f"[prompt]{prompt}:[/prompt][white] > ").strip().lower()

    # TODO: As commands with args are added, skip them here
    if not inpt.startswith("buy") and not inpt.startswith("add"):  # If not a command with args
        inpt = f'"{inpt}"'  # Group spaced words together

    inpt_cmd = find_command(inpt, commands, force_beginning)

    if isinstance(inpt_cmd, tuple):  # If find_command returned args
        primary_command, args = inpt_cmd  # Unpack the tuple
    else:
        primary_command = inpt_cmd  # The entire input is one part
        args = []

    return primary_command, args


def items_to_commands(lst: Iterable[ingredients.Ingredient]):
    #  Converts a list of ingredients, ingredient types, and/or strings into a list of commands for parsing.
    commands = set("")
    for entry in lst:
        if isinstance(entry, type):
            if entry == recipe.Recipe:
                commands.add("cocktails")
            else:
                obj = entry()
                commands.add(unidecode(f"{obj.format_type().lower()}s"))
        elif isinstance(entry, ingredients.Ingredient):
            commands.add(unidecode(entry.name.lower()))
        elif isinstance(entry, str):
            commands.add(entry.lower())

    return commands


def command_to_item(cmd, lst):
    #  Matches a string command to an ingredient or type from the given list.
    for entry in lst:
        if isinstance(entry, type):
            if entry == recipe.Recipe:
                if cmd == "cocktails":
                    return recipe.Recipe
            elif cmd == f"{unidecode(entry().format_type().lower())}s":
                return entry
        elif isinstance(entry, ingredients.Ingredient):
            if cmd == unidecode(entry.name.lower()):
                return entry
        else:
            console.print("[error]command_to_item argument not registering as type or Ingredient")
    return None


class BarCmd(cmd.Cmd):
    intro = 'Welcome to the bar. Type help or ? to list commands.\n'
    prompt = '> '

    def __init__(self, bar_instance):  # Pass your Bar instance
        super().__init__()
        self.bar = bar_instance

    @override
    def onecmd(self, cmd, return_result=False):
        # Check if find_command returned a tuple
        if isinstance(cmd, list):
            cmd, args = cmd  # Unpack the tuple
            if cmd == 'buy':
                if len(args) == 2:
                    # If ingredient passed as Ingredient
                    if isinstance(args[0], ingredients.Ingredient):
                        result = self.do_buy(args[0], args[1])
                    # If ingredient passed as string
                    elif isinstance(args[0], str):
                        # Join ingredient name parts (excluding the last element which is the quantity)
                        ingredient_name = ' '.join(args[:-1])
                        quantity = args[-1]  # Get the last element as the quantity

                        ingredient = ingredients.get_ingredient(ingredient_name)
                        if ingredient:
                            result = self.do_buy(ingredient, quantity)
                        else:
                            console.print(f"[error]Ingredient '{ingredient_name}' not found.")
                            return False
                    else:
                        console.print("[error]Invalid arguments.")
                        return False

                    if return_result:  # If we need to check the success of do_buy
                        return result
                    else:  # Just check success of passing args to function
                        return True

                else:  # Not enough arguments
                    console.print("[error]Syntax: buy \[volume] | buy 24 > ")
                    return False
        else:
            return super().onecmd(cmd)

    def do_shop(self, arg):
        self.bar.shop()

    def do_buy(self, ingredient: ingredients.Ingredient = None, arg=""):  # buy jameson 24
        parts = arg.split()
        if len(parts) == 3:
            if parts[0] == "buy":
                parts.remove("buy")

        if len(parts) == 2:
            ingredient = ingredients.get_ingredient(str(parts[0]))
            volume = parts[1]

        elif len(parts) == 1:
            volume = arg

        else:
            console.print("[error]Incorrect number of arguments. Invalid buy command. Usage: buy <quantity>")
            return False

        try:
            volume = int(volume)
        except ValueError:
            console.print("[error]Invalid quantity. Please enter a number.")
            return False

        if ingredient:
            if volume in ingredient.volumes:
                price = ingredient.volumes[volume]
                balance = self.bar.balance
                if balance >= price:
                    self.bar.balance -= price
                    self.bar.inventory[ingredient] = self.bar.inventory.get(ingredient, 0) + volume
                    return True
                else:
                    console.print(f"[error]Insufficient funds. Bar balance: [money]${balance}")
                    return False
            else:
                console.print(f"[error]Invalid volume. Available: {[oz for oz in ingredient.volumes.keys()]}")
                return False
        else:
            console.print("[error]No ingredient selected. Please select an ingredient first.")
            return False

    def do_menu(self, arg):
        self.bar.screen = bar.MENU
        global typ
        typ = None
        prompt = "'Back' to go back"

        while self.bar.screen == bar.MENU:
            menu_table, menu_list = self.bar.show_menu(typ=typ, expanded=True)
            bar_menu_panel = Panel(title=f"{self.bar.name} Menu", renderable=menu_table, border_style=rich_console.styles.get("bar_menu"))
            bar_menu_layout = Layout(name="bar_menu_layout", renderable=bar_menu_panel)

            console.print(bar_menu_layout)

            commands = items_to_commands(menu_list)
            commands.add("add")
            commands.add("back")

            primary_cmd = None
            while primary_cmd is None:
                primary_cmd, args = parse_input(prompt, commands)
            if primary_cmd == "back":
                if typ is None:
                    self.bar.screen = bar.MAIN
                else:
                    typ = None
            elif primary_cmd == "add":
                ing_cmd = find_command(args[0], items_to_commands(menu_list))
                if ing_cmd is not None:  # e.g. add beer
                    add_typ = command_to_item(ing_cmd, menu_list)
                    self.do_add(add_typ)
            elif primary_cmd in commands:
                typ = command_to_item(primary_cmd, menu_list)
            elif self.onecmd(primary_cmd):
                pass
            else:
                console.print("[error]No allowed command recognized.")

    def do_add(self, add_typ, add_arg=""):
        self.bar.screen = bar.MENU
        inv_ingredients = ingredients.list_ingredients(self.bar.inventory, add_typ)

        if add_arg != "":
            ing_command, empty_args = find_command(add_arg, items_to_commands(inv_ingredients))
            if ing_command is not None:
                ingredient = command_to_item(ing_command, inv_ingredients)
                if ingredient:
                    self.bar.menu[ingredient.get_menu_section()].append(ingredient)
                    console.print(f"{ingredient.name} added to menu.")
                    return True
                else:
                    console.print("[error]Ingredient arg given to add command, but ingredient not found")
                    return False
            else:
                console.print("[error]Arg given to add method, but find_command returned None")
                return False

        else:  # No ingredient given
            if add_typ is ingredients.Ingredient:
                console.print("[error]No type or ingredient given to add command. Syntax: add beer | add guinness")
                return False
            else:
                add_tool_table, add_tool_list = self.bar.table_inv(add_typ, off_menu=True)
                add_tool_panel = Panel(add_tool_table)
                add_tool_layout = Layout(add_tool_panel)

                console.print(add_tool_layout)

                adding = True
                add_commands = items_to_commands(add_tool_list)
                add_commands.add("back")
                add_commands.add("quit")
                while adding:
                    primary_cmd, ing_args = parse_input("Type a name to add", add_commands)
                    if primary_cmd:
                        if primary_cmd == "back":
                            return
                        else:
                            ingredient = command_to_item(primary_cmd, inv_ingredients)
                            self.bar.menu[ingredient.get_menu_section()].append(ingredient)
                            adding = False

    def do_save(self, arg):
        """Save the current game state."""
        self.bar.save_game()  # Call the save_game() method of the Bar instance

    def do_quit(self, arg):
        """Exit the application."""
        self.do_save(arg)
        print("Exiting...")  # Optional: Print a message before exiting
        sys.exit(0)  # Terminate the application with exit code 0 (success)
