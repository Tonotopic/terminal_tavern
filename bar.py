import commands
from ingredients import Ingredient, list_ingredients, all_ingredients
from rich.layout import Layout
from rich_console import console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.style import Style
from rich import box


class Bar:
    def __init__(self, balance=1000):
        self.inventory = {}  # Dictionary: {ingredient_object: fluid_ounces}
        self.balance = balance  # Float: current balance in dollars
        self.menu = {}  # List of Recipe objects
    def purchase(self, current_selection: type or Ingredient = Ingredient):
        # <editor-fold desc="Layout">
        table_settings = {
            'title_style': "underline",
            'show_header': False,
            'expand': True,
            'leading': 2
        }
        shop_panel = Panel(box=box.DOUBLE_EDGE, renderable="render failed")
        inv_panel = Panel(box=box.DOUBLE_EDGE, renderable="render failed")
        purchase_layout = Layout(name="purchase_layout")
        purchase_layout.split_column(
            Layout(name="purchase_header"),
            Layout(name="purchase_screen")
        )
        purchase_layout["purchase_screen"].split_row(
            Layout(name="bar", renderable=inv_panel),
            Layout(name="shop", renderable=shop_panel)
        )

        # </editor-fold>

        # <editor-fold desc="Populating shop panels">
        shop_commands = set()
        shop_list = []

        if isinstance(current_selection, type):  # Not currently selecting an ingredient
            subclasses = current_selection.__subclasses__()
            for typ in subclasses:
                shop_list.append(typ)

            # Create a table to display the shop list
            shop_table = Table(title="Available for Purchase", **table_settings)
            inv_table = Table(title="Bar Stock", **table_settings)

            tables = (shop_table, inv_table)
            for table in tables:
                table.add_column("Category", justify="center")
                container = self.inventory if table == inv_table else all_ingredients

                for category in subclasses:
                    obj = category()
                    style = obj.get_ing_style()
                    shop_commands.add(f"{obj.format_type().lower()}s")

                    table.add_row(Text(f"{obj.format_type()}s "  # Pluralize
                                       f"({len(list_ingredients(container, category))})",  # Quantity
                                       style=style))

                items = list_ingredients(container, current_selection)
                if items:  # If there are ingredients in this category
                    for item in items.values():
                        if type(item) is current_selection:
                            table.add_row(item.description())
                            shop_list.append(item)
                            shop_commands.add(item.name.lower())

            shop_panel.renderable = shop_table
            inv_panel.renderable = inv_table
        elif isinstance(current_selection, Ingredient):
            ingredient = current_selection
            style = ingredient.get_ing_style()
            # <editor-fold desc="inv_table">
            inv_volume = 0
            inv_table = Table(title=f"Your volume of [{style}]{ingredient.name}[/{style}]", box=None, padding=(5, 0, 0, 0),
                              **table_settings)
            inv_table.add_column(justify="center")
            if ingredient in self.inventory:
                inv_volume = self.inventory.get(ingredient)
            inv_table.add_row(Text(f"{inv_volume}oz", style))
            # </editor-fold>
            # <editor-fold desc="vol_table">
            vol_table = Table(title=f"Available Volumes of [{style}]{ingredient.name}[/{style}]", **table_settings)
            vol_table.add_column("Volume", justify="center")
            vol_table.add_column("Price", justify="center")
            vol_table.show_header = True

            for volume, price in ingredient.volumes.items():
                vol_table.add_row(f"[{style}]{volume}oz[/{style}]",
                                  Text("${:.2f}".format(price), style=Style(color="#cfba02")))
            # </editor-fold>
            shop_panel.renderable = vol_table
            inv_panel.renderable = inv_table
        else:
            console.print("current_category is not category or ingredient")
        # </editor-fold>

        console.print(purchase_layout)
        inpt = (commands.find_command(console.input("Type a category to view:"), shop_commands)
                .lower())
        match inpt:
            case "quit":
                return
            # <editor-fold desc="case 'back:'">
            case "back":
                if current_selection == Ingredient:
                    # @TODO Main menu
                    return
                elif isinstance(current_selection, Ingredient):  # Ingredient selected, go back to category
                    self.purchase(type(current_selection))
                    return
                elif isinstance(current_selection, type):  # Back to last category
                    self.purchase(current_selection.__base__)
                    return
                else:
                    console.print("current_category is not category or ingredient")
            # </editor-fold>
            case _:  # wildcard case
                if inpt in shop_commands:
                    for entry in shop_list:
                        if isinstance(entry, type):  # Category commands
                            if inpt == f"{entry().format_type().lower()}s":
                                self.purchase(entry)
                                return
                        elif isinstance(entry, Ingredient):  # Ingredient commands
                            if inpt == entry.name.lower():
                                self.purchase(entry)
                                return
                        else:
                            console.print("Not registering as type or Ingredient instance")

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
