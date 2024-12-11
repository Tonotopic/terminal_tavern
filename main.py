from pyplayscii import playscii
import bar

from rich_console import console
import ingredients
from rich.layout import Layout

main_layout = Layout()

bar = bar.Bar(1000)
bar.purchase()

ingredients.load_ingredients_from_db()

for ingredient in ingredients.all_ingredients.values():
    console.print(ingredient.description())




