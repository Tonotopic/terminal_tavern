import sqlite3

import flavors
import ingredients
import recipe
import utils

connection = sqlite3.connect("tavern_db.db")
cursor = connection.cursor()
cursor.execute("SELECT * FROM customer_names")
rows = cursor.fetchall()
customer_names = {}
for row in rows:
    name, gender, tag_field = row
    customer_names[name] = {"gender": gender, "tag_field": tag_field}
connection.close()


class Customer():
    def __init__(self):
        self.name = None
        self.gender = None
        self.tags = set()
        self.drink_pref = None
        self.fav_tastes = set()

    def generate_customer(self):

        tag_field = None

        def select_name():
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
            probabilities = {ingredients.Beer: 0.4, recipe.Recipe: 0.4, ingredients.Wine: 0.2}
            self.drink_pref = utils.roll_probabilities(probabilities)

        def generate_fav_tastes():
            for i in range(5):
                self.fav_tastes.add(utils.roll_probabilities(flavors.tastes.keys()))

        select_name()
        if tag_field is not None:
            apply_tags()
        if not self.drink_pref:
            generate_drink_pref()
        generate_fav_tastes()
