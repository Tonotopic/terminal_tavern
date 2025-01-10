from rich.table import Table
from rich.text import Text

from interface import commands
from utility import logger
from display.rich_console import console, styles
from recipe import Recipe
from data.ingredients import all_ingredients, list_ingredients, Ingredient, Spirit, Liqueur, separate_flavored, \
    get_ingredient, MenuItem


class BarStock:
    def __init__(self, bar):
        self.bar = bar
        self.inventory = {}  # Dictionary: {ingredient_object: fluid_ounces}

    def buy(self, ingredient: Ingredient = None, arg=""):
        """
        Parses volume argument and purchases the given volume of the current ingredient.

        :param ingredient: Ingredient to buy; currently being displayed
        :param arg: User input for the volume to buy
        :return: True if purchase successful
        """
        parts = arg.split()

        if len(parts) == 2:  # i.e. buy 24
            ingredient = get_ingredient(str(parts[0]))
            volume = parts[1]

        elif len(parts) == 1:
            volume = arg

        else:
            logger.logprint("[error]Incorrect number of arguments. Usage: buy <quantity>")
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
                    logger.logprint(f"[error]Insufficient funds. Bar balance: [money]${balance}")
                    return False
            else:
                logger.logprint(f"[error]Invalid volume. Available: {[oz for oz in ingredient.volumes.keys()]}")
                return False
        else:
            logger.logprint("[error]No ingredient selected. Please select an ingredient first.")
            return False

    def table_items(self, typ, off_menu=False):
        """
        Creates a table of items of the given type in stock.

        :param typ: The type of ingredient to display.
        :param off_menu: Set to True to display only items not already on the menu
        :return: The table and a list of the objects it displays.
        """
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
            row_ings.append(Text(ingredient.name, style=typ().get_style()))
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

    def reload(self):
        """Reloads all ingredients in stock from the database to update any changes and ensure all instances point to the
        same object."""
        new_ings = {}
        for inv_ing in self.inventory:
            for db_ing in all_ingredients:
                if inv_ing.name == db_ing.name:
                    new_ings[db_ing] = self.inventory[inv_ing]
        self.inventory = new_ings
        logger.log("Stock reloaded.")

    def table_ing_category(self, table_settings, typ: type = Ingredient, showing_flavored=False, shop=False):
        """
        Tables a category of ingredient, not just including ingredients of that type, but also listing sub-categories for
        selection, as in the shop/stock.

        :param table_settings: Unpackable containing any arguments to specify when constructing the table.
        :param typ: The current type to display, defaulting to start with Ingredient.
        :param showing_flavored: Whether the current page is the flavored subsection of the current type.
        :param shop: Set to True to table the shop, leave False to table your bar stock
        :return: A list of tables (multiple for overflow), and a list of the contents
        """

        container = all_ingredients if shop else self.inventory
        table_1 = Table(**table_settings)
        table_1.add_column(justify="center")
        tables = [table_1]
        lst = []

        subclasses = typ.__subclasses__()
        items = list_ingredients(container, typ, no_inheritance=True)
        items = sorted(items, key=lambda x: x.name)

        showing_flavorable_spirit = False
        if (isinstance(typ(), Spirit) or isinstance(typ(), Liqueur)) and typ is not Spirit:
            showing_flavorable_spirit = True

        if not showing_flavored:  # List subclasses
            for index, subclass in enumerate(subclasses):
                end_section = False
                # New section for any items once there are no more categories to list
                if items and index == len(subclasses) - 1 and not showing_flavorable_spirit:
                    end_section = True
                obj = subclass()
                style = obj.get_style()
                table_1.add_row(Text(f"{obj.format_type(plural=True)} "  # Pluralize
                                     f"({len(list_ingredients(container, subclass))})",  # Quantity
                                     style=style), end_section=end_section)
                table_1.add_row()  # rich.table's leading parameter breaks end_section. Add space between rows manually
                lst.append(subclass)

        if showing_flavorable_spirit:
            flavored, unflavored = separate_flavored(items)
            if not showing_flavored:  # Group flavored into a category and only list unflavored
                table_1.add_row(Text(f"Flavored ({len(flavored)})",
                                     style=styles.get("additive")), end_section=True)
                table_1.add_row()  # Manual space between rows
                lst.append("Flavored")
                items = unflavored
        if showing_flavored:
            items = flavored

        global table_section
        table_section = table_1
        for item in items:
            if len(table_section.rows) > console.height - 12:
                table_section = Table(**table_settings)
                table_section.add_column(justify="center")
                tables.append(table_section)

            if type(item) is typ:
                lst.append(item)
                style = item.get_style()
                if shop:
                    min_price = "{:.2f}".format(item.price_per_oz("min"))
                    max_price = "{:.2f}".format(item.price_per_oz("max"))
                    spacing = (console.size[0] / 2) - 6 - 11

                    if min_price == max_price:
                        price_string = f"${min_price}"
                    else:
                        price_string = f"${min_price} - ${max_price}"
                        spacing -= 8

                    table_section.add_row(f"[{style}][italic]{item.name}[/{style}][/italic]"
                                          f"{rich_console.standardized_spacing(item.name, spacing)}"
                                          f"[money]{price_string} /oz")

                else:
                    volume = container.get(item, 0)
                    table_section.add_row(f"[{style}][italic]{item.name}[/italic] ({volume}oz)")
                table_section.add_row()

        if len(table_1.rows) == 0:
            table_1.add_row(Text("[None]", styles.get("dimmed")))

        return tables, lst

    def list_type(self, typ, min_vol=0):
        """Lists the ingredients in stock of a specified type, with an optional minimum volume."""
        lst = []
        for item in self.inventory:
            if type(item) is typ and self.inventory[item] >= min_vol:
                lst.append(item)
        return lst

    def check_ingredients(self, recipe):
        """Checks if there are enough of all ingredients in stock to make the recipe."""
        logger.log(f"Checking ingredients for {recipe.name}...")
        ing_missing = False
        for req_ingredient, req_quantity in recipe.r_ingredients.items():
            if isinstance(req_ingredient, type):  # Check if requirement is a type (accepts any)
                req_quantity = req_ingredient().get_portions()[req_quantity]
                found_match = False
                has_enough = False
                for inv_ingredient in self.inventory:
                    if isinstance(inv_ingredient,
                                  req_ingredient):
                        found_match = True
                        if self.inventory[inv_ingredient] >= req_quantity:
                            has_enough = True
                            logger.log(
                                f"   {inv_ingredient.name} in quantity {self.inventory[inv_ingredient]} satisfies "
                                       f"{req_ingredient().format_type()} requirement")
                            break
                        else:
                            logger.log(f"   {inv_ingredient.name} in quantity {self.inventory[inv_ingredient]} "
                                       f"not enough for {req_ingredient().format_type()} requirement")
                if not has_enough:
                    if not ing_missing:
                        ing_missing = True
                        logger.logprint("[error]Ingredients missing for {recipe.name}:")
                    if found_match:
                        logger.logprint("[error] Not enough {req_ingredient().format_type()}!")
                    else:
                        logger.logprint("[error] No {req_ingredient().format_type()}!")
                    # Continue looping so all missing ingredients are printed
            else:  # Specific ingredient required
                if req_ingredient.name == "soda water":
                    continue
                req_quantity = req_ingredient.get_portions()[req_quantity]
                if req_ingredient in self.inventory:
                    if self.inventory[req_ingredient] >= req_quantity:
                        logger.log(f"   {req_ingredient.name} in quantity {self.inventory[req_ingredient]} "
                                   f"satisfies requirement")
                        break
                    else:
                        if not ing_missing:
                            ing_missing = True
                            console.print(f"[error]Ingredients missing for {recipe.name}:")
                        logger.log(
                            f"{req_ingredient.name} in quantity {self.inventory[req_ingredient]} "
                            f"not enough to satisfy requirement of {req_quantity}")
                        logger.logprint(f"[error] Not enough {req_ingredient.name}!")
                else:
                    if not ing_missing:
                        ing_missing = True
                        logger.logprint(f"[error]Ingredients missing for {recipe.name}:")
                    logger.logprint(f"[error] No {req_ingredient.name}!")
                # Add quantity check if needed
        if ing_missing:
            return False
        else:
            return True  # All ingredients present

    def has_enough(self, menu_item: MenuItem):
        """Checks whether inventory is sufficient to pour a single MenuItem, whether single ingredient or recipe."""
        if isinstance(menu_item, Recipe):
            if self.check_ingredients(menu_item):
                return True
        else:
            if self.inventory[menu_item] >= menu_item.pour_vol():
                return True
            else:
                console.print(f"[error]Not enough {menu_item.name}!")

        return False

    def select_ingredients(self, recipe):
        """
        For recipes with ingredients that accept any of a type (i.e. Bourbon), allows the user to select which
        ingredient to use from a list of compatible ingredients in stock.

        :param recipe: The cocktail being served.
        :return: A dict mirroring the recipe with the final selected ingredients inserted.
        """
        final_ings = dict()
        for r_ingredient in recipe.r_ingredients:
            if isinstance(r_ingredient, type):
                logger.log(f"Selecting {r_ingredient().format_type()}...")
                vol = r_ingredient().get_portions()[recipe.r_ingredients[r_ingredient]]
                available_ings = self.list_type(r_ingredient, min_vol=vol)
                options_str = [ing.name for ing in available_ings]
                console.print(f"  {options_str}")
                logger.log(f"  {options_str}")
                cmd = commands.input_loop(f"Select {r_ingredient().format_type()}",
                                          commands.items_to_commands(available_ings))[0]
                item = commands.command_to_item(cmd, available_ings)
                final_ings[item] = vol
            else:
                vol = r_ingredient.get_portions()[recipe.r_ingredients[r_ingredient]]
                final_ings[r_ingredient] = vol
        return final_ings

    def pour(self, menu_item: MenuItem):
        """Removes ingredients from the stock in proper portions, initiating ingredient selection where applicable."""
        logger.log(f"Pouring {menu_item.name}...")
        if isinstance(menu_item, Recipe):
            provided_ings = self.select_ingredients(menu_item)
            for ingredient in provided_ings:
                vol = provided_ings[ingredient]
                if ingredient.name != "soda water":
                    self.inventory[ingredient] -= vol
                logger.log(f"   Pouring {vol} of {ingredient.name} - stock now at {self.inventory[ingredient]}")
        else:
            self.inventory[menu_item] -= menu_item.pour_vol()
            logger.log(
                f"   Pouring {menu_item.pour_vol()} of {menu_item.name} - stock now at {self.inventory[menu_item]}")
