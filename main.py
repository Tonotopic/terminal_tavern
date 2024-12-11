import sys

import commands
import bar
import ingredients
from rich_console import console


def save_game(self, filename="save_game.json"):
    pass


ingredients.load_ingredients_from_db()

for ingredient in ingredients.all_ingredients:
    if isinstance(ingredient, ingredients.MenuItem):
        try:
            console.print(ingredient.name, ingredient.list_price())
        except IndexError as e:
            console.print(ingredient.name)
        except AttributeError as e:
            console.print(ingredient.name)

bar_name = console.input("Name your bar: > ")
bar = bar.Bar(bar_name, 1000)

while True:
    bar.dashboard()

    prompt = "'Shop' or view the 'menu'"
    primary_cmd, args = bar.bar_cmd.input_loop(prompt, ["shop", "menu"])
    if primary_cmd == "shop":
        bar.shop()
    elif primary_cmd == "menu":
        bar.menu.menu_screen()
    elif primary_cmd == "quit":
        bar.bar_cmd.do_quit("")
