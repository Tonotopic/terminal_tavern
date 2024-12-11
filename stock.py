from rich.table import Table
from rich.text import Text

import ingredients
import logger
from rich_console import console, styles
from recipe import Recipe
from ingredients import all_ingredients, list_ingredients, Ingredient, Spirit, Liqueur, categorize_spirits, get_ingredient, MenuItem, Beer, Cider, Wine, Mead


# TODO: "Shop beer"
class BarStock:
    def __init__(self, bar):
        self.bar = bar
        self.inventory = {}  # Dictionary: {ingredient_object: fluid_ounces}

    def buy(self, ingredient: Ingredient = None, arg=""):
        parts = arg.split()

        if len(parts) == 2:  # i.e. buy 24
            ingredient = get_ingredient(str(parts[0]))
            volume = parts[1]

        elif len(parts) == 1:
            volume = arg

        else:
            console.print("[error]Incorrect number of arguments. Usage: buy <quantity>")
            return False

        try:
            volume = int(volume)
        except ValueError:
            console.print("[error]Invalid quantity. Please enter a number.")
            return False

        if ingredient:
            if volume in ingredient.volumes:
                price = ingredient.volumes[volume]
                balance = self.bar.balance
                if balance >= price:
                    self.bar.balance -= price
                    self.inventory[ingredient] = self.inventory.get(ingredient, 0) + volume
                    return True
                else:
                    console.print(f"[error]Insufficient funds. Bar balance: [money]${balance}")
                    return False
            else:
                console.print(f"[error]Invalid volume. Available: {[oz for oz in ingredient.volumes.keys()]}")
                return False
        else:
            console.print("[error]No ingredient selected. Please select an ingredient first.")
            return False

    def table_items(self, typ, off_menu=False):
        inv_ingredients = list_ingredients(self.inventory, typ)
        add_tool_table = Table(expand=True)
        lst = []
        for i in range(3):
            add_tool_table.add_column("Name")
            add_tool_table.add_column("Type")

        row_ings = []
        for ingredient in inv_ingredients:
            if off_menu:
                if ingredient in self.bar.menu.get_section(ingredient):
                    continue
            lst.append(ingredient)
            row_ings.append(Text(ingredient.name, style=typ().get_ing_style()))
            row_ings.append(ingredient.format_type())
            if len(row_ings) == 6:
                add_tool_table.add_row(row_ings[0], row_ings[1], row_ings[2], row_ings[3], row_ings[4], row_ings[5],
                                       end_section=True)
                row_ings = []
        if len(row_ings) != 0:
            for i in range(6):
                if i + 1 > len(row_ings):
                    row_ings.append("")
            add_tool_table.add_row(row_ings[0], row_ings[1], row_ings[2], row_ings[3], row_ings[4], row_ings[5])

        return add_tool_table, lst

    def show_stock(self, table_settings, typ: type = Ingredient, showing_flavored=False, shop=False):
        table = Table(**table_settings)
        lst = []
        container = all_ingredients if shop else self.inventory

        table.add_column(justify="center")
        subclasses = typ.__subclasses__()
        items = list_ingredients(container, typ, type_specific=True)

        showing_flavorable_spirit = False
        if (isinstance(typ(), Spirit) or isinstance(typ(), Liqueur)) and typ is not Spirit:
            showing_flavorable_spirit = True

        if not showing_flavored:
            for index, subclass in enumerate(subclasses):
                end_section = False
                if items and index == len(subclasses) - 1 and not showing_flavorable_spirit:
                    end_section = True
                obj = subclass()
                style = obj.get_ing_style()
                table.add_row(Text(f"{obj.format_type(plural=True)} "  # Pluralize
                                   f"({len(list_ingredients(container, subclass))})",  # Quantity
                                   style=style), end_section=end_section)
                table.add_row()  # rich.table's leading parameter breaks end_section. Add space between rows manually
                lst.append(subclass)

        if showing_flavorable_spirit:
            flavored, unflavored = categorize_spirits(items)
            if not showing_flavored:
                table.add_row(Text(f"Flavored ({len(flavored)})",
                                   style=styles.get("additive")), end_section=True)
                table.add_row()  # Manual space between rows
                lst.append("Flavored")
                items = unflavored
        if showing_flavored:
            items = flavored

        global table_section
        table_section = table
        overflow_table = Table(**table_settings)
        overflow_2 = Table(**table_settings)
        overflow_table.add_column(justify="center")
        overflow_2.add_column(justify="center")
        for item in items:
            if len(table.rows) > console.height - 12:
                if len(overflow_table.rows) > console.height - 12:
                    table_section = overflow_2
                else:
                    table_section = overflow_table

            if type(item) is typ:
                lst.append(item)
                style = item.get_ing_style()
                if shop:
                    table_section.add_row(f"[{style}][italic]{item.name}")
                else:
                    volume = container.get(item, 0)
                    table_section.add_row(f"[{style}][italic]{item.name}[/italic] ({volume}oz)")
                table_section.add_row()

        if len(table.rows) == 0:
            table.add_row(Text("[None]", styles.get("dimmed")))

        if len(overflow_table.rows) != 0:
            if len(overflow_2.rows) != 0:
                return [table, overflow_table, overflow_2], lst
            return [table, overflow_table], lst
        else:
            return [table], lst

    def check_ingredients(self, recipe):
        """Checks if there are enough ingredients in stock to make the recipe."""
        ing_missing = False
        for req_ingredient, req_quantity in recipe.r_ingredients.items():
            if isinstance(req_ingredient, type):  # Check if requirement is a type (accepts any)
                found_match = False
                for inv_ingredient in self.inventory:
                    if isinstance(inv_ingredient,
                                  req_ingredient):

                        if self.inventory[inv_ingredient] >= req_quantity:
                            found_match = True
                            logger.log(f"{inv_ingredient.name} in quantity {self.inventory[inv_ingredient]} satisfies "
                                       f"{req_ingredient().format_type()} requirement")
                            break
                        else:
                            logger.log(f"{inv_ingredient.name} in quantity {self.inventory[inv_ingredient]} "
                                       f"not enough for {req_ingredient().format_type()} requirement")
                if not found_match:
                    if not ing_missing:
                        ing_missing = True
                        console.print(f"[error]Ingredients missing for {recipe.name}:")
                    console.print(f"[error] Not enough {req_ingredient().format_type()}!")
                    # Continue looping so all missing ingredients are printed
            else:  # Specific ingredient required
                if req_ingredient in self.inventory:
                    if self.inventory[req_ingredient] >= req_quantity:
                        logger.log(f"{req_ingredient.name} in quantity {self.inventory[req_ingredient]} "
                                   f"satisfies requirement")
                        break
                    else:
                        logger.log(
                            f"{req_ingredient.name} in quantity {self.inventory[req_ingredient]} "
                            f"not enough to satisfy requirement of {req_quantity}")
                        console.print(f"[error] Not enough {req_ingredient.name}!")
                else:
                    console.print(f"[error] No {req_ingredient.name}!")
                    return False  # Missing specific ingredient
                # Add quantity check if needed
        if ing_missing:
            return False
        else:
            return True  # All ingredients present

    def has_enough(self, menu_item: MenuItem):
        if isinstance(menu_item, Recipe):
            if self.check_ingredients(menu_item):
                return True
        else:
            if self.inventory[menu_item] >= menu_item.pour_vol():
                return True
            else:
                console.print(f"[error]Not enough {menu_item.name}!")

        return False

    def pour(self, menu_item: MenuItem):
        if isinstance(menu_item, Recipe):
            for ingredient, volume in menu_item.r_ingredients:
                self.inventory[ingredient] -= volume
                logger.log(f"Pouring {volume} of {ingredient.name} - stock now at {self.inventory[ingredient]}")
        else:
            self.inventory[menu_item] -= menu_item.pour_vol()
            logger.log(f"Pouring {menu_item.pour_vol()} of {menu_item.name} - stock now at {self.inventory[menu_item]}")


