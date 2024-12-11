import cmd
import re
import sys
from typing import override, Iterable

import rich.box
from rich.layout import Layout
from rich.panel import Panel
from unidecode import unidecode

import ingredients
from recipe import Recipe
import rich_console
from rich_console import console, Screen

# TODO: Make "buy" work outside ingredient volumes screen
# TODO: Help info on command logic

persistent_commands = {"shop", "buy", "menu"}
help_panels = {
    "help": f"Syntax: [cmd]'help \\[term]'[/cmd]\n"
            f"[cmd]'Help'[/cmd] can be used on commands (shop, add, etc), products (lychee, Ketel One Classic, etc), "
            f"and some game concepts (input, recipe, etc).\n"
            f"Command parsing will work the same for the help arg, i.e. [cmd]'help fish pois'[/cmd]"
            f" can return the description for [italic][beer]Little Fish Saison du Poisson.[/italic][/beer]",

    "input": f"Input parsing is [highlight]case-insensitive[/highlight] and allows for partial terms - "
             f"[cmd]'rh b f h'[/cmd] is as effective as 'Rhinegeist Beer for Humans', and in the right context, "
             f"[cmd]'sh'[/cmd] will work as effectively as [cmd]'shop'[/cmd].\n"
             f"An input of 3 or fewer characters will [highlight]priority match to the beginning[/highlight] of the term.\n"
             f"Generally, when partial input matches to multiple currently valid commands,"
             f"a message will print listing all matching commands, and the previous prompt will loop.\n"
             f"In cases where one valid command entirely contains another, i.e. [cmd]'lemonade'[/cmd] and [cmd]'lemon'[/cmd], "
             f"or [cmd]'Crown Royal Black'[/cmd] and [cmd]'Crown Royal Blackberry'[/cmd], the [highlight]most base command[/highlight] will be favored.\n"
             f"However, mid-word matches are allowed in most cases, so the likes of [cmd]'onade'[/cmd] and [cmd]'yal blackb'[/cmd] "
             f"can be used instead of having to type all the way to [cmd]'crown royal blackb'[/cmd].",

    # <editor-fold desc="Game Concepts">
    "recipe": f"[highlight]Recipes[/highlight], the backbones of [cocktails]Cocktails[/cocktails], are made up of [highlight]Ingredients[/highlight], "
              f"which may be spirits, liqueurs, syrups, fruits, spices, etc. as well as beer, wine, cider, and mead.\n"
              f"View your bar's drink [cmd]'menu'[/cmd], [cmd]'add cocktail'[/cmd], and create a [cmd]'new'[/cmd] cocktail to write a recipe.\n"
              f"You do [italic]not[/italic] need to have the ingredients in your inventory to write a new recipe.\n"
              f"[cmd]'Help cocktails'[/cmd] to view more on cocktails.",

    "price": f"A menu item's [highlight]price[/highlight] before [highlight]markup[/highlight] is based on its per-unit cost to you -\n "
             f"[money]$3.75[/money] for drinks costing you less than [money]$1.25[/money] wholesale, \n"
             f"3x wholesale costs between [money]$1.25[/money] and [money]$3.00[/money], \n"
             f"or 2x wholesale costs over [money]$3.00[/money].\n"
             f"[highlight]Markup[/highlight] or [highlight]markdown[/highlight] can then be applied per-item.",
    # </editor-fold>

    # <editor-fold desc="Commands">
    "shop": f"[cmd]'Shop'[/cmd] allows you to view available products by type, as well as to view your bar's stock in each section.\n"
            f"Type the name of a category or product from the current section (i.e. 'drinks', 'jameson') to view.\n"
            f"[cmd]'Shop'[/cmd] again to exit. [cmd]'Back'[/cmd] to go back to the parent category.\n"
            f"While viewing a product, [cmd]'buy \\[volume]'",

    "menu": f"[cmd]'Menu'[/cmd] shows the expanded drink menu currently made available at your bar, and allows you to manage it.\n"
            f"From the menu overview, type a category (i.e. beer) to expand the category.\n"
            f"[cmd]'Add \\[category]'[/cmd], i.e. [cmd]'add cocktail'[/cmd], to view drinks that can be added to the menu,"
            f"or additionally for cocktails, to create a new recipe.",

    "buy": f"Syntax: [cmd]'buy \\[volume]'[/cmd]\n"
           f"Buy the product currently being viewed, in the specified volume.\n"
           f"[warn]Note: Buying a product does [italic]not[/italic] automatically add it to the menu.",

    "add": f"Syntax: [cmd]'add \\[category]'[/cmd]\n"
           f"Used in the bar's drink menu to add products of the specified type.\n"
           f"[cmd]'Add cocktails'[/cmd] allows both selecting from created recipes, and writing them ([cmd]'new'[/cmd]).",
    # </editor-fold>

}


