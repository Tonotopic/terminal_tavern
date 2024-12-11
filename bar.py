import commands
import ingredients
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
        self.bar_cmd = commands.BarCmd(self)
        self.inventory = {}  # Dictionary: {ingredient_object: fluid_ounces}
        self.balance = balance  # Float: current balance in dollars
        self.menu = {}  # List of Recipe objects

    def shop(self, current_selection: type or Ingredient = Ingredient):
        # <editor-fold desc="Layout">
        global prompt
        table_settings = {
            'title_style': "underline",
            'show_header': False,
            'expand': True,
            'leading': 2
        }
        shop_panel = Panel(box=box.DOUBLE_EDGE, renderable="render failed")
        inv_panel = Panel(box=box.DOUBLE_EDGE, renderable="render failed")
        shop_layout = Layout(name="shop_layout")
        shop_layout.split_column(
            Layout(name="shop_header"),  # @TODO: Display current balance
            Layout(name="shop_screen")
        )
        shop_layout["shop_screen"].split_row(
            Layout(name="bar", renderable=inv_panel),
            Layout(name="shop", renderable=shop_panel)
        )

        # </editor-fold>

        # <editor-fold desc="Populating shop panels">
        shop_commands = set("")
        shop_commands.add("back")  # Commands specific to the shop
        # @TODO: Sort shop list display
        shop_list = []

        # Category selected, not currently selecting an ingredient
        if isinstance(current_selection, type):
            prompt = "Type a category to view: > "
            subclasses = current_selection.__subclasses__()  # Any more categories available
            for typ in subclasses:
                shop_list.append(typ)

            shop_table = Table(title="Available for Purchase", **table_settings)
            inv_table = Table(title="Bar Stock", **table_settings)

            tables = (shop_table, inv_table)
            for table in tables:
                table.add_column("Category", justify="center")
                container = self.inventory if table == inv_table else all_ingredients.values()

                for category in subclasses:
                    obj = category()
                    style = obj.get_ing_style()
                    shop_commands.add(f"{obj.format_type().lower()}s")

                    table.add_row(Text(f"{obj.format_type()}s "  # Pluralize
                                       f"({len(list_ingredients(container, category))})",  # Quantity
                                       style=style))

                items = list_ingredients(container, current_selection)
                if items:  # If there are ingredients in this category
                    # @TODO: Don't show full descriptions in inv_table
                    # @TODO: Placeholder for empty bar stock when all in shop_list are ingredients
                    prompt = "Type a category or product to view: > "
                    for item in items.values():
                        if type(item) is current_selection:
                            # @TODO: Descriptions justified to center looks bad
                            table.add_row(item.description())
                            # @TODO: At-a-glance price comparison
                            shop_list.append(item)
                            # @TODO: Remove accent markings from shop commands
                            shop_commands.add(item.name.lower())

            shop_panel.renderable = shop_table
            inv_panel.renderable = inv_table
        # Specific ingredient currently selected, show volumes
        elif isinstance(current_selection, Ingredient):
            shop_commands.add("buy")
            prompt = "Buy /[volume/], or go back: > "
            ingredient = current_selection
            style = ingredient.get_ing_style()

            # <editor-fold desc="inv_table">
            inv_volume = 0
            inv_table = Table(title=f"Your volume of [{style}][italic]{ingredient.name}[/{style}]", box=None,
                              padding=(5, 0, 0, 0),
                              **table_settings)
            inv_table.add_column(justify="center")
            if ingredient in self.inventory:
                inv_volume = self.inventory.get(ingredient)
            inv_table.add_row(Text(f"{inv_volume}oz", style))
            # </editor-fold>

            # <editor-fold desc="vol_table">
            vol_table = Table(title=f"Available Volumes of [{style}][italic]{ingredient.name}[/{style}]",
                              **table_settings)
            vol_table.add_column("Volume", justify="center")
            vol_table.add_column("Price", justify="center")
            vol_table.show_header = True

            for volume, price in ingredient.volumes.items():
                # @TODO: Sort volumes by price ascending
                vol_table.add_row(f"[{style}]{volume}oz[/{style}]",
                                  Text("${:.2f}".format(price), style=Style(color="#cfba02")))
            # </editor-fold>
            shop_panel.renderable = vol_table
            inv_panel.renderable = inv_table
        else:
            console.print("current category is not category or ingredient")
        # </editor-fold>

        console.print(shop_layout)

        # <editor-fold desc="Input">

        #  Match to any part of command when input > 3, e.g. so "gold" can return "Jose Cuervo Especial Gold"
        force_beginning = False
        #  When options on the screen are "Alcohols" and "Non-Alcoholic Drinks"
        if current_selection == ingredients.Drink:
            # Force match to the beginning of the word so "alco"+ doesn't return both commands
            force_beginning = True

        inpt = console.input(prompt).strip().lower()
        # Group spaced words together if not a command, so "especial silver" can pass to find_command
        # @TODO: As commands with args are added, skip them here
        if not inpt.startswith("buy"):
            inpt = f'"{inpt}"'
        inpt_cmd = commands.find_command(inpt, shop_commands, force_beginning)
        if isinstance(inpt_cmd, tuple):  # If find_command returned args
            primary_command, args = inpt_cmd  # Unpack the tuple
        else:
            primary_command = inpt_cmd
            args = []
        if primary_command in shop_commands:
            if primary_command == "buy":
                # Inject ingredient from menu into buy command
                '''parts = inpt.split()'''
                args.insert(0, current_selection)
                # TODO: Nonexistent quantity throws Key_Error in do_buy
                if self.bar_cmd.onecmd([primary_command, args]):
                    self.shop(type(current_selection))  # Go back from the ingredient screen
            elif inpt_cmd == "back":
                if current_selection == Ingredient:
                    # @TODO Main menu
                    return
                elif isinstance(current_selection, Ingredient):  # Ingredient selected, go back to category
                    self.shop(type(current_selection))
                    return
                elif isinstance(current_selection, type):  # Back to last category
                    self.shop(current_selection.__base__)
                    return
                else:
                    console.print("current_category is not category or ingredient")
            for entry in shop_list:
                if isinstance(entry, type):  # Category commands
                    if inpt_cmd == f"{entry().format_type().lower()}s":
                        self.shop(entry)
                        return
                elif isinstance(entry, Ingredient):  # Ingredient commands
                    if inpt_cmd == entry.name.lower():
                        self.shop(entry)
                        return
        else:
            console.print("No valid command found.")
        # </editor-fold>

    def save_game(self, filename="save_game.json"):
        pass
        """Saves the bar's inventory and balance to a file."""
        data = {
            "balance": self.balance,
            "inventory": {
                ingredient.name: ingredient.quantity  # Assuming ingredient has name and quantity
                for ingredient in self.inventory  # Assuming inventory is a list of Ingredient objects
                if ingredient.quantity > 0
            },
        }

        with open(filename, "w") as f:
            pass
            # json.dump(data, f, indent=4)  # Write data to file with indentation for readability

        print(f"Game saved to {filename}")


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
