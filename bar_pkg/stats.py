from math import sqrt

from data.ingredients import Lager, IPA, Stout, SourAle, WheatBeer, Shandy, DoubleIPA, FruitTart, SparklingWine, Rose, \
    RedWine, WhiteWine, Brandy
from display import rich_console

class BarStats:
    def __init__(self, bar, bar_name, balance):
        self.bar = bar
        self.bar_name = bar_name
        self.balance = balance
        self.reputation = 0
        self.rep_level = 0
        self.past_customers = {}

    def drink_variety(self):
        def type_coverage():
            """Scores how many types of drink are on the menu (beer, wine, etc)."""
            TYPE_WEIGHTS = {
                "Cocktails": 0.35,
                "Beer": 0.20,
                "Wine": 0.20,
                "Cider": 0.15,
                "Mead": 0.10
            }
            score = 0
            menu = self.bar.menu
            for section in menu.list_menu_by_section():
                if len(section[0]) > 0:
                    score += TYPE_WEIGHTS[section[1]]
            return score

        def drinks_per_type():
            """Scores how many different drinks are on the menu of each type."""
            SOFT_MAXES = {
                "Cocktails": 12,
                "Beer": 10,
                "Wine": 6,
                "Cider": 2,
                "Mead": 2
            }
            types_being_evaluated = 0
            total_sqrts = 0
            for drink_type, soft_max in SOFT_MAXES.items():
                num_drinks = len(self.bar.menu.get_section(drink_type))
                if num_drinks > 0:
                    types_being_evaluated += 1
                    total_sqrts += sqrt(num_drinks / soft_max)

            return total_sqrts / types_being_evaluated if types_being_evaluated > 0 else 0

        def diversity_within_type():
            def cocktail_diversity():
                """Counts how many unique flavors are represented in the top 3 flavors of all cocktails."""
                flavors = set()
                for cocktail in self.bar.menu.get_section("Cocktails"):
                    for flavor in list(cocktail.taste_profile.keys())[:3]:
                        flavors.add(flavor)
                return len(flavors) / len(rich_console.taste_styles.keys())

            def beer_diversity():
                BEER_STYLE_TARGETS = [Lager, IPA, Stout, SourAle]
                BONUS_TARGETS = [WheatBeer, Shandy, DoubleIPA, FruitTart]
                covered = set()
                for beer_option in self.bar.menu.get_section("Beer"):
                    for target in BEER_STYLE_TARGETS + BONUS_TARGETS:
                        if isinstance(beer_option, target):
                            covered.add(target)
                return min(1.0, len(covered) / len(BEER_STYLE_TARGETS))

            def wine_diversity():
                WINE_STYLE_TARGETS = [RedWine, WhiteWine, SparklingWine, Rose]
                BONUS_TARGETS = [Brandy]
                covered = set()
                for beer_option in self.bar.menu.get_section("Wine"):
                    for target in WINE_STYLE_TARGETS + BONUS_TARGETS:
                        if isinstance(beer_option, target):
                            covered.add(target)
                return min(1.0, len(covered) / len(WINE_STYLE_TARGETS))

            types_being_evaluated = 0
            total_of_scores = 0
            if len(self.bar.menu.get_section("Cocktails")) > 0:
                types_being_evaluated += 1
                total_of_scores += cocktail_diversity()
            if len(self.bar.menu.get_section("Beer")) > 0:
                types_being_evaluated += 1
                total_of_scores += beer_diversity()
            if len(self.bar.menu.get_section("Wine")) > 0:
                types_being_evaluated += 1
                total_of_scores += wine_diversity()

            return total_of_scores / types_being_evaluated if types_being_evaluated > 0 else 0

        type_coverage = type_coverage()
        drinks_per_type = drinks_per_type()
        diversity_within_type = diversity_within_type()

        return min(1.0,
            type_coverage * 0.35 +
            drinks_per_type * 0.35 +
            diversity_within_type * 0.30
        )

