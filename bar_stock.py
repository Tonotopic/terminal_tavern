from rich import box
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.layout import Layout
from rich.style import Style

from rich_console import console, styles, Screen
import commands
from ingredients import all_ingredients, list_ingredients, Ingredient, Spirit, Liqueur, categorize_spirits, Drink

# TODO: "Shop beer"
class BarStock:
    def __init__(self, bar):
        self.bar = bar
        self.inventory = {}  # Dictionary: {ingredient_object: fluid_ounces}

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
                return (table, overflow_table, overflow_2), lst
            return (table, overflow_table), lst
        else:
            return table, lst



    def check_ingredients(self, recipe):
        """Checks if there are ingredients in the inventory to make the recipe."""
        for required_ingredient, quantity in recipe.r_ingredients.items():
            if isinstance(required_ingredient, type):  # Check if requirement is a type (accepts any)
                found_match = False
                for inv_ingredient in self.inventory:
                    if isinstance(inv_ingredient,
                                  required_ingredient):
                        found_match = True
                        break  # Stop checking further for this ingredient
                if not found_match:
                    return False  # No ingredient of the right type provided
            else:  # Specific ingredient required
                if required_ingredient not in self.inventory:
                    return False  # Missing specific ingredient
                # Add quantity check if needed

        return True  # All ingredients are valid