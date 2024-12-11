import re
from typing import Iterable

import rich.box
from rich.panel import Panel
from unidecode import unidecode

import ingredients
import logger
import utils
from recipe import Recipe
import rich_console
from rich_console import console

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

    "buy": f"Syntax: [cmd]'buy \\[volume]'[/cmd]\n, e.g. [cmd]'buy 96'[/cmd]"
           f"Buy the product currently being viewed, in the specified volume.\n"
           f"[warn]Note: Buying a product does [italic]not[/italic] automatically add it to the menu.",

    "add": f"Syntax: [cmd]'add \\[category]'[/cmd]\n"
           f"Used in the bar's drink menu to add products of the specified type.\n"
           f"[cmd]'Add cocktails'[/cmd] allows both selecting from created recipes, and writing them ([cmd]'new'[/cmd]).",

    "markup": f"Syntax: [cmd]'markup \\[menu item or category]'[/cmd], e.g. [cmd]'markup guinness', 'markup beer'[/cmd]\n"
                            f"Markup and markdown allow you to tweak the calculated price of a menu item.\n"
                            f"They can be used simultaneously, so that markup can reflect your preferred initial price, "
                            f"while markdown can represent temporary pricing for specials."
                            f"[cmd]'markup'[/cmd] and [cmd]'markdown'[/cmd] can be used at the menu management screen.",

    "markdown": f"Syntax: [cmd]'markdown \\[menu item or category]'[/cmd], e.g. [cmd]'markdown guinness', 'markdown beer'[/cmd]\n"
                            f"Markup and markdown allow you to tweak the calculated price of a menu item.\n"
                            f"They can be used simultaneously, so that markup can reflect your preferred initial price"
                            f"while markdown can represent temporary pricing for specials.\n"
                            f"[cmd]'markup'[/cmd] and [cmd]'markdown'[/cmd] can be used at the menu management screen.",
    # </editor-fold>

}


def draw_help_panel(cmd):
    panel = Panel(help_panels.get(cmd), title=f"Help: {cmd}", box=rich.box.ASCII2,
                  style=rich_console.styles.get("highlight"), width=100)
    console.print(panel)


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


def find_command(inpt, commands=None, force_beginning=False, feedback=True):
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
    sorted_commands.insert(0, "help")
    if "back" in sorted_commands:
        sorted_commands.remove("back")
        sorted_commands.append("back")
    sorted_commands.append("quit")
    if inpt == "" or inpt == '""':
        if feedback:
            console.print(f"Valid commands: {sorted_commands}")
        return None

    # <editor-fold desc="Find matching commands">
    # Startswith matching
    matching_commands = []
    input_words = primary_command.split()
    if len(input_words) == 0:
        input_words[0] = primary_command
    for command in sorted_commands:
        matching = True
        cmd_words = command.split()
        while matching:
            if len(input_words) > len(cmd_words):
                matching = False
                break
            for i, cmd_word in enumerate(cmd_words):
                if len(input_words) < i + 1:
                    break
                if len(input_words[i]) < 4 or force_beginning:
                    if not cmd_word.startswith(input_words[i]):
                        matching = False
                        break
                else:
                    pattern = r"\s*".join(input_words[i])
                    if not re.search(pattern, cmd_word):
                        matching = False
                        break
            if matching:
                matching_commands.append(command)
                break

    # Mid-word matching - If it hasn't already matched to startswith, match to any part of commands
    if not matching_commands:
        for command in sorted_commands:
            matching = True
            while matching:
                if len(input_words) > len(command.split()):
                    matching = False
                for input_word in input_words:
                    word_has_match = False
                    for cmd_word in command.split():
                        if len(input_word) < 3:
                            if cmd_word.startswith(input_word):
                                word_has_match = True
                                break
                        else:
                            pattern = r"\s*".join(input_word)
                            if re.search(pattern, cmd_word):
                                word_has_match = True
                                break
                    if not word_has_match:
                        matching = False
                if matching:  # After all input words, there are none that don't match the command
                    matching_commands.append(command)
                    break

    # </editor-fold>

    if feedback:
        logger.log(f"'{inpt}' command matches : {matching_commands}")

    if len(matching_commands) == 1:
        # found 1 match
        if len(parts) > 1:  # If arguments are present along the primary command
            return matching_commands[0], parts[1:]
        else:
            return matching_commands[0]
    elif len(matching_commands) == 0:
        if len(sorted_commands) <= 15:
            if feedback:
                console.print(f"[error]Valid commands: {sorted_commands}")
        else:
            if feedback:
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
            logger.log("Most base command: " + most_base_cmd)
            return most_base_cmd
        else:
            if feedback:
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
    # If not a command with args, group spaced words together
    arg_commands = ["buy", "add", "help", "remove", "load", "markup", "markdown"]
    if not find_command(inpt.split()[0], arg_commands, feedback=False):
        logger.log(f"Not a command with args - wrapping {inpt} in quotes")
        inpt = f'"{inpt}"'

    inpt_cmd = find_command(inpt, commands, force_beginning)

    if isinstance(inpt_cmd, tuple):  # If find_command returned args
        primary_command, args = inpt_cmd  # Unpack the tuple
    else:
        primary_command = inpt_cmd  # The entire input is one part
        args = []

    return primary_command, args


