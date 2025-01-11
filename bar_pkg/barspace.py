import random

import customer
import utility.clock

global last_entry_time
last_entry_time = None


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

        group = customer.CustomerGroup(group_id, customers)
        group.arrival = utility.clock.current_game_mins(self.opening_time)

        self.current_customer_groups.add(group)
        self.event_log.append(log_msg[:-2])

    def check_bar_events(self, current_game_mins):
        def check_customer_entry():
            global last_entry_time
            if not last_entry_time:
                last_entry_time = current_game_mins
            if current_game_mins > last_entry_time + 5:
                self.enter_customer_group()
                last_entry_time = current_game_mins

        def check_customers_leaving():
            groups_leaving = set()
            for group in self.current_customer_groups:
                if utility.clock.current_game_mins(self.opening_time) > group.arrival + 10:
                    self.bar.bar_stats.past_customers[group.group_id] = group
                    groups_leaving.add(group)

                    log_msg = ""
                    for cstmr in group.customers:
                        log_msg = log_msg + cstmr.name + ", "
                    log_msg = log_msg[:-2] + " are leaving the bar!"
                    self.event_log.append(log_msg)

            for group_leaving in groups_leaving:
                self.current_customer_groups.remove(group_leaving)

        check_customer_entry()
        check_customers_leaving()


    def print_event_log(self):
        log_str = ""
        for line in self.event_log:
            log_str = log_str + line + "\n"
        return log_str
