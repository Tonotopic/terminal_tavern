from math import exp


def _sigmoid(x):
    return 1 / (1 + exp(-x))

class CustomerBehavior:
    def __init__(self, bar, customer):
        self.bar = bar
        self.customer = customer

    def chance_to_come_in(self):
        BASE = -0.5  # baseline log-odds at all-mediocre inputs

        WEIGHTS = {
            "favorite_type_variety": 1.0,
            "low_prices": 2.0,
            "events": 1.8,
            "bar_activities": 1.2,
        }

        scores = {
            "favorite_type_variety": self.bar.bar_stats.variety_of_type(self.customer.drink_pref),
            "low_prices": self.bar.bar_stats.price_score()
            #"events":
            #"bar_activities":
        }

        logit = BASE + sum(WEIGHTS[k] * (scores[k] - 0.5) * 2 for k in WEIGHTS)
        return _sigmoid(logit)

    def chance_to_stay(self):
        BASE = 0.0  # once in the door, default leans slightly toward staying

        WEIGHTS = {
            "favorite_type_variety": 1.0,
            "drink_variety": 1.0,
            "new_options": 1.2,
            "events": 1.5,
            "bar_activities": 1.5,
        }

        scores = {
            "favorite_type_variety": self.bar.bar_stats.variety_of_type(self.customer.drink_pref),
            "drink_variety": self.bar.bar_stats.drink_variety(),
            #"new_options":
            #"events":
            #"bar_activities":
        }

        logit = BASE + sum(WEIGHTS[k] * (scores[k] - 0.5) * 2 for k in WEIGHTS)
        return _sigmoid(logit)

    def chance_to_return(self):
        BASE = -0.5  # baseline log-odds when everything is mediocre (score ~0.5)

        WEIGHTS = {
            "favorite_type_variety": 1.2,
            "drink_variety": 1.0,
            "drinks_rating": 2.0,
            "new_options": 1.0,
            "quality": 1.5,
            "service": 2.5,
        }

        scores = {
            "favorite_type_variety": self.bar.bar_stats.variety_of_type(self.customer.drink_pref),
            "drink_variety": self.bar.bar_stats.drink_variety(),
            #"drinks_rating":
            #"new_options":
            "quality": self.customer.score_menu_quality()
            #"service":
        }

        # center each score at 0 (score of 0.5 contributes nothing)
        logit = BASE + sum(WEIGHTS[k] * (scores[k] - 0.5) * 2 for k in WEIGHTS)
        return _sigmoid(logit)