def input_loop(prompt, commands, force_beginning=False, ingredient=None, bar=None):
    """Loops the prompt checking for the success of certain commands so feedback can be shown without
    re-drawing the entire screen."""
    global found_valid_input
    found_valid_input = False
    while found_valid_input is False:
        inpt = parse_input(prompt, commands, force_beginning)
        if inpt[0] is None:
            continue
        primary_cmd, args = inpt

        if primary_cmd == "quit":
            if bar:
                bar.screen = rich_console.Screen.MAIN
                utils.save_game(bar)
            utils.quit()
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
        elif primary_cmd == "new" and "load" not in commands:  # Skip check_new (for new game) when new cocktail
            found_valid_input = True
            return primary_cmd, args
        elif callable(globals().get("check_" + primary_cmd)):
            result = globals().get("check_" + primary_cmd)(args, bar, ingredient)
            if result is not None:
                found_valid_input = True
                return result
        else:
            found_valid_input = True
            return primary_cmd, args

        # <editor-fold desc="Command Functions">


# <editor-fold desc="Input Loop Command Checkers">
def check_add(args, bar, ingredient):
    if ingredient is None and len(args) == 0:
        console.print("[error]Invalid args. Use: 'add cocktail', 'add beer', etc.")
        return None
    type_displaying = ingredient
    if type_displaying is None:
        typ = command_to_item(find_command(args[0], ["cocktails", "beers", "ciders", "wines", "meads"]),
                              [Recipe, ingredients.Beer, ingredients.Cider, ingredients.Wine, ingredients.Mead])
        if bar.menu.add(typ):
            return "add", args
    else:
        if bar.menu.add(type_displaying):
            return "add", args


def check_buy(args, bar, ingredient):
    if len(args) > 0:
        if bar.stock.buy(ingredient=ingredient, arg=args[0]):
            return "buy", args
    else:
        console.print("[error]Incorrect number of arguments. Usage: buy <quantity>")


def check_load(args, bar, ingredient):
    try:
        if len(utils.list_saves()) < int(args[0]):
            console.print(f"[error]There are only {len(utils.list_saves())} save files to load from.")
        else:
            return "load", args
    except IndexError:
        console.print("[error]Syntax: 'load \\[num]'")
    except ValueError:
        console.print(f"[error]Load argument must be a number")



def check_markdown(args, bar, ingredient):
    if ingredient is None and len(args) == 0:
        console.print("[error]Invalid args. Use: 'markdown margarita', 'markdown beer', etc.")
    elif bar.menu.mark(direction="down", mark_arg=args[0]):
        return "markdown", args


def check_markup(args, bar, ingredient):
    if ingredient is None and len(args) == 0:
        console.print("[error]Invalid args. Use: 'markup margarita', 'markup beer', etc.")
    elif bar.menu.mark(direction="up", mark_arg=args[0]):
        return "markup", args


def check_new(args, bar, ingredient):
    bar_name = ""
    while bar_name == "":
        bar_name = console.input("Name your bar: > ")
        if bar_name not in utils.list_saves():
            return "new", [bar_name]
        else:
            console.print("[error]This bar name is already present in your save files.")


def check_remove(args, bar, ingredient):
    if ingredient is None and len(args) == 0:
        console.print("[error]Invalid args. Use: 'remove margarita', 'remove guinness', etc.")
    elif bar.menu.remove(args[0]):
        return "remove", args
# </editor-fold>
