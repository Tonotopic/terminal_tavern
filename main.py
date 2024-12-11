from rich.layout import Layout
from colorama import just_fix_windows_console
import commands

import bar
import ingredients
from rich_console import console

just_fix_windows_console()
main_layout = Layout()

ingredients.load_ingredients_from_db()

bar = bar.Bar(1000)
inpt = commands.find_command(console.input("Type 'purchase' to make a purchase"))
if inpt == "purchase":
    bar.purchase()

'''
for ingredient in ingredients.all_ingredients.values():
    console.print(ingredient.description())
'''
