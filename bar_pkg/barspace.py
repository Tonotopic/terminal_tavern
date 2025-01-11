class BarSpace:
    def __init__(self, bar):
        self.bar = bar
        self.current_customers = set()
        self.event_log = []

    def enter_customer(self, customer):
        self.current_customers.add(customer)
        new_customer = False
        if customer not in self.bar.bar_stats.past_customers:
            self.bar.bar_stats.past_customers.append(customer)
            new_customer = True

        log_msg = f"New customer {customer.name} enters!" if new_customer else f"Patron {customer.name} enters!"
        self.event_log.append(log_msg)

    def print_event_log(self):
        log_str = ""
        for line in self.event_log:
            log_str = log_str + line + "\n"
        return log_str
