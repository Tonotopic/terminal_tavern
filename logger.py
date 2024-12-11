import os
import glob
import datetime

from rich_console import console

logs_folder = "logs"
if not os.path.exists(logs_folder):
    os.makedirs(logs_folder)


def rotate_logs():
    log_files = glob.glob("log_*.txt")
    if len(log_files) >= 3:
        oldest_file = min(log_files, key=os.path.getctime)
        os.remove(oldest_file)


def timestamp():
    return datetime.datetime.now().strftime("%m-%d_%H-%M-%S")


rotate_logs()

filename = os.path.join(logs_folder, f"log_{timestamp()}.txt")

log_file = open(filename, "a")


def log(message, log_locals=False):
    with console.capture() as capture:
        console.log(message, log_locals=log_locals)
    log_file.write(capture.get())


def close_log():
    log_file.close()
