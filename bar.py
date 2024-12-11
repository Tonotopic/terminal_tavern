import rich.pretty

import commands
from ingredients import Ingredient, list_ingredients, all_ingredients
from rich.layout import Layout
from rich_console import console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich import box


class Bar:
    def __init__(self, balance=1000):
        self.inventory = {}  # Dictionary: {ingredient_object: fluid_ounces}
        self.balance = balance  # Float: current balance in dollars
        self.menu = {}  # List of Recipe objects

    def purchase(self):
        shop_commands = set()
        current_category = Ingredient

        while True:

            purchase_layout = Layout(name="purchase_layout")
            purchase_layout.split_column(
                Layout(name="purchase_header"),
                Layout(name="purchase_screen")
            )

            # <editor-fold desc="populating shop panels">
            shop_list = []
            subclasses = current_category.__subclasses__()
            for typ in subclasses:
                shop_list.append(typ)

            # Create a table to display the shop list
            shop_table = Table(title="Available for Purchase",
                               title_style="underline", show_header=False, expand=True, leading=2)
            inv_table = Table(title="Bar Stock",
                              title_style="underline", show_header=False, expand=True, leading=2)

            tables = (shop_table, inv_table)
            for table in tables:
                table.add_column("Category", justify="center")
                for category in shop_list:
                    obj = category()
                    style = obj.get_ing_style()
                    shop_commands.add(f"{obj.format_type().lower()}s")
                    container = self.inventory if table == inv_table else all_ingredients
                    table.add_row(Text(f"{obj.format_type()}s "  # Pluralize
                                       f"({len(list_ingredients(container, category))})",  # Quantity
                                       style=style))

            # Embed the table in a panel for better visual presentation
            shop_panel = Panel(shop_table, box=box.DOUBLE_EDGE, style="#c2af02")
            inv_panel = Panel(inv_table, box=box.DOUBLE_EDGE, style="#c2af02")
            # </editor-fold>

            purchase_layout["purchase_screen"].split_row(
                Layout(name="bar", renderable=inv_panel),
                Layout(name="shop", renderable=shop_panel)
            )

            console.print(purchase_layout)
            inpt = (commands.find_command(console.input("Type a category to view:"), shop_commands)
                    .lower())
            match inpt:
                case "quit":
                    break
                case "back":
                    if current_category != Ingredient:
                        current_category = current_category.__base__
                    else:
                        # @TODO Main menu
                        break
                case _: # wildcard case
                    if inpt in shop_commands:
                        for category in shop_list:
                            if inpt == f"{category().format_type().lower()}s":
                                current_category = category
                            break
                    else:
                        console.print("No matching commands found.")



class Recipe:
    def __init__(self, name, r_ingredients: dict[type[Ingredient] | Ingredient, float]):
        self.name = name
        self.r_ingredients = r_ingredients

    def select_ingredients(self):
        for r_ingredient in self.r_ingredients:
            if isinstance(r_ingredient, type):
                pass

    def check_ingredients(self, provided_ingredients: dict[Ingredient, float]):
        """Checks if provided ingredients satisfy the recipe requirements."""
        for required_ingredient, quantity in self.r_ingredients.items():
            if isinstance(required_ingredient, type):  # Check if requirement is a type (accepts any)
                found_match = False
                for provided_ingredient in provided_ingredients:
                    if isinstance(provided_ingredient,
                                  required_ingredient):
                        found_match = True
                        break  # Stop checking further for this ingredient
                if not found_match:
                    return False  # No ingredient of the right type provided
            else:  # Specific ingredient required
                if required_ingredient not in provided_ingredients:
                    return False  # Missing specific ingredient
                # Add quantity check if needed

        return True  # All ingredients are valid

    def make(self):
        provided_ingredients = {}
        if self.check_ingredients(provided_ingredients):
            pass

    def calculate_abv(self):
        """Calculates the ABV of the recipe using ingredient ABVs."""
        total_alcohol_fl_oz = 0
        total_volume_fl_oz = 0

        for ingredient, fluid_ounces in self.r_ingredients.items():
            if hasattr(ingredient, "abv"):
                alcohol_fl_oz = fluid_ounces * (ingredient.abv / 100)
                total_alcohol_fl_oz += alcohol_fl_oz

            total_volume_fl_oz += fluid_ounces

        if total_volume_fl_oz == 0:
            return 0

        abv = (total_alcohol_fl_oz / total_volume_fl_oz) * 100
        return abv