def draw_help_panel(cmd):
    panel = Panel(help_panels.get(cmd), title=f"Help: {cmd}", box=rich.box.ASCII2,
                  style=rich_console.styles.get("highlight"), width=100)
    console.print(panel)


def find_command(inpt, commands=None, force_beginning=False):
    """Takes an input string and a command list, and either returns a single command match,
    prints multiple matching commands for the user to choose between,
    or prints all valid commands if no valid command is found.

        Args:
          :param inpt: The string from user input.
          :param commands: Optional list of commands to match to. all_commands if None
          :param force_beginning: Can be set to True to disallow matching to the middle of a command.
        """
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
    if "back" in sorted_commands:
        sorted_commands.remove("back")
        sorted_commands.append("back")
    sorted_commands.insert(0, "help")
    sorted_commands.append("quit")
    if inpt == "" or inpt == '""':
        console.print(f"Valid commands: {sorted_commands}")
        return None

    # <editor-fold desc="Find matching commands">
    # Startswith matching
    matching_commands = []
    for command in sorted_commands:
        # Short inputs likely to be only the beginning of a word
        if len(primary_command) < 4 or force_beginning:
            if command.startswith(primary_command):
                matching_commands.append(command)

    # Mid-word matching - If it hasn't already matched to startswith
    if not matching_commands:
        # Match to any part of command when input > 3, e.g. so "gold" can return "Jose Cuervo Especial Gold"
        input_words = primary_command.split()

        for command in sorted_commands:

            matching = True

            while matching:
                if len(input_words) > len(command.split()):
                    matching = False

                for input_word in input_words:
                    word_has_match = False
                    for full_name_word in command.split():
                        if len(input_word) < 3:
                            if full_name_word.startswith(input_word):
                                word_has_match = True
                                break
                        else:
                            pattern = r"\s*".join(input_word)
                            if re.search(pattern, full_name_word):
                                word_has_match = True
                                break
                    if not word_has_match:
                        matching = False
                if matching:  # After all input words, there are none that don't match the command
                    matching_commands.append(command)
                    break

    # </editor-fold>

    if len(matching_commands) == 1:
        # found 1 match
        if len(parts) > 1:  # If arguments are present along the primary command
            return matching_commands[0], parts[1:]
        else:
            return matching_commands[0]
    elif len(matching_commands) == 0:
        if len(sorted_commands) <= 10:
            console.print(f"[error]Valid commands: {sorted_commands}")
        else:
            console.print(f"[error]No matching term found for [cmd]{inpt}")
        return None
    elif len(matching_commands) > 1:  # found more than one match
        most_base_cmd = None
        for cmd in matching_commands:
            for ref_cmd in matching_commands:
                if cmd in ref_cmd and cmd != ref_cmd:
                    most_base_cmd = cmd
                elif ref_cmd in cmd and cmd != ref_cmd:
                    most_base_cmd = ref_cmd
        if most_base_cmd is not None:
            return most_base_cmd
        else:
            console.print(f"Matching commands : {matching_commands}")


def parse_input(prompt, commands=None, force_beginning: bool = False):
    """Prints prompt, takes, standardizes, and validates input, handles spaces logic,
    and distinguishes primary commands from arguments.

        Args:
          :param prompt: Message printed just before the user's input cursor in the console.
          :param commands: Optional list of commands to pass to find_command. all_commands if None
          :param force_beginning: Can be set to True to disallow matching to the middle of a command.
        """
    inpt = ""
    while inpt == "":
        inpt = console.input(f"[prompt]{prompt}:[/prompt][white] > ").strip().lower()

    # TODO: As commands with args are added, skip them here
    # If not a command with args
    if not inpt.startswith("buy") and not inpt.startswith("ad") and not inpt.startswith("help") and not inpt.startswith(
            "rem"):
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
            if entry == Recipe:
                commands.add("cocktails")
            else:
                obj = entry()
                commands.add(unidecode(f"{obj.format_type().lower()}s"))
        elif isinstance(entry, ingredients.Ingredient):
            commands.add(unidecode(entry.name.lower()))
        elif isinstance(entry, str):
            commands.add(entry.lower())
        elif isinstance(entry, Recipe):
            commands.add(entry.name.lower())

    return commands


