import math
import os
import pickle
import random
import sys

from display.rich_console import console
from utility import logger

current_bar = None


# <editor-fold desc="Savefiles">
def save_bar(bar_obj):
    """Saves the game state to a file.

    Args:
        bar_obj: The Bar object to save.
        filename: The name of the file to save to. Defaults to "save_game.pickle".
    """
    filename = bar_obj.bar_stats.bar_name + ".pickle"
    with open(filename, "wb") as f:  # Open the file in binary write mode
        pickle.dump(bar_obj, f)  # Serialize and write the Bar object to the file
        logger.logprint(f"Game saved as {filename}")


def list_saves():
    """Returns a list of save file names in the directory."""
    file_names = [save_file for save_file in os.listdir() if save_file.endswith(".pickle")]
    return file_names


def load_bar(index):
    """
    Loads the game state (bar) from the file at the given index of the save list.

    :param index: The desired file's index in list_saves()
    :return: The loaded Bar object, or None if loading fails.
    """
    global current_bar
    filename = list_saves()[index]
    with open(filename, "rb") as f:
        current_bar = pickle.load(f)
        logger.log(f"Game loaded from {filename}")

        current_bar.reload_ingredients()

        return current_bar


# </editor-fold>

def format_a(following_string: str):
    """Determines whether "a" or "an" should be printed depending on the following word."""
    if following_string.lower()[0] in "aeiou" or following_string.startswith("herb"):
        return "an"
    else:
        return "a"

def debugging():
    """Returns True if running in the PyCharm debugger."""
    from sys import gettrace
    if gettrace():
        return True
    elif sys.monitoring.get_tool(sys.monitoring.DEBUGGER_ID) is not None:
        return True
    else:
        return False


def quit():
    """Exit the application."""
    logger.log("Received quit command. Exiting...")
    print("Exiting...")
    sys.exit(0)


def split_with_quotes(inpt):
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

    return parts


def quarter_round(price):
    return math.ceil(price * 4) / 4


def roll_probabilities(choices):
    if isinstance(choices, dict):
        if isinstance(list(choices.values())[0], float):
            if not 0.99 < sum(choices.values()) < 1.01:
                logger.log("Probabilities do not sum to 1!")
            return random.choices(list(choices.keys()), weights=list(choices.values()))

    return random.choices(list(choices))[0]