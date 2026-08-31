from data.ingredients import load_ingredients_from_db, Beer, Wine, Cider, Mead, mean_median_cost_value, all_ingredients
from data.menu_items import MenuItem
from display.rich_console import console
from interface import ui
from utility import utils

if utils.debugging():
    width, height = console.size
    console.size = 120, height

load_ingredients_from_db()

"""for ingredient in all_ingredients:
    console.print(f"{ingredient.format_name()} ({ingredient.format_type()})")
    console.print(ingredient.print_taste_profile())"""

'''for ingredient in all_ingredients:
    if isinstance(ingredient, MenuItem):
        try:
            console.print(ingredient.name, ingredient.list_price())
        except IndexError as e:
            console.print(ingredient.name)
        except AttributeError as e:
            console.print(ingredient.name)'''

for category in [Beer, Wine, Cider, Mead]:
    mean, median = mean_median_cost_value(category)
    console.print(
        f"{category.__name__} mean: ${mean:.2f}, median: ${median:.2f}"
    )

for ingredient in all_ingredients:
    if not isinstance(ingredient, MenuItem):
        continue
    console.print(f"{ingredient.quality_score() * 100:.2f}: {ingredient.format_name()}")

ui.startup_screen()
current_bar = utils.current_bar

while True:
    if current_bar.get_screen() == "MAIN":
        ui.dashboard(current_bar)
    elif current_bar.get_screen() == "SHOP":
        # current_selection passed in shop command handler, and shop recursively calls itself
        # shop screen is set inside ui.shop_screen - return once it's done calling itself
        current_bar.set_screen("MAIN")
    elif current_bar.get_screen() == "BAR_MENU":
        ui.menu_screen(current_bar)
    elif current_bar.get_screen() == "PLAY":
        ui.play_screen(current_bar, current_bar.occupancy.opening_time)
