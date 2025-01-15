import time

from display.live_display import draw_live


def clock_time(current_game_mins):
    clock_hours = (current_game_mins // 60) % 24
    clock_minutes = current_game_mins % 60
    return clock_hours, clock_minutes


def current_game_mins(start_game_mins):
    game_mins_per_sec = 1
    elapsed_real_secs = time.perf_counter() - start_real_time
    elapsed_game_mins = int(elapsed_real_secs * game_mins_per_sec)
    current_mins = start_game_mins + elapsed_game_mins
    return current_mins


def run_clock(bar, start_game_mins, clock_panel, layout):
    def start_clock():
        global start_real_time
        start_real_time = time.perf_counter()

    def update_play_layout(stop_func, live):
        def update_clock():
            current_mins = current_game_mins(start_game_mins)
            clock_hours, clock_minutes = clock_time(current_mins)

            clock_panel.renderable = f"Sunday 01 Jan {clock_hours:02}:{clock_minutes:02}"
            live.update(layout, refresh=False)

            if clock_hours == "02":
                global day_ended
                day_ended = True
                stop_func()

        update_clock()
        bar.barspace.check_bar_events()
        layout["event_log"].update(bar.barspace.event_log_panel())

    global day_ended
    day_ended = False
    start_clock()
    draw_live(update_function=update_play_layout, sec=1)
