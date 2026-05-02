import random

from rich.panel import Panel

import customer
import utility.clock
from display.rich_console import console
from utility import logger, utils

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

    def print_msg(self, msg, game_time=None):
        """
        Prints occupancy/customer events to the bar event log on the game screen, and to the logger file.

        :param game_time: The in-game time the message's timestamp will bear.
        :param msg: The message to send the player (and the logger).
        """
        if game_time:
            timestamp = utility.clock.print_time(game_time)
            msg = f"{timestamp}: {msg}"

        # Divide the message so it wraps when it reaches the panel's width
        line_width = int((console.width / 2) - 6) # Panel borders take up 6 characters' width
        lines = utils.split_with_markup(msg, line_width)
        # Print lines to game screen
        for line in lines:
            self.event_log.append(line)

        # Also print to the logger
        logger.log(msg)

    def event_log_panel(self):
        """
        Formats and returns the panel that shows the player everything that happens while the bar is open.

        :return: The panel object.
        """
        log_str = ""
        log_lines = self.event_log
        occupied_height = 5

        # Cut off old lines when the panel reaches capacity
        if len(self.event_log) > console.height - occupied_height:
            log_lines = self.event_log[-(console.height - occupied_height):]

        # Populate the string that will be printed with each line of text
        for line in log_lines:
            log_str = log_str + line + "\n"

        # TODO Why does adding border style cause the live display twitch?
        panel = Panel(title="Event Log", renderable=log_str, border_style=console.get_style("panel"))
        return panel

    def check_customer_events(self, game_time):
        """
        Checks for prerequisite conditions, and if indicated, triggers customers entering, ordering, and leaving.

        :param game_time: The current in-game time.
        """
        def check_customer_entry():
            """Triggers customers to enter based on how long it's been since the last customers entered."""
            global last_entry_time
            #
            if not last_entry_time:
                self.enter_customer_group(game_time)
                last_entry_time = game_time
            elif game_time > last_entry_time + 20:
                self.enter_customer_group(game_time)
                last_entry_time = game_time

        def check_customer_orders():
            """Triggers orders from customers based on when they ordered their last round."""
            for group in self.current_customer_groups:
                # Order the first round 5 minutes in
                if group.last_round is None:
                    ref_time = group.arrival + 5
                # Order subsequent rounds ~30min apart
                else:
                    ref_time = group.last_round + 30
                if game_time > ref_time:
                    group.order_round(self.bar, game_time)
                    group.last_round = game_time

        def check_customers_leaving():
            """Triggers customers to leave based on how long they've been in the bar."""
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
                    self.print_msg(log_msg, game_time)

            for group_leaving in groups_leaving:
                self.current_customer_groups.remove(group_leaving)

        check_customer_entry()
        check_customer_orders()
        check_customers_leaving()

    def current_customers(self):
        """Returns a list of all customers currently in the bar."""
        customers = []
        for group in self.current_customer_groups:
            for cstmr in group.customers:
                customers.append(cstmr)

        return customers

    def print_customers(self):
        """Prints a naturally readable string of the current customers' names."""
        string = ""
        for cstmr in self.current_customers():
            string = string + cstmr.format_name() + ", "
        return string[:-2]

    def get_customer(self, name):
        """Gets a customer by their name."""
        name = name.lower()
        for cstmr in self.current_customers():
            if name == cstmr.name.lower():
                return cstmr

    def new_group_id(self):
        """Handles the assignment of IDs to customer groups."""
        group_id = self.group_id_counter
        self.group_id_counter += 1
        return group_id

    def enter_customer_group(self, game_time):
        # Chances for different group sizes to spawn
        group_sizes = {1: 4,
                       2: 2.5,
                       3: 2,
                       4: 0.5,
                       5: 0.025,
                       6: 0.025}
        headcount = random.choices(list(group_sizes.keys()), weights=list(group_sizes.values()))[0]

        new_customers = True
        if len(self.bar.bar_stats.past_customers) >= 6 and random.randrange(3) > 2: # 1/3 will be returning customers
            new_customers = False

        log_msg = f"[attn]New customers enter![/attn] - " if new_customers \
            else f"[attn]Repeat patrons enter![/attn] - "

        # TODO: Repeat patrons
        # Create new customers
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
        self.print_msg(log_msg, game_time)
