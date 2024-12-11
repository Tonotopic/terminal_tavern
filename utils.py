import sys
import os
import pickle

from rich_console import console


def save_game(bar_obj):
    """Saves the game state to a file.

    Args:
        bar_obj: The Bar object to save.
        filename: The name of the file to save to. Defaults to "save_game.pickle".
    """
    filename = bar_obj.name + ".pickle"
    with open(filename, "wb") as f:  # Open the file in binary write mode
        pickle.dump(bar_obj, f)  # Serialize and write the Bar object to the file
        console.print(f"Game saved as {filename}")


def list_saves():
    file_names = [save_file for save_file in os.listdir() if save_file.endswith(".pickle")]
    return file_names


def load_game(index):
    """Loads the game state from a file.

    Returns:
        The loaded Bar object, or None if loading fails.
    """
    filename = list_saves()[index]
    try:
        with open(filename, "rb") as f:
            bar_obj = pickle.load(f)
            console.print(f"Game loaded from {filename}")
            return bar_obj
    except Exception as e:
        console.print(f"Error loading save file: {e}")
        return None


def quit():
    """Exit the application."""
    print("Exiting...")  # Optional: Print a message before exiting
    sys.exit(0)  # Terminate the application with exit code 0 (success)
