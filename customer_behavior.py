from math import exp

def _sigmoid(x):
    return 1 / (1 + exp(-x))

class CustomerBehavior:
    def __init__(self, customer):
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
            "favorite_type_variety": self.favorite_type_variety_score(),
            "low_prices": self.low_prices_score(),
            "events": self.events_score(),
            "bar_activities": self.bar_activities_score(),
        }

        logit = BASE + sum(WEIGHTS[k] * (scores[k] - 0.5) * 2 for k in WEIGHTS)
        return _sigmoid(logit)

    def chance_to_stay(self):
        BASE = 0.0  # once someone's in the door, default lean is mildly toward staying

        WEIGHTS = {
            "favorite_type_variety": 1.0,
            "drink_variety": 1.0,
            "new_options": 1.2,
            "events": 1.5,  # live activity in the moment matters a lot for "stay another 10 min"
            "bar_activities": 1.5,
        }

        scores = {
            "favorite_type_variety": self.favorite_type_variety_score(),
            "drink_variety": self.drink_variety(),
            "new_options": self.new_options_score(),
            "events": self.events_score(),
            "bar_activities": self.bar_activities_score(),
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
            "quality_per_cost": 1.5,
            "service": 2.5,  # heaviest weight = biggest swing either way
        }

        scores = {
            "favorite_type_variety": self.favorite_type_variety_score(),
            "drink_variety": self.drink_variety(),
            "drinks_rating": self.drinks_rating_score(),
            "new_options": self.new_options_score(),
            "quality_per_cost": self.quality_per_cost_score(),
            "service": self.service_score(),
        }

        # center each score at 0 (score of 0.5 contributes nothing)
        logit = BASE + sum(WEIGHTS[k] * (scores[k] - 0.5) * 2 for k in WEIGHTS)
        return _sigmoid(logit)
