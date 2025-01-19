import datetime
import inspect
import logging
import os
import sys
import traceback
import types
from logging.handlers import RotatingFileHandler

from display.rich_console import console


# TODO: Rich logs

def filename():
    """Generates a filename with a timestamp."""
    now = datetime.datetime.now().strftime("%m-%d--%H-%M-%S")
    return os.path.join(logs_dir, f"{now}.log")


def log(msg):
    """Prints to log only with timestamp."""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:12]
    logger.info(f"{timestamp} - {msg}")


def logprint(msg):
    """Prints to the log and the console."""
    console.print(msg)
    log(msg)


def delete_oldest_log(log_dir, max_files):
    log_files = os.listdir(log_dir)
    log_files = [os.path.join(log_dir, f) for f in log_files]
    log_files.sort(key=lambda x: os.path.getmtime(x))
    if len(log_files) > max_files:
        os.remove(log_files[0])


def log_exception(exc_type, exc_value, exc_traceback):
    """Logs and prints traceback and locals when an exception is encountered."""
    console.print("[error]!!!!!!!!Exception encountered!!!!!!!!!!")
    tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logprint(tb_str)

    # Extract the frame where the exception occurred
    tb = exc_traceback
    while tb.tb_next:
        tb = tb.tb_next
    frame = tb.tb_frame

    # Get local variables from the frame
    logprint("[error]Locals:")

    local_vars = frame.f_locals
    for var_name, var_value in local_vars.items():
        try:
            if var_name.startswith("__") or isinstance(var_value, types.ModuleType):
                continue

            def is_ingredient(obj):
                for cls in inspect.getmro(type(obj)):
                    if cls.__name__ == "Ingredient":
                        return True

            def ing_name(obj):
                if hasattr(obj, "name"):
                    return obj.name
                else:
                    return obj.format_type()

            if isinstance(var_value, list) or isinstance(var_value, dict):
                locals_line = f"  [l]{var_name}[/l]: "
                for item in var_value:
                    if is_ingredient(item):
                        locals_line += f"{ing_name(item)}, "
                    else:
                        locals_line += str(var_value)
            else:
                if is_ingredient(var_value):
                    var_value = ing_name(var_value)
                locals_line = f"  [l]{var_name}[/l]: {var_value}"

            logger.error(locals_line)
            if len(locals_line) > 500:
                locals_line = locals_line[:500] + "..."
            console.print(locals_line)
        except Exception as e:
            console.print(e)
            continue


logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")  # Go up one directory, then into logs
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

filename = filename()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler(filename, maxBytes=10 * 1024 * 1024, backupCount=5)

logger.addHandler(file_handler)

sys.excepthook = log_exception

delete_oldest_log(logs_dir, 5)
