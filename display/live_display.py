import time
from itertools import cycle
from typing import Callable

from pynput import keyboard
from rich.live import Live

from utility import logger
from display.rich_console import console

live_prompt = "Cycling multiple pages... Begin typing to stop."


def bump_console_height(down=False):
    """
    Change console height by 1, affecting how Layouts are drawn.
    :param down: Leave False to increase height, set to True to decrease height again
    """
    width, height = console.size
    if down:
        height = height - 1
    else:
        height = height + 1
    console.size = (width, height)


def draw_sentinel_update(key):  # Unspecified key is used by listener below
    """Sets global sentinel to True to stop the cycling of the live display."""
    global draw_sentinel
    draw_sentinel = True
    raise keyboard.Listener.StopException()


def listen(sec: int):
    """Listens for a keypress for the given number of seconds after each live page has been drawn."""
    with keyboard.Listener(on_press=draw_sentinel_update) as listener:  # , suppress=True
        listener.join(sec)


def draw_live(update_function: Callable, sec):
    """
    Update a live display using the {update_function} every {sec} sec

    :param update_function: A callable that performs the display update. It should accept a 'stop' function
    :param sec: The number of seconds to wait in between display updates.
    """

    bump_console_height()
    with Live(console=console, refresh_per_second=0.00001) as live:
        logger.log("Drawing live display...")

        global draw_sentinel
        draw_sentinel = False

        def stop_display():
            global draw_sentinel
            draw_sentinel = True
            logger.log("Stopping live display.")

        while not draw_sentinel:
            update_function(stop_display, live)
            live.refresh()
            listen(sec=sec)

    bump_console_height(down=True)


def live_cycle_tables(tables, panel, layout, sec):
    """
        Cycles through rendering the given tables in the given panel, re-drawing the given Layout every {sec} seconds.

        :param tables: Iterable of multiple tables to cycle through displaying
        :param panel: The panel to render the tables in. This should be contained in the provided Layout object
        :param layout: The Layout object to refresh, which should include the panel whose renderable is being changed.
        :param sec: The number of seconds to hold each table on the screen.
        """
    table_iterator = cycle(tables)

    def update_table_display(stop_func, live):
        try:
            table = next(table_iterator)
            panel.renderable = table
            live.update(layout)
        except StopIteration:
            stop_func()

    draw_live(update_table_display, sec=sec)


def run_clock(start_game_mins, panel, layout):
    def start_clock():
        global start_real_time
        start_real_time = time.perf_counter()

    def update_clock(stop_func, live):
        game_mins_per_sec = 1
        elapsed_real_secs = time.perf_counter() - start_real_time
        elapsed_game_mins = int(elapsed_real_secs * game_mins_per_sec)
        current_game_mins = start_game_mins + elapsed_game_mins
        clock_hours = (current_game_mins // 60) % 24
        clock_minutes = current_game_mins % 60

        panel.renderable = f"In-game time: {clock_hours:02}:{clock_minutes:02}"
        live.update(layout, refresh=False)

        if clock_hours == "02":
            global day_ended
            day_ended = True
            stop_func()

    global day_ended
    day_ended = False
    start_clock()
    draw_live(update_function=update_clock, sec=1)


'''def run_clock(bar, start_game_mins, panel, layout):
    game_mins_per_sec = 1  # 1 min = 1 sec

    start_real_time = time.perf_counter()
    try:
        while True:
            elapsed_real_secs = time.perf_counter() - start_real_time
            elapsed_game_mins = int(elapsed_real_secs * game_mins_per_sec)

            current_game_mins = start_game_mins + elapsed_game_mins
            clock_hours = (current_game_mins // 60) % 24
            clock_minutes = current_game_mins % 60

            panel.renderable = f"In-game time: {clock_hours:02}:{clock_minutes:02}"

            time.sleep(1 / game_mins_per_sec)
    except KeyboardInterrupt:
        pass'''
