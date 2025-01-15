import random

from rich.panel import Panel

import customer
import display.rich_console
from utility.clock import current_game_mins

global last_entry_time
last_entry_time = None


# TODO: Much of this should probably be a bar_manager/floor_manager class
class BarSpace:
    def __init__(self, bar):
        self.bar = bar
        self.opening_time = 16 * 60
        self.current_customer_groups = set()
        self.event_log = []

        self.group_id_counter = 1

    def new_group_id(self):
        group_id = self.group_id_counter
        self.group_id_counter += 1
        return group_id

    def enter_customer_group(self):
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

        log_msg = f"New customers enter! - " if new_customers else f"Repeat patrons enter! - "

        customers = set()
        group_id = self.new_group_id()
        for i in range(headcount):
            cstmr = customer.create_customer()
            customers.add(cstmr)
            log_msg = log_msg + cstmr.name + ", "

        group = customer.CustomerGroup(group_id=group_id, customers=customers)
        group.arrival = current_game_mins(self.opening_time)

        self.current_customer_groups.add(group)
        self.event_log.append(log_msg[:-2])

    def check_bar_events(self):
        def check_customer_entry():
            global last_entry_time
            if not last_entry_time:
                last_entry_time = current_game_mins(self.opening_time)
            if current_game_mins(self.opening_time) > last_entry_time + 10:
                self.enter_customer_group()
                last_entry_time = current_game_mins(self.opening_time)

        def check_customer_orders():
            for group in self.current_customer_groups:
                if group.last_round is None:
                    ref_time = group.arrival + 5
                else:
                    ref_time = group.last_round + 15
                if current_game_mins(self.opening_time) > ref_time:
                    group.order_round(self.bar)
                    group.last_round = current_game_mins(self.opening_time)

        def check_customers_leaving():
            groups_leaving = set()
            for group in self.current_customer_groups:
                if current_game_mins(self.opening_time) > group.arrival + 30:
                    self.bar.bar_stats.past_customers[group.group_id] = group
                    groups_leaving.add(group)

                    log_msg = ""
                    if len(group.customers) > 1:
                        for cstmr in group.customers:
                            log_msg = log_msg + cstmr.name + ", "
                        log_msg = log_msg[:-2] + " are leaving the bar."
                    else:
                        log_msg = f"{group.customers[0].name} leaves the bar."
                    self.event_log.append(log_msg)

            for group_leaving in groups_leaving:
                self.current_customer_groups.remove(group_leaving)

        check_customer_entry()
        check_customer_orders()
        check_customers_leaving()

    def event_log_panel(self):
        log_str = ""
        for line in self.event_log:
            log_str = log_str + line + "\n"
        # TODO Why does adding border style cause the live display twitch?
        panel = Panel(title="Event Log", renderable=log_str, border_style=display.rich_console.styles.get("panel"))
        return panel
