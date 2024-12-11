import flavors
import rich_console
from ingredients import load_ingredients_from_db, all_ingredients, MenuItem
import ui
from rich_console import console

for ingredient in all_ingredients:
    if isinstance(ingredient, MenuItem):
        try:
            console.print(ingredient.name, ingredient.list_price())
        except IndexError as e:
            console.print(ingredient.name)
        except AttributeError as e:
            console.print(ingredient.name)


current_bar = ui.startup_screen()

while True:
    if current_bar.get_screen() == "MAIN":
        ui.dashboard(current_bar)
    elif current_bar.get_screen() == "SHOP":
        # current_selection passed in shop command handler, and shop recursively calls itself
        # shop screen is set inside ui.shop_screen - return once it's done calling itself
        current_bar.set_screen("MAIN")
    elif current_bar.get_screen() == "BAR_MENU":
        ui.menu_screen(current_bar)
