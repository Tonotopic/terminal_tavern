import math

from rich import box
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

import ingredients
import logger
import recipe
from ingredients import Beer, Cider, Wine, Mead, MenuItem, list_ingredients, Ingredient
from recipe import Recipe
from rich_console import console, styles
from commands import items_to_commands, find_command, command_to_item, input_loop


class BarMenu:
    def __init__(self, bar):
        self.bar = bar
        self.cocktails: list[Recipe] = []
        self.beer: list[Beer] = []
        self.cider: list[Cider] = []
        self.wine: list[Wine] = []
        self.mead: list[Mead] = []

    # <editor-fold desc="Sections">
    def full_menu(self):
        return self.cocktails + self.beer + self.cider + self.wine + self.mead

    def menu_sections(self):
        return [(self.cocktails, "Cocktails", Recipe), (self.beer, "Beer", Beer), (self.cider, "Cider", Cider),
                (self.wine, "Wine", Wine), (self.mead, "Mead", Mead)]

    def get_section(self, item: str | MenuItem):
        if isinstance(item, str):
            for category in self.menu_sections():
                if item == category[1].lower():
                    return category[0]
            menu_item = find_command(item, items_to_commands(self.full_menu()))
            if menu_item:
                item = command_to_item(menu_item, self.full_menu())

        for menu_section in self.menu_sections():
            if isinstance(item, menu_section[2]):
                return menu_section[0]

    # </editor-fold>

    # <editor-fold desc="Display">
    def table_menu(self, display_type=None, expanded=False):
        table_settings = {
            "show_header": False,
            "box": box.MINIMAL,
            "style": styles.get("bar_menu")
        }
        table_1 = Table(**table_settings)
        table_2 = Table(**table_settings)
        table_3 = Table(**table_settings)
        tables = [table_1, table_2, table_3]
        width = console.size[0] if expanded else int(console.size[0] / 2)
        for table in tables:
            table.add_column(width=width - 12)
        lst = []

        # Menu overview
        if display_type is None:

            table_section = table_1
            for menu_section, sect_name, sect_typ in self.menu_sections():
                if sect_typ in (recipe.Recipe, ingredients.Beer) or len(menu_section) > 0:
                    table_section.add_row()
                    table_section.add_row(Text(sect_name, style=styles.get(sect_name.lower())),
                                          str(len(menu_section)), end_section=True)
                    lst.append(sect_typ)

                    for menu_item in menu_section:
                        if len(table_1.rows) > console.height - 8:
                            if len(table_2.rows) > console.height - 8:
                                table_section = table_3
                            else:
                                table_section = table_2
                        table_section.add_row(menu_item.list_item(expanded=expanded))
                        table_section.add_row()
                        lst.append(menu_item)

        # Viewing specifically the Beer menu, Cocktail menu, etc
        else:
            display_section = None
            for menu_section, sect_name, sect_typ in self.menu_sections():
                if display_type == sect_typ:
                    display_section = menu_section
                    break
            if display_section is None:
                console.print("[error]Display section does not match to an existing menu section")
                return None

            table_1.add_row(Text(sect_name, style=styles.get(sect_name.lower())), str(len(display_section)),
                            end_section=True)
            table_1.add_row()

            table_section = table_1
            for item in display_section:
                if len(table_1.rows) > console.height - 12:
                    if len(table_2.rows) > console.height - 12:
                        table_section = table_3
                    else:
                        table_section = table_2

                listing = item.list_item(expanded=expanded)
                table_section.add_row(listing)
                table_section.add_row()
                lst.append(item)

        filled_tables = [table for table in [table_1, table_2, table_3] if len(table.rows) > 0]
        return filled_tables, lst

    def overview(self, item):
        if isinstance(item, Ingredient):
            description_panel = Panel(renderable=item.description(), border_style=item.get_style())
            stock_rem = self.bar.stock.inventory[item]
            pours_left = math.floor(stock_rem / item.pour_vol())
            stock_panel = Panel(
                renderable=f"[panel]{stock_rem}[/panel]oz in stock ([panel]{pours_left}[/panel] full pours)",
                border_style=styles.get("panel"))
            overview_layout = Layout(name="overview_layout")
            overview_layout.split_column(Layout(name="description", renderable=description_panel, size=3),
                                         Layout(name="stock", renderable=stock_panel, size=3))

        elif isinstance(item, recipe.Recipe):
            ingredients_panel = Panel(renderable=item.breakdown_ingredients(), title=item.name,
                                      border_style=styles.get("cocktails"))
            taste_panel = Panel(renderable=item.print_taste_profile(), title="Taste Profile",
                                border_style=styles.get("panel"))

            overview_layout = Layout(name="overview_layout")
            overview_layout.split_row(Layout(name="ingredients", renderable=ingredients_panel),
                                      Layout(name="taste_profile", renderable=taste_panel))

        console.print(overview_layout)
        primary_cmd = input_loop("'Back' to go back", ["back"], bar=self.bar)
        if primary_cmd == "back":
            return

    # </editor-fold>

    # <editor-fold desc="Modify">

    def select_to_add(self, add_typ, add_arg=""):
        self.bar.set_screen("BAR_MENU")

        add_commands = ["back", "menu"]
        add_prompt = "Type a name to add"

        if add_arg != "":
            inv_ingredients = list_ingredients(self.bar.stock.inventory, add_typ)
            ing_command = find_command(add_arg, items_to_commands(inv_ingredients))[0]
            if ing_command is not None:
                ingredient = command_to_item(ing_command, inv_ingredients)
                if ingredient:
                    self.bar.menu.__getattribute__(add_typ.__name__).append(ingredient)
                    return True
                else:
                    console.print("[error]Ingredient arg given to add command, but ingredient not found")
                    return False
            else:
                console.print("[error]Arg given to add method, but find_command returned None")
                return False

        else:  # No ingredient given
            if isinstance(add_typ, str):
                typ_cmd = find_command(add_typ, [section[1].lower() for section in self.menu_sections()])
                if not typ_cmd:
                    console.print(f"[error]{typ_cmd} did not match to a menu category")
                    return False
                add_typ = command_to_item(typ_cmd, [Recipe, Beer, Cider, Wine, Mead])
                if add_typ is None:
                    console.print("[error]Add type argument does not match any category")
                    return False
            if add_typ is Ingredient:
                console.print("[error]No type or ingredient given to add command. Syntax: add beer")
                return False

            adding = True
            logger.log("Adding " + add_typ().format_type())
            while adding:
                if add_typ == Recipe:
                    add_tool_table, add_tool_list = self.bar.show_recipes(off_menu=True)
                    if "new" not in add_commands:
                        add_commands.append("new")
                else:
                    add_tool_table, add_tool_list = self.bar.stock.table_items(add_typ, off_menu=True)

                add_tool_panel = Panel(add_tool_table, border_style=styles.get("bar_menu"))
                add_tool_layout = Layout(add_tool_panel)
                add_commands.extend(items_to_commands(add_tool_list))

                console.print(add_tool_layout)
                add_cmd, ing_args = input_loop(add_prompt, add_commands, bar=self.bar, skip="new")
                if add_cmd == "back":
                    self.bar.set_screen("BAR_MENU")
                    return True
                elif add_cmd == "menu":
                    self.bar.set_screen("MAIN")
                    return True
                if add_cmd == "new":
                    self.bar.new_recipe()
                else:
                    item = command_to_item(add_cmd, add_tool_list)
                    self.add(item)
                    self.bar.set_screen("BAR_MENU")
                    return True

    def add(self, item):
        self.get_section(item).append(item)

    def remove(self, remove_arg):
        item_cmd = find_command(remove_arg, items_to_commands(self.full_menu()))
        if item_cmd:
            rmv_item = command_to_item(item_cmd, self.full_menu())
            menu_section = self.get_section(rmv_item)
            menu_section.remove(rmv_item)
            logger.log(f"Removing {rmv_item.name} from the menu.")
            return True
        else:
            console.print(f"[error]'{remove_arg}' did not match to a current menu item")
            return False

    def mark(self, direction, mark_arg):
        if mark_arg == "":
            console.print("[error]Syntax: 'markup \\[menu item/category]'")
            return False
        else:
            category_strings = [cat[1].lower() for cat in self.menu_sections()]
            menu_args = items_to_commands(self.full_menu()).union(set(category_strings))
            cmd = find_command(mark_arg, menu_args)
            if cmd in menu_args:
                item = command_to_item(cmd, self.full_menu() + [section[2] for section in self.menu_sections()])
                if isinstance(item, type):
                    obj = item()
                    style = obj.get_style()
                    name = obj.format_type()
                else:
                    style = item.get_style()
                    name = item.name
                    if item.markup != 0:
                        console.print(
                            f"[{style}]{item.name}[/{style}]'s price is marked up by [money]{"${:.2f}".format(item.markup)}.")
                    if item.markdown != 0:
                        console.print(
                            f"[{style}]{name}[/{style}] is currently marked down by {item.formatted_markdown}.")

                prompt = f"[cmd]Mark{direction} [{style}]{name}[/{style}] by what percentage or dollar value?[/cmd] > "
                logger.log(f"Marking {direction} {name}...")
                value = None
                percent = False
                while value is None:
                    try:
                        inpt = console.input(prompt).strip()
                        if find_command(inpt, ["back"], feedback=False):
                            return True
                        if inpt.startswith("$"):
                            value = float(inpt.strip("$"))
                        elif inpt.endswith("%"):
                            percent = True
                            value = float(inpt[:-1]) / 100
                        else:
                            if float(inpt) == 0.00:
                                value = 0
                            else:
                                console.print("[error]Must begin with $ or end with %")
                                continue
                    except ValueError:
                        console.print("[error]Must be a number")

                if cmd in category_strings:
                    successful = True
                    for menu_item in self.get_section(cmd):
                        if direction == "up":
                            if not menu_item.mark_up(value, percent):
                                successful = False
                                msg = f"[error]Error marking section {cmd} thrown by {menu_item.name}"
                                console.print(msg)
                                logger.log(msg)
                        elif direction == "down":
                            if not menu_item.mark_down(value, percent):
                                successful = False
                                msg = f"[error]Error marking section {cmd} thrown by {menu_item.name}"
                                console.print(msg)
                                logger.log(msg)
                    return successful


                elif item in self.get_section(item):
                    if direction == "up":
                        return item.mark_up(value, percent)
                    elif direction == "down":
                        return item.mark_down(value, percent)
            else:
                console.print(f"[error]Syntax: 'mark{direction} \\[item]' or 'mark{direction} \\[category]'")
                return None

    # </editor-fold>

    def check_stock(self):
        for menu_item in self.full_menu():
            if not self.bar.stock.has_enough(menu_item):
                console.print(
                    f"[error] Not enough {menu_item.name}! Restock or remove from the menu before proceeding.")
                return False
        return True
