from rich.layout import Layout

import commands
import bar
import ingredients
from rich_console import console

main_layout = Layout()

ingredients.load_ingredients_from_db()

bar = bar.Bar(1000)
inpt = commands.find_command(console.input("Type 'shop' to shop: > "), commands.main_commands)
if inpt == "shop":
    bar.shop()
