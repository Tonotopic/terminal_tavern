import logging
import datetime
import os
import sys
import traceback
import inspect
from logging.handlers import RotatingFileHandler


def filename():
    """Generates a filename with a timestamp."""
    now = datetime.datetime.now().strftime("%m-%d--%H-%M-%S")
    return os.path.join("logs", f"{now}.log")


def log(msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:12]
    logger.info(f"{timestamp} - {msg}")


def delete_oldest_log(log_dir, max_files):
    log_files = os.listdir(log_dir)
    log_files = [os.path.join(log_dir, f) for f in log_files]
    log_files.sort(key=lambda x: os.path.getmtime(x))
    if len(log_files) > max_files:
        os.remove(log_files[0])


def exception_handler(exc_type, exc_value, exc_traceback):
    tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.error(tb_str)

    # Extract the frame where the exception occurred
    tb = exc_traceback
    while tb.tb_next:
        tb = tb.tb_next
    frame = tb.tb_frame

    # Get local variables from the frame
    local_vars = frame.f_locals
    for var_name, var_value in local_vars.items():
        logger.error(f"  {var_name}: {var_value}")


if not os.path.exists("logs"):
    os.makedirs("logs")

filename = filename()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler(filename, maxBytes=10 * 1024 * 1024, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

sys.excepthook = exception_handler

delete_oldest_log("logs", 5)
