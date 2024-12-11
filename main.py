from rich.layout import Layout
from colorama import just_fix_windows_console

import bar
import ingredients
from rich_console import console

just_fix_windows_console()
main_layout = Layout()

bar = bar.Bar(1000)
bar.purchase()

ingredients.load_ingredients_from_db()

for ingredient in ingredients.all_ingredients.values():
    console.print(ingredient.description())




