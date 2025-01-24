import random

from rich.panel import Panel

import customer
import utility.clock
from utility import logger, clock, utils
from display.rich_console import console

# TODO: Multi-line log lines don't offset display properly

global last_entry_time
last_entry_time = None


class Occupancy:
    def __init__(self, bar):
        self.bar = bar
        self.opening_time = 16 * 60
        self.current_customer_groups = set()
        self.event_log = []
        self.customer_displayed = None

        self.group_id_counter = 1

    def log(self, game_time, msg):
        timestamp = utility.clock.print_time(game_time)
        # msg = timestamp + ": " + msg

        self.event_log.append(f"{timestamp}: {msg}")
        logger.log(msg)

    def event_log_panel(self):
        line_width = (console.width / 2) - 6
        log_str = ""
        log_lines = self.event_log
        occupied_height = 5

        if len(self.event_log) > console.height - occupied_height:
            log_lines = self.event_log[-(console.height - occupied_height):]

        for line in log_lines:
            log_str = log_str + line + "\n"
        # TODO Why does adding border style cause the live display twitch?
        panel = Panel(title="Event Log", renderable=log_str, border_style=console.get_style("panel"))
        return panel

    def check_bar_events(self, game_time):
        def check_customer_entry():
            global last_entry_time
            if not last_entry_time:
                self.enter_customer_group(game_time)
                last_entry_time = game_time
            elif game_time > last_entry_time + 20:
                self.enter_customer_group(game_time)
                last_entry_time = game_time

        def check_customer_orders():
            for group in self.current_customer_groups:
                if group.last_round is None:
                    ref_time = group.arrival + 5
                else:
                    ref_time = group.last_round + 30
                if game_time > ref_time:
                    group.order_round(self.bar, game_time)
                    group.last_round = game_time

        def check_customers_leaving():
            groups_leaving = set()
            for group in self.current_customer_groups:
                if game_time > group.arrival + 90:
                    self.bar.bar_stats.past_customers[group.group_id] = group
                    groups_leaving.add(group)

                    log_msg = ""
                    if len(group.customers) > 1:
                        for i, cstmr in enumerate(group.customers):
                            cstmr.times_visited += 1
                            if i == len(group.customers) - 1:
                                log_msg = log_msg + "and "
                            log_msg = "" + log_msg + cstmr.format_name()
                            if len(group.customers) > 2:
                                log_msg = log_msg + ", "
                            else:
                                log_msg = log_msg + " "
                        if len(group.customers) > 2:
                            log_msg = log_msg[:-2] + " "
                        log_msg = log_msg + "are leaving the bar."
                    else:
                        for cstmr in group.customers:
                            cstmr.times_visited += 1
                        log_msg = f"{next(iter(group.customers)).format_name()} leaves the bar."
                    self.log(game_time, log_msg)

            for group_leaving in groups_leaving:
                self.current_customer_groups.remove(group_leaving)

        check_customer_entry()
        check_customer_orders()
        check_customers_leaving()

    def current_customers(self):
        customers = []
        for group in self.current_customer_groups:
            for cstmr in group.customers:
                customers.append(cstmr)

        return customers

    def print_customers(self):
        string = ""
        for cstmr in self.current_customers():
            string = string + cstmr.format_name() + ", "
        return string[:-2]

    def get_customer(self, name):
        name = name.lower()
        for cstmr in self.current_customers():
            if name == cstmr.name.lower():
                return cstmr

    def new_group_id(self):
        group_id = self.group_id_counter
        self.group_id_counter += 1
        return group_id

    def enter_customer_group(self, game_time):
        group_sizes = {1: 4,
                       2: 2.5,
                       3: 2,
                       4: 0.5,
                       5: 0.025,
                       6: 0.025}
        headcount = random.choices(list(group_sizes.keys()), weights=list(group_sizes.values()))[0]

        new_customers = True
        if len(self.bar.bar_stats.past_customers) >= 6 and random.randrange(3) > 2:
            new_customers = False

        log_msg = f"[attention]New customers enter![/attention] - " if new_customers \
            else f"[attention]Repeat patrons enter![/attention] - "

        customers = set()
        group_id = self.new_group_id()
        for i in range(headcount):
            cstmr = customer.create_customer(bar=self.bar)
            customers.add(cstmr)
            if i == headcount - 1 and headcount > 1:
                log_msg = log_msg + "and "
            log_msg = log_msg + cstmr.format_name()
            if headcount > 2:
                log_msg = log_msg + ", "
            else:
                log_msg = log_msg + " "
        if headcount > 2:
            log_msg = log_msg[:-2]

        group = customer.CustomerGroup(group_id=group_id, customers=customers)
        group.arrival = game_time

        self.current_customer_groups.add(group)
        self.log(game_time, log_msg)
