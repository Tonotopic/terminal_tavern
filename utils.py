import math
import sys
import os
import pickle

import ingredients
import logger
from rich_console import console


def save_bar(bar_obj):
    """Saves the game state to a file.

    Args:
        bar_obj: The Bar object to save.
        filename: The name of the file to save to. Defaults to "save_game.pickle".
    """
    filename = bar_obj.name + ".pickle"
    with open(filename, "wb") as f:  # Open the file in binary write mode
        pickle.dump(bar_obj, f)  # Serialize and write the Bar object to the file
        msg = f"Game saved as {filename}"
        console.print(msg)
        logger.log(msg)


def list_saves():
    file_names = [save_file for save_file in os.listdir() if save_file.endswith(".pickle")]
    return file_names


def load_bar(index):
    """Loads the game state from a file.

    Returns:
        The loaded Bar object, or None if loading fails.
    """
    filename = list_saves()[index]
    try:
        with open(filename, "rb") as f:
            bar_obj = pickle.load(f)
            logger.log(f"Game loaded from {filename}")

            ingredients.load_ingredients_from_db()
            bar_obj.regen_recipes()

            return bar_obj
    except Exception as e:
        console.print(f"Error loading save file: {e}")
        return None


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
