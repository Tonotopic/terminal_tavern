import datetime
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from rich.console import Console
from rich.highlighter import NullHighlighter
from rich.logging import RichHandler
from display.rich_console import console, theme


def get_filename():
    """Generates a filename with a timestamp."""
    now = datetime.datetime.now().strftime("%m-%d--%H-%M-%S")
    return os.path.join(logs_dir, f"{now}.log")


def delete_oldest_log(log_dir, max_files):
    log_files = [os.path.join(log_dir, f) for f in os.listdir(log_dir)]
    log_files.sort(key=os.path.getmtime)
    if len(log_files) > max_files:
        os.remove(log_files[0])


# <editor-fold desc="Setup Directories and Rotation">
logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(logs_dir, exist_ok=True)

log_path = get_filename()
file_handler = RotatingFileHandler(
    log_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
)

file_console = Console(
    file=file_handler.stream,
    theme=theme,
    width=140,
    force_terminal=True,
    color_system="256",
    highlight=False,  # disabling highlighting ensures the style of numbers is not overwritten to be uniform
)

rich_file_handler = RichHandler(
    console=file_console,
    markup=True,
    highlighter=NullHighlighter(),
    rich_tracebacks=True,
    tracebacks_show_locals=True,
)

rich_console_handler = RichHandler(
    console=console,
    markup=True,
    highlighter=NullHighlighter(),
    rich_tracebacks=True,
    tracebacks_show_locals=True,
)
rich_console_handler.setLevel(logging.WARNING)

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)
logger.addHandler(rich_file_handler)
logger.addHandler(rich_console_handler)
# </editor-fold>


# <editor-fold desc="Public Helper Functions">
def log(msg):
    """Logs to file only (RichHandler adds the timestamp automatically)."""
    logger.info(msg)


def logprint(msg):
    """Prints to the console AND logs to the file."""
    console.print(msg)
    logger.info(msg)


def log_exception(exc_type, exc_value, exc_traceback):
    """Logs and prints formatted Rich tracebacks with local variables."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical(
        "[error]!!!!!!!!Exception encountered!!!!!!!!!![/error]",
        exc_info=(exc_type, exc_value, exc_traceback),
    )
# </editor-fold>


sys.excepthook = log_exception
delete_oldest_log(logs_dir, 5)
