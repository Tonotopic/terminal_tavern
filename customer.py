import random

import recipe
from data import flavors, ingredients
from data.ingredients import list_ingredients, get_ingredient
from data.db_connect import get_connection, close_connection
from utility import utils

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
    def __init__(self):
        self.name = None
        self.gender = None
        self.tags = set()

        self.drink_pref = None
        self.fav_spirit = None
        self.fav_tastes = set()
        self.fav_ingreds = set()

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
            for i in range(15):
                ingredient = utils.roll_probabilities(possible_ingreds)
                faves.add(ingredient)
            self.fav_ingreds = faves

        select_name()
        if tag_field is not None:
            apply_tags()
        if not self.drink_pref:
            generate_drink_pref()
        generate_fav_spirit()
        generate_fav_tastes()
        generate_fav_ingreds()

    def format_name(self):
        return f"[customer]{self.name}[/customer]"

    def score(self, drink: ingredients.MenuItem):
        points = 0
        for taste in self.fav_tastes:
            if taste in drink.taste_profile:
                points += drink.taste_profile[taste]

    def order(self, bar):
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
                if probs[ingredients.Beer]:
                    probs[ingredients.Beer] += prob_points["men order beer"]
            elif self.gender == "fem":
                if probs[ingredients.Wine]:
                    probs[ingredients.Wine] += prob_points["women order wine"]
                    probs[ingredients.Beer] += prob_points["women order beer"]
            return probs

        ordering_pref_drink = utils.roll_probabilities(ratio_chances["order preferred drink type"])
        if ordering_pref_drink:
            order = utils.roll_probabilities(bar.menu.get_section(self.drink_pref))
        else:
            order_type_probs = order_type_probabilities()

            order_typ = utils.roll_probabilities(utils.percentize(order_type_probs))

            order = utils.roll_probabilities(bar.menu.get_section(order_typ))

        style = order.get_style()
        bar.barspace.log(
            f"{self.format_name()} orders {utils.format_a(order.name)} [{style}]{order.name}[/{style}].    "
            f"[money](+${"{:.2f}".format(order.current_price())})[/money]")

        bar.make_sale(order)
        self.order_history.append(order)


def create_customer():
    new_customer = Customer()
    new_customer.generate_customer()
    return new_customer


class CustomerGroup:
    def __init__(self, group_id, customers):
        self.group_id = group_id
        self.customers = customers
        self.arrival = None
        self.last_round = None

    def order_round(self, bar):
        for customer in self.customers:
            customer.order(bar)
