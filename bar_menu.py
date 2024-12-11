from rich import box
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.layout import Layout

from ingredients import Beer, Cider, Wine, Mead, MenuItem
from recipe import Recipe
from rich_console import console, styles, standardized_spacing, Screen
from commands import items_to_commands, find_command, command_to_item, input_loop
import ingredients


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

    def get_section(self, item: MenuItem):
        for menu_section in self.menu_sections():
            if isinstance(item, menu_section[2]):
                return menu_section[0]

    # </editor-fold>

    # <editor-fold desc="Display">
    def table_menu(self, display_type=None, expanded=False):
        # @TODO: Multiple columns or live display to save space
        table = Table(show_header=False, box=box.MINIMAL, style=styles.get("bar_menu"))
        lst = []

        # Menu overview
        if display_type is None:
            table.add_column("Type", width=115)
            table.add_column("Quantity")
            for menu_section, sect_name, sect_typ in self.menu_sections():
                table.add_row()
                table.add_row(Text(sect_name, style=styles.get(sect_name.lower())),
                              str(len(menu_section)), end_section=True)
                lst.append(sect_typ)

                if expanded:
                    for menu_item in menu_section:
                        table.add_row(menu_item.list_item())
                        table.add_row()
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

            table.add_row(Text(sect_name, style=styles.get(sect_name.lower())), str(len(display_section)),
                          end_section=True)

            if display_section == self.cocktails:
                for cocktail in display_section:
                    listing = cocktail.list_item()
                    table.add_row(listing)
                    table.add_row()
                    lst.append(cocktail)
            else:
                for item in display_section:
                    listing = item.list_item()
                    table.add_row(listing)
                    table.add_row()
                    lst.append(item)

        return table, lst

    # </editor-fold>

    # <editor-fold desc="Modify">
    def add(self, add_typ, add_arg=""):
        self.bar.screen = Screen.BAR_MENU
        inv_ingredients = ingredients.list_ingredients(self.bar.stock.inventory, add_typ)

        if add_arg != "":
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
                add_typ = None
                if typ_cmd:
                    pass
                else:
                    console.print(f"[error]{typ_cmd} did not match to a menu category")
                    return False
                add_typ = command_to_item(typ_cmd, [Recipe, ingredients.Beer, ingredients.Cider, ingredients.Wine,
                                                    ingredients.Mead])
                if add_typ is None:
                    console.print("[error]Add type argument does not match any category")
                    return False
            if add_typ is ingredients.Ingredient:
                console.print("[error]No type or ingredient given to add command. Syntax: add beer")
                return False
            elif add_typ == Recipe:
                choosing_recipe = True
                while choosing_recipe:
                    recipes_table, recipes_list = self.bar.show_recipes(off_menu=True)
                    recipes_panel = Panel(recipes_table, border_style=styles.get("bar_menu"))
                    recipes_layout = Layout(recipes_panel)

                    recipe_commands = items_to_commands(recipes_list)
                    recipe_commands.add("back")
                    recipe_commands.add("new")

                    console.print(recipes_layout)

                    prompt = "Enter the name of a recipe, or 'new' to define a new recipe"
                    recipe_cmd = input_loop(prompt, recipe_commands, bar=self.bar)[0]

                    if recipe_cmd == "new":
                        self.bar.new_recipe()
                    elif recipe_cmd == "back":
                        return True
                    else:
                        for index, recipe in enumerate(recipes_list):
                            if recipe_cmd == recipe.name.lower():
                                self.cocktails.append(recipes_list[index])
                                return True

            else:
                add_tool_table, add_tool_list = self.bar.stock.table_items(add_typ, off_menu=True)
                add_tool_panel = Panel(add_tool_table, border_style=styles.get("bar_menu"))
                add_tool_layout = Layout(add_tool_panel)

                console.print(add_tool_layout)

                adding = True
                add_commands = items_to_commands(add_tool_list)
                add_commands.add("back")
                while adding:
                    recipe_cmd, ing_args = input_loop("Type a name to add", add_commands, bar=self.bar)
                    if recipe_cmd == "back":
                        return True
                    else:
                        ingredient = command_to_item(recipe_cmd, inv_ingredients)
                        self.get_section(ingredient).append(ingredient)
                        return True

    def remove(self, remove_arg):
        item_cmd = find_command(remove_arg, items_to_commands(self.full_menu()))
        if item_cmd:
            rmv_item = command_to_item(item_cmd, self.full_menu())
            menu_section = self.get_section(rmv_item)
            menu_section.remove(rmv_item)
            return True
        else:
            console.print(f"[error]'{remove_arg}' did not match to a current menu item")
            return False

    def markup(self, markup_arg):
        if markup_arg == "":
            console.print("[error]Syntax: 'markup \\[menu item]'")
            return False
        else:
            pass

    def markdown(self, markdown_arg):
        pass
    # </editor-fold>
