from itertools import cycle
from typing import Callable, Optional

from pynput import keyboard
from rich.console import RenderableType
from rich.live import Live

from utility import logger
from display.rich_console import console

live_prompt = "Cycling multiple pages... Begin typing to stop."


class _TrackedLive:
    """Record the last renderable sent to Live while preserving Live's update API."""

    def __init__(self, live: Live) -> None:
        self.live = live
        self.latest_renderable: Optional[RenderableType] = None

    def update(self, renderable: RenderableType, *, refresh: bool = False) -> None:
        self.latest_renderable = renderable
        self.live.update(renderable, refresh=refresh)

    def refresh(self) -> None:
        self.live.refresh()


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
    # Effective height for layouts is normally lowered by 1 to make room for the prompt.
    # "Cycling multiple pages[...]" is part of layout, not a prompt, so layout needs to take the whole screen again

    tracked_live: Optional[_TrackedLive] = None

    try:
        with Live(console=console, auto_refresh=False, screen=True) as live:
            # Tracks the state of the live display mode to return to post-pause
            tracked_live = _TrackedLive(live)
            logger.log("Drawing live display...")

            global draw_sentinel
            draw_sentinel = False

            def stop_display():
                global draw_sentinel
                draw_sentinel = True
                logger.log("Stopping live display.")

            while not draw_sentinel:
                update_function(stop_display, tracked_live)
                tracked_live.refresh()
                listen(sec=sec)

        if (
            tracked_live is not None
            and tracked_live.latest_renderable is not None
        ):
            console.print(tracked_live.latest_renderable)
    finally:
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
