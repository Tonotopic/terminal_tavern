import math
import os
import pickle
import random
import re
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

def debugging():
    """Returns True if running in the PyCharm debugger."""
    from sys import gettrace
    if gettrace():
        return True
    elif sys.monitoring.get_tool(sys.monitoring.DEBUGGER_ID) is not None:
        return True
    else:
        return False


def format_a(following_string: str):
    """Determines whether "a" or "an" should be printed depending on the following word."""
    if following_string.lower()[0] in "aeiou" or following_string.startswith("herb"):
        return "an"
    else:
        return "a"


def index_with_markup(string: str, no_markup_index: int):
    """
    Returns the index of the given marked-up string that corresponds with the given index in a no-markup version of the
    string. I.e. give a position in a plain string, get an index of the same actual char position in the marked-up string

    :param string: Marked-up string to find a corresponding index for
    :param no_markup_index: The target index in the no-markup/actual-appearance string
    :return: The corresponding char's index in the original marked-up string
    """
    no_markup_str = remove_markup(string)
    if len(no_markup_str) - 1 < no_markup_index:  # Index at end if shorter than index given
        no_markup_index = len(no_markup_str) - 1

    no_markup_counter = 0
    in_tag = False
    for markup_index, char in enumerate(string):
        if no_markup_counter >= no_markup_index:
            if string[markup_index] == no_markup_str[no_markup_index]:
                return markup_index
            else:
                logger.logprint("[error]Markup index char doesn't match no markup index char")

        if char == "[":
            in_tag = True
        elif char == "]":
            in_tag = False
        elif not in_tag:
            no_markup_counter += 1

    if string[markup_index] == no_markup_str[no_markup_index]:
        return markup_index
    else:
        logger.logprint("[error]Markup index char doesn't match no markup index char")


def numb_lines(string, line_width):
    line_width = int(line_width)
    string = remove_markup(string)
    if len(string) <= line_width:
        return 1
    else:
        remainder = string[line_width:]
        lines_in_remainder = numb_lines(remainder, line_width)
    return 1 + lines_in_remainder


def percentize(numbers: list | dict):
    if isinstance(numbers, list):
        total = sum(numbers)
        percents = [number / total for number in numbers]
    elif isinstance(numbers, dict):
        percents = {}
        total = sum(numbers.values())
        for number in numbers:
            percent = numbers[number] / total
            percents[number] = percent
    return percents


def quarter_round(price):
    return math.ceil(price * 4) / 4


def quit():
    """Exit the application."""
    logger.log("Received quit command. Exiting...")
    print("Exiting...")
    sys.exit(0)


def remove_markup(string):
    return re.sub(r"\[.*?\]", "", string)


def roll_probabilities(choices):
    if isinstance(choices, dict):
        if isinstance(list(choices.values())[0], float):
            if not 0.99 < sum(choices.values()) < 1.01:
                logger.log("Probabilities do not sum to 1!")
            return random.choices(list(choices.keys()), weights=list(choices.values()))[0]

    return random.choices(list(choices))[0]


def split_with_markup(string: str, line_width):
    """
    Splits string based on line width, handling lonely markup tags.

    :param string: Whole string to split
    :param line_width: Maximum length of each line
    :return: List of lines from the string
    """
    lines = []
    num_lines = numb_lines(string, line_width)
    if num_lines > 1:
        for line_num in range(num_lines):
            # Start line_num at 1, not 0, for comparison with num_lines
            line_num += 1

            # Split at end if shorter than max
            split_index = line_width if len(remove_markup(string)) > line_width else len(remove_markup(string)) - 1
            markup_split_index = index_with_markup(string, split_index)

            # Jump to end of markup on last line
            if line_num == num_lines and len(string) > markup_split_index:
                markup_split_index = len(string)

            # Backtrack to last space so no terms are cut off
            if markup_split_index < len(string) - 1:
                while True:
                    if string[markup_split_index] == " ":
                        break
                    markup_split_index -= 1

            cut_section = string[:markup_split_index]
            # Remainder for processing next
            string = string[markup_split_index:]

            all_tags = re.findall(r"\[[^]]*\]", cut_section)
            open_tags = {}

            tag_fixed_str = cut_section
            for tag in all_tags:
                if tag.startswith("[/"):  # Closing tag
                    tag_word = tag[2:-1]
                    if tag_word in open_tags and open_tags[tag_word] > 0:
                        open_tags[tag_word] -= 1  # Mark open tag as closed
                    else:  # If closing tag is unmatched
                        tag_fixed_str = f"[{tag_word}]" + tag_fixed_str  # Open tag to match
                elif tag.startswith("["):  # Opening tag
                    open_tags[tag[1:-1]] = open_tags.get(tag[1:-1], 0) + 1  # Mark open tag

            # Close tags left open
            for tag_word, count in open_tags.items():
                if count > 0:
                    tag_fixed_str = tag_fixed_str + f"[/{tag_word}]"
            lines.append(tag_fixed_str)
    else:
        lines.append(string)
    return lines


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
