from rich import box
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.layout import Layout

from ingredients import Beer, Cider, Wine, Mead, MenuItem
from recipe import Recipe
from rich_console import console, styles, standardized_spacing, Screen
from commands import parse_input, items_to_commands, find_command, command_to_item
import ingredients


class BarMenu:
    def __init__(self):
        self.cocktails: list[Recipe] = []
        self.beer: list[Beer] = []
        self.cider: list[Cider] = []
        self.wine: list[Wine] = []
        self.mead: list[Mead] = []

    def menu_sections(self):
        return [(self.cocktails, "Cocktails", Recipe), (self.beer, "Beer", Beer), (self.cider, "Cider", Cider),
                (self.wine, "Wine", Wine), (self.mead, "Mead", Mead)]

    def get_section(self, item: MenuItem):
        for menu_section in self.menu_sections():
            if isinstance(item, menu_section[2]):
                return menu_section[0]

    def table_menu(self, display_type=None, expanded=False):
        # @TODO: Multiple columns to save space
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
                    listing, price = cocktail.list_item()
                    table.add_row(listing, price)
                    table.add_row()
                    lst.append(cocktail)
            else:
                for item in display_section:
                    listing, price = item.list_item()
                    table.add_row(listing, price)
                    lst.append(item)

        return table, lst

    def menu_screen(self, bar):
        bar.screen = Screen.BAR_MENU
        global type_displaying
        type_displaying = None
        prompt = "'Back' to go back"

        while bar.screen == Screen.BAR_MENU:
            menu_table, menu_list = self.table_menu(display_type=type_displaying, expanded=True)
            bar_menu_panel = Panel(title=f"{bar.name} Menu", renderable=menu_table,
                                   border_style=styles.get("bar_menu"))
            bar_menu_layout = Layout(name="bar_menu_layout", renderable=bar_menu_panel)

            console.print(bar_menu_layout)

            menu_commands = set()
            # When viewing a section, don't add menu items as primary commands
            if type_displaying is None:
                menu_commands = items_to_commands(menu_list)  # Categories
                menu_commands.add("add")
            menu_commands.add("remove")
            menu_commands.add("back")
            menu_commands.add("menu")

            primary_cmd = None
            while primary_cmd is None:
                inpt = parse_input(prompt, menu_commands)
                if inpt is None:  # Help method returned
                    continue  # Don't try to unpack and throw an error
                primary_cmd, args = inpt
                if primary_cmd == "add" and len(args) == 0:
                    console.print("[error]Invalid args. Use: 'add cocktail', 'add beer', etc.")
                    primary_cmd = None

            if primary_cmd == "back":
                if type_displaying is None:  # At the full menu screen
                    bar.screen = Screen.MAIN
                else:  # Viewing beer menu, etc.
                    type_displaying = None
            elif primary_cmd == "menu":
                bar.screen = Screen.MAIN
            elif primary_cmd == "add":
                typ_cmd = find_command(args[0], items_to_commands(menu_list))
                if typ_cmd is not None:  # e.g. add beer
                    add_typ = command_to_item(typ_cmd, menu_list)
                    self.add(bar, add_typ)
            elif primary_cmd == "remove":
                typ_cmd = find_command(args[0], menu_commands)
                if typ_cmd is not None:
                    remove_typ = command_to_item(typ_cmd, menu_list)
                    self.do_remove(remove_typ)
            elif primary_cmd in menu_commands:  # beer, cider, wine, etc.
                type_displaying = command_to_item(primary_cmd, menu_list)
            elif bar.bar_cmd.onecmd(primary_cmd, args):
                pass
            else:
                console.print("[error]No allowed command recognized.")

    def add(self, bar, add_typ, add_arg=""):
        bar.screen = Screen.BAR_MENU
        inv_ingredients = ingredients.list_ingredients(bar.inventory, add_typ)

        if add_arg != "":
            ing_command = find_command(add_arg, items_to_commands(inv_ingredients))[0]
            if ing_command is not None:
                ingredient = command_to_item(ing_command, inv_ingredients)
                if ingredient:
                    bar.menu.__getattribute__(add_typ.__name__).append(ingredient)
                    # TODO: This isn't visible
                    console.print(f"{ingredient.name} added to menu.")
                    return True
                else:
                    console.print("[error]Ingredient arg given to add command, but ingredient not found")
                    return False
            else:
                console.print("[error]Arg given to add method, but find_command returned None")
                return False

        else:  # No ingredient given
            if add_typ is ingredients.Ingredient:
                console.print("[error]No type or ingredient given to add command. Syntax: add beer | add guinness")
                return False
            elif add_typ == Recipe:
                choosing_recipe = True
                while choosing_recipe:
                    recipes_table, recipes_list = bar.show_recipes(off_menu=True)
                    recipes_panel = Panel(recipes_table, border_style=styles.get("bar_menu"))
                    recipes_layout = Layout(recipes_panel)

                    recipe_commands = items_to_commands(recipes_list)
                    recipe_commands.add("back")
                    recipe_commands.add("new")

                    console.print(recipes_layout)

                    recipe_cmd = None
                    while recipe_cmd is None:
                        recipe_cmd = parse_input("Enter the name of a recipe, or 'new' to define a new recipe",
                                                 recipe_commands)[0]
                    if recipe_cmd == "new":
                        bar.new_recipe()
                    elif recipe_cmd == "back":
                        return
                    elif recipe_cmd == "quit":
                        bar.bar_cmd.onecmd(recipe_cmd)
                    else:
                        for index, recipe in enumerate(recipes_list):
                            if recipe_cmd == recipe.name.lower():
                                self.cocktails.append(recipes_list[index])
                                return True

            else:
                add_tool_table, add_tool_list = bar.table_inv(add_typ, off_menu=True)
                add_tool_panel = Panel(add_tool_table, border_style=styles.get("bar_menu"))
                add_tool_layout = Layout(add_tool_panel)

                console.print(add_tool_layout)

                adding = True
                add_commands = items_to_commands(add_tool_list)
                add_commands.add("back")
                add_commands.add("quit")
                while adding:
                    recipe_cmd, ing_args = parse_input("Type a name to add", add_commands)
                    if recipe_cmd:
                        if recipe_cmd == "back":
                            return
                        else:
                            ingredient = command_to_item(recipe_cmd, inv_ingredients)
                            self.get_section(ingredient).append(ingredient)
                            adding = False
