from math import sqrt

from data.ingredients import Lager, IPA, Stout, SourAle, WheatBeer, Shandy, DoubleIPA, FruitTart, SparklingWine, Rose, \
    RedWine, WhiteWine, Brandy, Beer, Wine
from display import rich_console
from recipe import Recipe

# TODO: Stock amts can be negative

class BarStats:
    def __init__(self, bar, bar_name, balance):
        self.bar = bar
        self.bar_name = bar_name
        self.balance = balance
        self.reputation = 0
        self.rep_level = 0
        self.past_customers = {}

    def cocktail_diversity(self):
        """Counts how many unique flavors are represented in the top 3 flavors of all cocktails, out of all possible
        flavors."""
        flavors = set()
        for cocktail in self.bar.menu.get_section("Cocktails"):
            for flavor in list(cocktail.taste_profile.keys())[:3]:
                flavors.add(flavor)
        return len(flavors) / len(rich_console.taste_styles.keys())

    def beer_diversity(self):
        """Scores how well the beer selection covers the typical array of styles."""
        beer_style_targets = [Lager, IPA, Stout, SourAle]
        bonus_targets = [WheatBeer, Shandy, DoubleIPA, FruitTart]
        covered_base = set()
        covered_bonus = set()
        for beer_option in self.bar.menu.get_section("Beer"):
            for target in beer_style_targets:
                if isinstance(beer_option, target):
                    covered_base.add(target)
            for target in bonus_targets:
                if isinstance(beer_option, target):
                    covered_bonus.add(target)

        base_score = len(covered_base) / len(beer_style_targets)
        bonus_score = len(covered_bonus) / len(bonus_targets)
        return min(1.0, base_score + bonus_score * 0.2)  # bonus adds a small top-up, capped

    def wine_diversity(self):
        """Scores how many of the basic wine styles are covered on the menu."""
        wine_style_targets = [RedWine, WhiteWine, SparklingWine, Rose]
        bonus_targets = [Brandy]
        covered_base = set()
        covered_bonus = set()
        for wine_option in self.bar.menu.get_section("Wine"):
            for target in wine_style_targets:
                if isinstance(wine_option, target):
                    covered_base.add(target)
            for target in bonus_targets:
                if isinstance(wine_option, target):
                    covered_bonus.add(target)

    def drink_variety(self):
        """Scores the bar on various measures of diversity in drink options."""

        def drink_type_coverage():
            """Scores how many types of drink are on the menu (beer, wine, etc)."""
            core_weights = {
                "Cocktails": 0.23,
                "Beer": 0.16,
                "Wine": 0.11,
            }  # Sums to 0.50 - having the 3 common types = baseline
            bonus_weights = {
                "Cider": 0.33,
                "Mead": 0.17,
            }
            score = 0
            menu = self.bar.menu
            for section in menu.list_menu_by_section():
                if len(section[0]) > 0:
                    score += core_weights.get(section[1], 0)
                    score += bonus_weights.get(section[1], 0)
            return min(1.0, score)

        def drinks_per_type():
            """Scores how many different drinks are on the menu of each type."""
            soft_maxes = {
                "Cocktails": 12,
                "Beer": 10,
                "Wine": 6,
                "Cider": 2,
                "Mead": 2
            }
            types_being_evaluated = 0
            total_sqrts = 0
            for drink_type, soft_max in soft_maxes.items():
                num_drinks = len(self.bar.menu.get_section(drink_type))
                if num_drinks > 0:
                    types_being_evaluated += 1
                    total_sqrts += min(1.0, sqrt(num_drinks / soft_max))

            return total_sqrts / types_being_evaluated if types_being_evaluated > 0 else 0

        def diversity_within_type():
            """Combines cocktail, beer, and wine diversity."""
            types_being_evaluated = 0
            total_of_scores = 0
            if len(self.bar.menu.get_section("Cocktails")) > 0:
                types_being_evaluated += 1
                total_of_scores += self.cocktail_diversity()
            if len(self.bar.menu.get_section("Beer")) > 0:
                types_being_evaluated += 1
                total_of_scores += self.beer_diversity()
            if len(self.bar.menu.get_section("Wine")) > 0:
                types_being_evaluated += 1
                total_of_scores += self.wine_diversity()

            return total_of_scores / types_being_evaluated if types_being_evaluated > 0 else 0

        type_coverage = drink_type_coverage()
        per_type = drinks_per_type()
        within_type = diversity_within_type()

        return min(1.0,
            type_coverage * 0.35 +
            per_type * 0.35 +
            within_type * 0.30
        )

    def variety_of_type(self, drink_pref):
        """Retrieves the variety score of the given drink type."""
        diversity_by_type = {
            Recipe: self.cocktail_diversity,
            Beer: self.beer_diversity,
            Wine: self.wine_diversity,
        }
        scorer = diversity_by_type.get(drink_pref)
        return scorer() if scorer else 0.5

    def price_score(self):
        """Scores how favorably priced the bar's drinks are - based on markup over cost as a ratio, not raw dollar
        markup, so a fair markup on a cheap well drink and on an expensive premium spirit score are the same."""
        #TODO: Calibrate price scoring
        typical_markup_ratio = 3.5
        sensitivity = 0.15

        markup_ratios = []
        for section in self.bar.menu.list_menu_by_section():
            for item in section[0]:
                if item.cost > 0:
                    cost_value, _ = item.cost_value()
                    if cost_value:  # guards both None and 0
                        price = item.base_price()
                        markup_ratios.append(price / cost_value)

        if not markup_ratios:
            return 0.5

        avg_ratio = sum(markup_ratios) / len(markup_ratios)
        score = 0.5 - (avg_ratio - typical_markup_ratio) * sensitivity
        return max(0.0, min(1.0, score))