def command_to_item(cmd, lst):
    #  Matches a string command to an ingredient or type from the given list.
    if cmd is None:
        return None
    for entry in lst:
        if isinstance(entry, type):
            if entry == Recipe:
                if cmd == "cocktails":
                    return Recipe
            elif f"{unidecode(entry().format_type().lower())}s".startswith(cmd):
                return entry
        elif isinstance(entry, ingredients.Ingredient):
            if cmd == unidecode(entry.name.lower()):
                return entry
        elif isinstance(entry, Recipe):
            if cmd == unidecode(entry.name.lower()):
                return entry
        elif isinstance(entry, str):
            if cmd == entry:
                return entry
        else:
            console.print("[error]command_to_item argument not registering as type or Ingredient")
    return None


class BarCmd(cmd.Cmd):
    intro = 'Welcome to the bar. Type help or ? to list commands.\n'

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
                    console.print("[error]Syntax: buy \\[volume] | buy 24 > ")
                    return False
        else:
            return super().onecmd(cmd)

    def input_loop(self, prompt, commands, force_beginning=False, ingredient = None, bar=None):
        """Loops the prompt checking for the success of certain commands so feedback can be shown without
        re-drawing the entire screen."""
        found_valid_input = False
        while found_valid_input is False:
            inpt = parse_input(prompt, commands, force_beginning)
            if inpt is None:
                continue
            primary_cmd, args = inpt
            if primary_cmd == "quit":
                self.do_quit("")
            elif primary_cmd == "help":
                ingredient_cmds = items_to_commands(ingredients.all_ingredients)
                help_args = help_panels.keys()

                arg_input = " ".join(args)
                if arg_input == "":
                    draw_help_panel("help")
                    console.print(f"Help topics: {help_args}")
                    continue

                arg = find_command(f'"{arg_input}"', help_args)
                if arg in help_panels.keys():
                    draw_help_panel(arg)
                    continue
                elif arg in ingredient_cmds:
                    arg_ing = command_to_item(arg, ingredients.all_ingredients)
                    console.print(arg_ing.description())
                    continue
            elif primary_cmd == "buy":
                if len(args) > 0:
                    if self.do_buy(ingredient, args[0]):
                        return primary_cmd, args[0]
                else:
                    console.print("[error]Incorrect number of arguments. Usage: buy <quantity>")
            elif primary_cmd == ("add" or "remove") and ingredient is None and len(args) == 0:
                console.print("[error]Invalid args. Use: 'add cocktail', 'add beer', etc.")
                continue
            elif primary_cmd == "add":
                type_displaying = ingredient
                if type_displaying is None:
                    if self.bar.menu.add(args[0]):
                        return primary_cmd, args
                else:
                    if self.bar.menu.add(type_displaying):
                        return primary_cmd, args
            elif primary_cmd == "remove":
                if bar.menu.remove(args[0]):
                    return primary_cmd, args
            else:
                return primary_cmd, args

            # <editor-fold desc="Command Functions">

    def do_buy(self, ingredient: ingredients.Ingredient = None, arg=""):
        parts = arg.split()

        if len(parts) == 2:  # i.e. buy 24
            ingredient = ingredients.get_ingredient(str(parts[0]))
            volume = parts[1]

        elif len(parts) == 1:
            volume = arg

        else:
            console.print("[error]Incorrect number of arguments. Usage: buy <quantity>")
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

    def do_quit(self, arg):
        """Exit the application."""
        self.do_save(arg)
        print("Exiting...")  # Optional: Print a message before exiting
        sys.exit(0)  # Terminate the application with exit code 0 (success)

    def do_shop(self, arg):
        self.bar.shop()

    def do_save(self, arg):
        """Save the current game state."""
        self.bar.save_game()  # Call the save_game() method of the Bar instance

    # </editor-fold>
