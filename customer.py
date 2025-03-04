import random
from decimal import Decimal
from typing import Iterable

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

import recipe
from data import flavors, ingredients
from data.ingredients import list_ingredients, get_ingredient
from data.db_connect import get_connection, close_connection
from display.rich_console import console
from utility import utils
from utility import logger

connection = get_connection()
cursor = connection.cursor()
cursor.execute("SELECT * FROM customer_names")
rows = cursor.fetchall()
customer_names = {}
for row in rows:
    name, gender, tag_field = row
    customer_names[name] = {"gender": gender, "tag_field": tag_field}
close_connection(connection)

ratio_chances = {
    "order preferred drink type": {True: 0.75, False: 0.25}
}
prob_points = {
    "men order beer": 75,
    "women order beer": -75,
    "women order wine": 50,
    "people order wine": -20,
    "people order mead": -50,
}


class Customer:
    def __init__(self, bar):
        self.bar = bar
        self.name = None
        self.gender = None
        self.tags = set()

        self.drink_pref = None
        self.fav_spirit = None
        self.fav_tastes = set()
        self.fav_ingreds = set()
        self.fav_keywords = set()

        self.revealed_favs = {"Preferred drink type": None, "Favorite spirit": None, "Favorite tastes": set(),
                              "Favorite ingredients": set(), "Favorite keywords": set()}
        self.times_visited = 0
        self.order_history = []
        self.bar_love = 0

    def generate_customer(self):
        tag_field = None

        def select_name():
            # TODO: Ensure names arent used twice
            name = utils.roll_probabilities(customer_names.keys())
            dict = customer_names[name]
            customer_names.pop(name)
            nonlocal tag_field
            gender = dict["gender"]
            tag_field = dict["tag_field"]
            self.name = name
            self.gender = gender

        def apply_tags():
            tags = str(tag_field).split(", ")
            for tag in tags:
                match tag:
                    case "Beer":
                        self.drink_pref = ingredients.Beer
                    case "Wine":
                        self.drink_pref = ingredients.Wine
                    case _:
                        self.tags.add(tag)

        def generate_drink_pref():
            probabilities = {ingredients.Beer: 100, recipe.Recipe: 100, ingredients.Wine: 80}
            if self.gender == "masc":
                probabilities[ingredients.Beer] += prob_points["men order beer"]
            elif self.gender == "fem":
                probabilities[ingredients.Wine] += prob_points["women order wine"]
                probabilities[ingredients.Beer] += prob_points["women order beer"]
            self.drink_pref = utils.roll_probabilities(probabilities)

        def generate_fav_spirit():
            self.fav_spirit = utils.roll_probabilities(
                [ingredients.Vodka, ingredients.Whiskey, ingredients.Gin, ingredients.Tequila, ingredients.Rum])

        def generate_fav_tastes():
            for i in range(5):
                self.fav_tastes.add(utils.roll_probabilities(flavors.tastes.keys()))

        def generate_fav_ingreds():
            faves = set()
            possible_ingreds = (
                    list_ingredients(typ=ingredients.Liqueur) + list_ingredients(typ=ingredients.Fruit) +
                    list_ingredients(typ=ingredients.Spice) + list_ingredients(typ=ingredients.Herb) +
                    list_ingredients(typ=ingredients.Tea) + list_ingredients(typ=ingredients.Absinthe) +
                    [get_ingredient("Coca-Cola"), get_ingredient("Sprite")])
            for i in range(10):
                ingredient = utils.roll_probabilities(possible_ingreds)
                faves.add(ingredient)
            self.fav_ingreds = faves

        def generate_fav_keywords():
            words = set(random.choices(list(flavors.keywords), k=5))
            self.fav_keywords = words

        select_name()
        if tag_field is not None:
            apply_tags()
        if not self.drink_pref:
            generate_drink_pref()
        generate_fav_spirit()
        generate_fav_tastes()
        generate_fav_ingreds()
        generate_fav_keywords()

    def format_name(self):
        return f"[cstmr]{self.name}[/cstmr]"

    def score(self, game_time, drink: ingredients.MenuItem, drinking=False):
        # TODO: Score with the ingredients they chose
        logger.log(f"{self.name} scoring {drink.name}:")
        points = Decimal(0)

        cost_points = round(Decimal(drink.cost_value()[0] * 8), 2)
        points += cost_points
        logger.log(f"   {cost_points} points from cost value")

        if isinstance(drink, self.drink_pref):
            points += 50
            logger.log("    50 points from preferred drink type")

        for taste in self.fav_tastes:
            if taste in drink.taste_profile:
                taste_points = drink.taste_profile[taste] * 5
                points += taste_points
                logger.log(f"   {taste_points} points from favorite taste {taste}")
                if drinking and taste_points > 25 and not self.is_revealed(taste):
                    self.say(game_time, random.choice([f"I'm a big fan of the {taste} flavor in this {drink.name}.",
                                                       f"I love when drinks taste {taste}.",
                                                       f"It's {taste}... I like it.", f"Very {taste}. I'm interested.",
                                                       f"This {drink.name} tastes nicely {taste}.",
                                                       f"The {taste} flavor is a nice touch.",
                                                       f"I love how {taste} this {drink.name} is.",
                                                       f"{taste.capitalize()} drinks are great.",
                                                       f"I like how it tastes {taste}.",
                                                       f"That's a good {taste} flavor.",
                                                       f"The {drink.name} is {taste}. It's good.",
                                                       f"Tastes pretty {taste}. I'm a fan.",
                                                       f"I do tend to go for {taste} drinks.",
                                                       f"I like a good {taste} drink."]))
                    self.reveal_fav(taste)

        if isinstance(drink, recipe.Recipe):
            for ingredient in drink.r_ingredients:
                if isinstance(ingredient, self.fav_spirit):
                    logger.log("    50 points from favorite spirit")
                    points += 50
                    if drinking and not self.is_revealed(spirit):
                        spirit = self.fav_spirit().format_type()
                        self.say(game_time,
                                 random.choice([f"{spirit} is calling my name!", f"{spirit} cocktails are the best!",
                                                f"Uh oh... {spirit} is my weakness.",
                                                f"I'll always say yes to {spirit}.",
                                                f"Oh, {spirit}... What would I do without you?",
                                                f"Awesome, {spirit} is my weapon of choice.",
                                                f"I love a good {spirit} cocktail.",
                                                f"Oooh, you have {spirit} cocktails!"]))
                        self.reveal_fav(spirit)

                if ingredient in self.fav_ingreds:
                    logger.log(f"   80 points from favorite ingredient {ingredient.name}")
                    points += 80
                    if drinking and not self.is_revealed(ingredient):
                        self.reveal_fav(ingredient)
                        if ingredient.name not in {"lime", "lemon"}:
                            self.say(game_time,
                                     random.choice([f"Oh man, they've got {ingredient.name} in the {drink.name}!",
                                                    f"Oooh, {ingredient.name} is my favorite.",
                                                    f"I love cocktails with {ingredient.name}.",
                                                    f"Oh, hey, I love {ingredient.name}!",
                                                    f"I've always got {ingredient.name} for cocktails at home.",
                                                    f"{ingredient.name.capitalize()} is a favorite of mine.",
                                                    f"{ingredient.name.capitalize()} goes great in cocktails.",
                                                    f"Aw, {ingredient.name}! I love {ingredient.name}.",
                                                    f"{ingredient.name.capitalize()} cocktail? My lucky day!"]))

        logger.log(f"{points} points total")
        return points

    def order(self, bar, game_time):
        bar.occupancy.customer_displayed = self

        def order_type_probabilities():
            probs = {}
            for section in bar.menu.menu_sections():
                if len(section[0]) == 0:
                    continue
                typ = section[2]

                probs[typ] = 100
                if typ == ingredients.Wine:
                    probs[ingredients.Wine] += prob_points["people order wine"]
                elif typ == ingredients.Mead:
                    probs[ingredients.Mead] += prob_points["people order mead"]

                for menu_item in section[0]:
                    probs[typ] += 5

            if self.gender == "masc":
                if ingredients.Beer in probs:
                    probs[ingredients.Beer] += prob_points["men order beer"]
            elif self.gender == "fem":
                try:
                    probs[ingredients.Wine] += prob_points["women order wine"]
                    probs[ingredients.Beer] += prob_points["women order beer"]
                except KeyError:
                    pass
            return probs

        typ = self.drink_pref().format_type().lower()
        typs = self.drink_pref().format_type(plural=True).lower()
        if len(bar.menu.get_section(self.drink_pref)) > 0:
            if len(bar.menu.get_section(self.drink_pref)) < 4:
                self.say(game_time, msg=random.choice([f"There's not a lot of {typs}...",
                                                       f"I was thinking there would be more {typs}...",
                                                       f"They don't have much of a {typ} selection...",
                                                       f"Well, at least there's a couple {typs}...",
                                                       f"Not many {typs} at this place...",
                                                       f"My favorite places have a few more {typs}.",
                                                       f"I'd rather have a {typ}, but there aren't too many here.", ]))

            ordering_pref_drink = utils.roll_probabilities(ratio_chances["order preferred drink type"])
        else:
            if random.randint(1, 6) > 5:
                self.say(game_time, msg=random.choice([f"Wish I could have a {typ}.", f"I could really go for a {typ}.",
                                                       f"Aw, they don't have any {typs}.",
                                                       f"Let's go somewhere with {typ} next.",
                                                       f"I'd be happier with a {typ} in my hand.",
                                                       f"What I could really use is a {typ}.",
                                                       f"I was thinking there'd be {typs}.", f"I'd love a {typ}.",
                                                       f"I like my {typ} bars a little better."]))
            ordering_pref_drink = False
        if ordering_pref_drink:
            order = utils.roll_probabilities(bar.menu.get_section(self.drink_pref))
        else:
            order_type_probs = order_type_probabilities()

            order_typ = utils.roll_probabilities(utils.percentize(order_type_probs))

            scores = {}
            for menu_item in bar.menu.get_section(order_typ):
                scores[menu_item] = self.score(game_time, menu_item)
            order = utils.roll_probabilities(scores)

        style = order.get_style()
        bar.occupancy.log(game_time,
                          f"{self.format_name()} orders {utils.format_a(order.name)} [{style}]{order.name}[/{style}]. "
                          f"[money](+${"{:.2f}".format(order.current_price())})[/money]")
        self.score(game_time, order, drinking=True)

        bar.make_sale(order)
        self.order_history.append(order)

    def say(self, game_time, msg):
        self.bar.occupancy.log(game_time, f"[dimmed]{self.name}: {msg}[/dimmed]")

    def is_revealed(self, pref):
        if isinstance(pref, type):
            if self.revealed_favs["Preferred drink type"] is None:
                return False
            elif self.revealed_favs["Preferred drink type"] == pref:
                return True
            else:
                logger.logprint("[error]Customer's revealed preference is not the reference object")
        elif isinstance(pref, ingredients.Spirit):
            if self.revealed_favs["Favorite spirit"] is None:
                return False
            elif self.revealed_favs["Favorite spirit"] == pref:
                return True
            else:
                logger.logprint("[error]Customer's revealed preference is not the reference object")
        elif isinstance(pref, ingredients.Ingredient):
            if pref in self.revealed_favs["Favorite ingredients"]:
                return True
            else:
                return False
        elif isinstance(pref, str):
            if pref in flavors.tastes:
                if pref in self.revealed_favs["Favorite tastes"]:
                    return True
                else:
                    return False
            elif pref in flavors.keywords:
                if pref in self.revealed_favs["Favorite keywords"]:
                    return True
                else:
                    return False

    def reveal_fav(self, pref):
        if pref == self.drink_pref:
            self.revealed_favs["Preferred drink type"] = pref
        elif pref == self.fav_spirit:
            self.revealed_favs["Favorite spirit"] = pref
        elif pref in self.fav_tastes:
            self.revealed_favs["Favorite tastes"].add(pref)
        elif pref in self.fav_ingreds:
            self.revealed_favs["Favorite ingredients"].add(pref)
        elif pref in self.fav_keywords:
            self.revealed_favs["Favorite keywords"].add(pref)

    def customer_panel(self):

        unknown_text = Text("Unknown", style=console.get_style("dimmed"))

        def table_fav(attribute, fav_name):
            text = Text("")
            if isinstance(attribute, Iterable):
                for term in attribute:
                    if self.is_revealed(term):
                        if attribute == self.fav_tastes:
                            text += Text(term + ", ", style=console.get_style(term))
                        elif attribute == self.fav_ingreds:
                            text += Text(term.name + ", ", style=console.get_style(term.get_style()))
                        else:
                            text += Text(term.name + ", ")
                    else:
                        text += unknown_text + ", "
                text = text[:-2]

            else:
                if self.revealed_favs[fav_name] is None:
                    text = unknown_text
                else:
                    style = attribute().format_type()
                    text = Text(attribute, style=console.get_style(style))

            table.add_row(f"{fav_name}:", text)
            table.add_row()

        table = Table(show_header=False, box=None)
        table.add_row(self.format_name(), f"{self.times_visited} visits")
        table.add_row()

        table_fav(attribute=self.drink_pref, fav_name="Preferred drink type")
        table_fav(attribute=self.fav_spirit, fav_name="Favorite spirit")
        table_fav(attribute=self.fav_tastes, fav_name="Favorite tastes")
        table_fav(attribute=self.fav_ingreds, fav_name="Favorite ingredients")
        table_fav(attribute=self.fav_keywords, fav_name="Favorite keywords")

        table.add_row("Order history:", str([order.name for order in self.order_history[:5]]))

        panel = Panel(renderable=table)
        return panel


def create_customer(bar):
    new_customer = Customer(bar)
    new_customer.generate_customer()
    return new_customer


class CustomerGroup:
    def __init__(self, group_id, customers):
        self.group_id = group_id
        self.customers = customers
        self.arrival = None
        self.last_round = None

    def order_round(self, bar, game_time):
        for customer in self.customers:
            customer.order(bar, game_time)
