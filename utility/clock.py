import time

from display.live_display import draw_live

global game_mins_per_sec
game_mins_per_sec = 1


def clock_time(current_game_mins):
    clock_hours = (current_game_mins // 60) % 24
    clock_minutes = current_game_mins % 60
    return clock_hours, clock_minutes


def print_time(mins):
    tim = clock_time(mins)
    clock_hours, clock_minutes = tim
    return f"{clock_hours:02}:{clock_minutes:02}"


def current_game_mins(start_game_mins):
    global game_mins_per_sec
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

        def update_customer_count():
            layout["customers"].renderable.title = f"Customers ({bar.barspace.current_customer_count()})"
            layout["customers"].renderable.renderable = bar.barspace.print_customers()

        update_clock()
        bar.barspace.check_bar_events()
        update_customer_count()
        layout["event_log"].update(bar.barspace.event_log_panel())

    global day_ended
    day_ended = False
    start_clock()
    global game_mins_per_sec
    draw_live(update_function=update_play_layout, sec=1 / game_mins_per_sec)
