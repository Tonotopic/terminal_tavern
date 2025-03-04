import re
from typing import Iterable

import rich.box
from rich.panel import Panel
from unidecode import unidecode

from data import ingredients
from display.rich_console import console
from interface import ui
from recipe import Recipe
from utility import utils, logger

persistent_commands = {"shop", "menu"}
help_panels = {
    "help": f"Syntax: [cmd]'help \\[term]'[/cmd]\n"
            f"[cmd]'Help'[/cmd] can be used on commands (shop, add, etc), products (lychee, Ketel One Classic, etc), "
            f"and some game concepts (input, recipe, etc).\n"
            f"Command parsing will work the same for the help arg, i.e. [cmd]'help fish pois'[/cmd]"
            f" can return the description for [italic][beer]Little Fish Saison du Poisson.[/italic][/beer]",

    "input/commands": f"Input parsing is [highlight]case-insensitive[/highlight] and allows for partial terms - "
             f"[cmd]'rh b f h'[/cmd] is as effective as 'Rhinegeist Beer for Humans', and in the right context, "
             f"[cmd]'sh'[/cmd] will work as effectively as [cmd]'shop'[/cmd].\n\n"
             f"An input of 3 or fewer characters will [highlight]priority match to the beginning[/highlight] of the term.\n"
             f"Generally, when partial input matches to multiple currently valid commands, "
             f"a message will print listing all matching commands, and the previous prompt will loop.\n\n"
             f"In cases where one valid command entirely contains another, i.e. [cmd]'lemonade'[/cmd] and [cmd]'lemon'[/cmd], "
             f"or [cmd]'Crown Royal Black'[/cmd] and [cmd]'Crown Royal Blackberry'[/cmd], the [highlight]most base command[/highlight] will be favored.\n\n"
             f"Mid-word matches are allowed in most cases ([cmd]'berri'[/cmd] can return [cmd]'Raspberri'[/cmd]), and words may be skipped ([cmd]'capy pun'[/cmd] can return [beer]Urban Artifact Capy Snacks Fruit Punch[/beer]).",

    # <editor-fold desc="Game Concepts">
    "recipe": f"[highlight]Recipes[/highlight], the backbones of [cocktails]Cocktails[/cocktails], are made up of [highlight]Ingredients[/highlight], "
              f"which may be spirits, liqueurs, syrups, fruits, spices, etc. as well as beer, wine, cider, and mead.\n"
              f"View your bar's drink [cmd]'menu'[/cmd], [cmd]'add cocktail'[/cmd], and create a [cmd]'new'[/cmd] cocktail to write a recipe.\n"
              f"You do [italic]not[/italic] need to have the ingredients in your inventory to write a new recipe.\n"
              f"[cmd]'Help cocktails'[/cmd] to view more on cocktails.",

    "price/pricing": f"A menu item's [highlight]price[/highlight] before [highlight]markup[/highlight] is based on its per-unit cost to you.\n\n"
             f"For cocktails:\n"
             f"[money]$4.50[/money] for drinks costing you less than [money]$1.50[/money] wholesale, \n"
             f"3x wholesale costs between [money]$1.50[/money] and [money]$4.00[/money], \n"
             f"or 2.5x wholesale costs over [money]$4.00[/money].\n\n"
             "For other drinks:\n"
             f"[money]$3.75[/money] for drinks costing you less than [money]$1.25[/money] wholesale, \n"
             f"3x wholesale costs between [money]$1.25[/money] and [money]$3.00[/money], \n"
             f"or 2x wholesale costs over [money]$3.00[/money].\n\n"
             f"[highlight]Markup[/highlight] or [highlight]markdown[/highlight] can then be applied per-item.",
    # </editor-fold>

    # <editor-fold desc="Commands">
    "shop": f"[cmd]'Shop'[/cmd] allows you to view available products by type, as well as to view your bar's stock in each section.\n"
            f"Type the name of a category or product from the current section (i.e. 'drinks', 'jameson') to view.\n"
            f"[cmd]'Shop'[/cmd] again to exit. [cmd]'Back'[/cmd] to go back to the parent category.\n"
            f"While viewing a product, [cmd]'buy \\[volume]'",

    "menu": f"[cmd]'Menu'[/cmd] shows the expanded drink menu currently made available at your bar, and allows you to manage it.\n\n"
            f"From the menu overview, type a category (i.e. beer) to expand the category.\n\n"
            f"[cmd]'Add \\[type]'[/cmd], i.e. [cmd]'add cocktail'[/cmd], to view drinks that can be added to the menu, "
            f"or additionally for cocktails, to create a new recipe.\n"
            f"[cmd]'Remove \\[item]'[/cmd] to remove an item from the menu. Cocktail recipes will not be lost.\n\n"
            f"[cmd]'markup \\[item]'[/cmd] and [cmd]'markdown \\[item]'[/cmd] work slightly differently; [cmd]'help markup'[/cmd] to read more.",

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


def draw_help_panel(term):
    """Prints a panel to the user containing help info for the given term."""
    logger.log("Drawing help panel for " + term)
    panel = Panel(help_panels.get(term), title=f"Help: {term}", box=rich.box.ASCII2,
                  style=console.get_style("highlight"), width=100)
    console.print(panel)


def items_to_commands(lst: Iterable, plural_types=True):
    """
    Converts a list of ingredients, ingredient types, and/or strings into a list of commands for parsing.

    :param lst: List of ingredient objects
    :param plural_types: Whether types should be pluralized, i.e. Liqueurs, Lagers
    :return: A set of command strings to match input to
    """
    commands = set("")
    for entry in lst:
        if isinstance(entry, type):
            obj = entry()
            commands.add(unidecode(obj.format_type(plural=plural_types).lower()))
        elif isinstance(entry, ingredients.Ingredient):
            commands.add(unidecode(entry.name.lower()))
        elif isinstance(entry, str):
            commands.add(entry.lower())
        elif isinstance(entry, Recipe):
            commands.add(entry.name.lower())

    return commands


def command_to_item(cmd, lst, plural=False):
    """
    Matches a string command to an ingredient or type from the given list.
    :param cmd: Full command string
    :param lst: Reference list of types, ingredients, recipes, and/or strings
    :param plural: Whether type names are plural.
    :return: The matching item, if found.
    """
    if cmd is None:
        return None
    for entry in lst:
        if isinstance(entry, type):
            if entry == Recipe:
                if cmd == "cocktails":
                    return Recipe
            elif f"{unidecode(entry().format_type(plural).lower())}" == cmd:
                return entry
        elif isinstance(entry, ingredients.Ingredient):
            if cmd == unidecode(entry.name.lower()):
                return entry
        elif isinstance(entry, Recipe):
            if cmd == unidecode(entry.name.lower()):
                return entry
        elif isinstance(entry, str):
            if cmd == entry.lower():
                return entry
        else:
            console.print("[error]command_to_item argument not registering as type or Ingredient")
    return None


def find_command(inpt, commands=None, force_beginning=False, feedback=True):
    """
    Takes an input string and a command list, and either returns a single command match,
    prints multiple matching commands for the user to choose between,
    or prints all valid commands if no valid command is found.

    :param inpt: The string from user input.
    :param commands: Optional list of commands to match to.
    :param force_beginning: Can be set to True to disallow matching to the middle of a command.
    :param feedback: Whether to print the result to the user.
    """
    # Because "jose" and "silver" on their own will both return multiple products
    # Currently entire input match must be sequential so "especial silver" or "ial sil" is required
    inpt = inpt.strip().lower()

    # <editor-fold desc="Splitting logic allowing for spaces in quotes">
    parts = utils.split_with_quotes(inpt)
    primary_command = parts[0]

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
        remaining_command = command
        while matching:
            if len(input_words) > len(command.split()):
                matching = False
                break
            for input_word in input_words:
                if not matching:
                    break
                inpt_word_has_match = False
                for cmd_word in remaining_command.split():
                    if len(input_word) < 4 or force_beginning:
                        if cmd_word.startswith(input_word):
                            inpt_word_has_match = True
                            try:
                                remaining_command = command.split(cmd_word)[1]
                            except IndexError:
                                remaining_command = command.split(cmd_word)[0]
                            break
                    else:
                        pattern = r"\s*".join(input_word)
                        if re.search(pattern, cmd_word):
                            inpt_word_has_match = True
                            break
                if not inpt_word_has_match:
                    matching = False
                    break
            if matching:
                matching_commands.append(command)
                break

    # Mid-word matching - If it hasn't already matched to startswith, match to any part of commands
    if not matching_commands:
        for command in sorted_commands:
            matching = True
            remaining_command = command
            while matching:
                if len(input_words) > len(command.split()):
                    matching = False
                for input_word in input_words:
                    if not matching:
                        break
                    inpt_word_has_match = False
                    for cmd_word in remaining_command.split():
                        if len(input_word) < 3:
                            if cmd_word.startswith(input_word):
                                inpt_word_has_match = True
                                try:
                                    remaining_command = command.split(f"{cmd_word} ")[1]
                                except IndexError:
                                    remaining_command = command.split(cmd_word)[0]
                                break
                        else:
                            pattern = r"\s*".join(input_word)
                            if re.search(pattern, cmd_word):
                                inpt_word_has_match = True
                                break
                    if not inpt_word_has_match:
                        matching = False  # If there's an input word with no match in the command, it's not this command
                        break
                if matching:  # After all input words, there are none that don't match the command
                    matching_commands.append(command)
                    break

    # </editor-fold>

    if feedback:
        logger.log(f"'{inpt}' cmd matches: {matching_commands}")

    if len(matching_commands) == 1:
        # found 1 match
        if len(parts) > 1:  # If arguments are present along the primary command
            return matching_commands[0], parts[1:]
        else:
            return matching_commands[0]
    elif len(matching_commands) == 0:
        if len(sorted_commands) <= 15:
            if feedback:
                logger.logprint(f"[error]Valid commands: {sorted_commands}")
        else:
            if feedback:
                console.print(f"[error]No matching term found for [cmd]{inpt}")
                logger.log(f"Valid commands: {sorted_commands}")
        return None
    elif len(matching_commands) > 1:  # found more than one match
        min_length = 20
        most_base_cmd = None
        # Get shortest matching command
        for cmd in matching_commands:
            if len(cmd) < min_length:
                min_length = len(cmd)
                most_base_cmd = cmd
        # Check if all command matches contain the shortest
        if most_base_cmd:
            all_cmds_contain_base = True
            for cmd in matching_commands:
                if most_base_cmd not in cmd:
                    all_cmds_contain_base = False
        else:
            all_cmds_contain_base = False

        if all_cmds_contain_base:
            logger.log("Most base command: " + most_base_cmd)
            return most_base_cmd
        else:
            if feedback:
                logger.logprint(f"Matching commands : {matching_commands}")


def parse_input(prompt=None, commands=None, force_beginning: bool = False, inpt=""):
    """
    Gather, standardize, and validate input, handling multi-word logic and distinguishing primary commands from arguments.

        Args:
          :param prompt: Message printed just before the user's input cursor in the console.
          :param commands: Optional list of commands to pass to find_command.
          :param force_beginning: Can be set to True to disallow matching to the middle of a command.
        """
    while inpt == "":
        inpt = console.input(f"[prompt]{prompt}:[/prompt][white] > ").strip().lower()

    # TODO: As commands with args are added, skip them here
    # If not a command with args, group spaced words together
    parts = inpt.split()
    arg_commands = ["shop", "buy", "add", "remove", "load", "markup", "markdown"]  # help is added by find_command
    current_arg_cmds = []
    for arg_cmd in arg_commands:
        if arg_cmd in commands:
            current_arg_cmds.append(arg_cmd)

    arg_cmd = find_command(inpt=parts[0], commands=current_arg_cmds, feedback=False)
    while True:
        if arg_cmd is None and not inpt.startswith('"'):
            inpt = f'"{inpt}"'
        elif len(parts) > 1 and not parts[1].startswith('"'):
            parts[1] = '"' + parts[1]
            parts[len(parts) - 1] = parts[len(parts) - 1] + '"'
            inpt = " ".join(parts)

        inpt_cmd = find_command(inpt=inpt, commands=commands, force_beginning=force_beginning)

        # Start over parsing with input wrapped in quotes if the potential arg command we detected isn't accurate
        if arg_cmd:
            if inpt_cmd is None or inpt_cmd[0] != arg_cmd:
                arg_cmd = None
                inpt = inpt.replace('"', "")
                continue

        if isinstance(inpt_cmd, tuple):  # If find_command returned args
            primary_command, args = inpt_cmd  # Unpack the tuple
            for i, arg in enumerate(args):
                try:
                    int(arg)
                except ValueError:
                    args[i] = f'"{arg}"'

        else:
            primary_command = inpt_cmd  # The entire input is one part
            args = []

        return primary_command, args


def input_loop(prompt: str, commands, force_beginning=False, skip: str = None, ingredient=None, bar=None):
    """
    Loops the prompt checking for the success of certain commands so feedback can be shown without
    re-drawing the entire screen.

    :param prompt: Message printed just before the user's input cursor in the console.
    :param commands: Optional list of commands to pass to find_command.
    :param force_beginning: Can be set to True to disallow matching to the middle of a command.
    :param skip: This command's checker will not be called, e.g. distinguishing "new" cocktail from "new" game
    :param ingredient: Current context ingredient/type where needed for command checkers.
    :param bar: Current context bar where needed for command checkers.
    :return: The primary command and any args, whether or not a command checker has executed
    """
    while True:
        inpt = parse_input(prompt=prompt, commands=commands, force_beginning=force_beginning)
        if inpt[0] is None:
            continue
        primary_cmd, args = inpt

        if primary_cmd == "quit":
            if bar:
                bar.set_screen("main")
                utils.save_bar(bar)
            utils.quit()
        elif primary_cmd == "help":
            ingredient_cmds = items_to_commands(ingredients.all_ingredients)
            help_args = set(help_panels.keys()).union(ingredient_cmds)

            arg_input = " ".join(args)
            if arg_input == "":
                draw_help_panel("help")
                console.print(f"Help topics: {list(help_panels.keys())}")
                continue

            if not arg_input.startswith('"'):
                arg_input = f'"{arg_input}"'
            arg = find_command(arg_input, help_args)
            if arg in help_panels.keys():
                draw_help_panel(arg)
                continue
            elif arg in ingredient_cmds:
                arg_ing = command_to_item(cmd=arg, lst=ingredients.all_ingredients)
                console.print(arg_ing.description())
                continue
        elif callable(globals().get("check_" + primary_cmd)):
            if primary_cmd == skip:
                return primary_cmd, args
            result = globals().get("check_" + primary_cmd)(args, bar, ingredient)
            if result is not None:
                return result
            else:
                continue
        else:
            return primary_cmd, args

        # <editor-fold desc="Command Functions">


# <editor-fold desc="Input Loop Command Checkers">
def check_add(args, bar, ingredient):
    """
    Interprets the argument and attempts the process of adding an item to the menu.

    :param args: Section/type argument
    :param bar: Current context bar.
    :param ingredient: Type being viewed in the menu, if not all. Makes "add" work with no args.
    :return: "add" and args if item added to menu, else None
    """
    if ingredient is None and len(args) == 0:
        logger.logprint("[error]Invalid args. Use: 'add cocktail', 'add beer', etc.")
        return None
    type_displaying = ingredient
    if type_displaying is None:
        typ = command_to_item(find_command(args[0], ["cocktails", "beers", "ciders", "wines", "meads"]),
                              [Recipe, ingredients.Beer, ingredients.Cider, ingredients.Wine, ingredients.Mead],
                              plural=True)
        if bar.menu.select_to_add(typ):
            return "add", args
    else:
        if bar.menu.select_to_add(type_displaying):
            return "add", args


def check_buy(args, bar, ingredient):
    """
    Checks the success of the buy command, for use in the input loop.

    :param args: User's input for the volume option to buy.
    :param bar: Current context bar.
    :param ingredient: The ingredient object being purchased.
    :return: "buy" and args if purchase successful, else None
    """
    if len(args) > 0:
        if bar.stock.buy(ingredient=ingredient, arg=args[0]):
            return "buy", args
    else:
        logger.logprint("[error]Incorrect number of arguments. Usage: buy <quantity>")


def check_load(args, bar, ingredient):
    """
    Validates input for loading a game.

    :param args: String of user input for save slot number
    :return: "load" and args
    """
    try:
        if len(utils.list_saves()) < int(args[0]):
            console.print(f"[error]There are only {len(utils.list_saves())} save files to load from.")
        else:
            return "load", args
    except IndexError:
        msg = "[error]Syntax: 'load \\[num]'"
        logger.log("IndexError :" + msg)
        console.print(msg)
    except ValueError:
        logger.logprint("[error]Load argument must be a number")


def check_markdown(args, bar, ingredient):
    """
    Attempts to mark down a menu item or section, checking the result.

    :param args: User input for ingredient/section to mark down
    :param bar: Current context bar.
    :return: "markdown" and args if markdown successful, else None
    """
    if ingredient is None and len(args) == 0:
        logger.logprint("[error]Invalid args. Use: 'markdown margarita', 'markdown beer', etc.")
    elif bar.menu.mark(direction="down", mark_arg=args[0]):
        return "markdown", args


def check_markup(args, bar, ingredient):
    """
    Attempts to mark up a menu item or section, checking the result.

    :param args: User input for ingredient/section to mark up
    :param bar: Current context bar.
    :return: "markup" and args if markup successful, else None"""
    if ingredient is None and len(args) == 0:
        logger.logprint("[error]Invalid args. Use: 'markup margarita', 'markup beer', etc.")
    elif bar.menu.mark(direction="up", mark_arg=args[0]):
        return "markup", args


def check_new(args, bar, ingredient):
    """Validates bar name input."""
    console.print()
    bar_name = ""
    while bar_name == "":
        bar_name = console.input("[cmd]Name your bar:[/cmd] > ")
        if bar_name in "quit" or bar_name in "back":
            utils.quit()
    if bar_name not in utils.list_saves():
        return "new", [bar_name]
    else:
        console.print("[error]This bar name is already present in your save files.")


def check_open(args, bar, ingredient):
    """Ensures everything is in order to open the bar."""
    if bar.menu.check_stock():
        return "open", args


def check_remove(args, bar, ingredient):
    """
    Attempts to remove an item from the menu, checking the result.

    :param args: User input for item to remove.
    :param bar: Current context bar.
    :return: "remove" and args if an item is successfully removed, else None
    """
    if ingredient is None and len(args) == 0:
        console.print("[error]Invalid args. Use: 'remove margarita', 'remove guinness', etc.")
    elif bar.menu.remove(args[0]):
        return "remove", args


def check_shop(args, bar, ingredient):
    """
    Sets and initiates the shop screen, interpreting a type argument if present.

    :param args: Optional user input argument corresponding to an ingredient type, i.e. spices, Pale Ales
    :param bar: Current context bar
    :return: "shop" and args if arg recognized, else None
    """
    if len(args) > 0:
        all_ingredient_types = ingredients.all_ingredient_types()
        cmd_lst = [typ().format_type(plural=True).lower() for typ in all_ingredient_types]
        shop_arg = find_command(args[0], cmd_lst)
        if shop_arg:
            shop_typ = command_to_item(shop_arg, all_ingredient_types, plural=True)
            bar.set_screen("SHOP")
            ui.shop_screen(bar, shop_typ)
        else:
            return None
    else:
        bar.set_screen("SHOP")
        ui.shop_screen(bar)
    return "shop", args

# </editor-fold>
