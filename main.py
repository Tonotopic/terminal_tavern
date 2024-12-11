from ingredients import load_ingredients_from_db
import ui
from rich_console import Screen

load_ingredients_from_db()

'''for ingredient in ingredients.all_ingredients:
    if isinstance(ingredient, ingredients.MenuItem):
        try:
            console.print(ingredient.name, ingredient.list_price())
        except IndexError as e:
            console.print(ingredient.name)
        except AttributeError as e:
            console.print(ingredient.name)'''

current_bar = ui.startup_screen()
while True:
    if current_bar.screen == Screen.MAIN:
        ui.dashboard(current_bar)
    elif current_bar.screen == Screen.SHOP:
        ui.shop_screen(current_bar)
    elif current_bar.screen == Screen.BAR_MENU:
        ui.menu_screen(current_bar)
