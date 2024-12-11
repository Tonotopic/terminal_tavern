from typing import List
from rich import box
from rich.layout import Layout
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.style import Style
from unidecode import unidecode
import warnings

import commands
import ingredients
import recipe
import rich_console
from rich_console import console
from ingredients import Ingredient, list_ingredients, all_ingredients
from recipe import Recipe

warnings.filterwarnings("ignore", category=SyntaxWarning)

global prompt

MAIN = 1
SHOP = 2
INVENTORY = 3
BAR_MENU = 4


class Bar:
    def __init__(self, name, balance=1000):
        self.name = name
        self.bar_cmd = commands.BarCmd(self)
        self.inventory = {}  # Dictionary: {ingredient_object: fluid_ounces}
        self.balance = balance  # Float: current balance in dollars
        self.menu: List[List[Recipe | ingredients.Beer | ingredients.Cider | ingredients.Wine | ingredients.Mead]] = [
            [], [], [], [], []]  # Cocktails, beer, cider, wine, mead
        self.recipes = {}
        self.screen = MAIN

    def dashboard(self):
        # <editor-fold desc="Layout">

        bar_name_panel = Panel(renderable=f"Welcome to [underline]{self.name}!")
        balance_panel = Panel(renderable=f"Balance: [money]${str(self.balance)}")

        bar_layout = Layout(name="bar_layout")
        bar_layout.split_column(Layout(name="bar_header", size=3),
                                Layout(name="bar_body"))
        bar_layout["bar_header"].split_row(Layout(name="bar_name", renderable=bar_name_panel),
                                           Layout(name="balance", renderable=balance_panel))
        # </editor-fold>

        console.print(bar_layout)

    def shop(self, current_selection: type or Ingredient = Ingredient, msg=None):
        """Opens the shop screen and executes an input loop.
        Sub-categories and ingredient items falling under the current selection are displayed and set as commands.
        The user can view and buy products in their available quantities.

            Args:
              :param current_selection: The current category or product being displayed.
              :param msg: One-time specific prompt, such as confirming a successful purchase.
            """
        self.screen = SHOP
        showing_flavored = False

        while self.screen == SHOP:
            # <editor-fold desc="Layout">
            global prompt
            table_settings = {
                "title_style": "underline",
                "show_header": False,
                "expand": True
            }
            panel_settings = {
                "renderable": "render failed",
                "box": box.DOUBLE_EDGE,
                "border_style": rich_console.styles.get("shop")
            }

            header_panel = Panel(**panel_settings, title=f"[money]Shop")
            shop_panel = Panel(**panel_settings, title=f"[money]Available for Purchase")
            inv_panel = Panel(**panel_settings, title=f"[panel]Bar Stock")

            shop_layout = Layout(name="shop_layout")
            shop_layout.split_column(
                Layout(name="shop_header", renderable=header_panel),  # Size is set later based on contents
                Layout(name="shop_screen")
            )
            shop_layout["shop_screen"].split_row(
                Layout(name="bar", renderable=inv_panel),
                Layout(name="shop", renderable=shop_panel)
            )

            # </editor-fold>

            # <editor-fold desc="Header">
            global header_text
            header_table = Table(**table_settings)
            header_table.show_header = True

            header_table.add_column("Current balance:", justify="center", width=21)
            header_table.add_column("Viewing:", justify="center", width=console.width - 40)

            header_panel.renderable = header_table
            header_panel.renderable.justify = "center"
            # </editor-fold>

            # <editor-fold desc="Populating shop panels">

            shop_commands = set(commands.persistent_commands)  # Commands specific to the shop
            shop_commands.add("back")
            shop_commands.remove("menu")

            # TODO: Sort shop list display
            shop_list = []
            overflow_table = Table(**table_settings)
            overflow_2 = Table(**table_settings)

            # Type selected, not currently selecting an ingredient
            if isinstance(current_selection, type):
                if msg:
                    prompt = msg
                else:
                    prompt = "Type a category to view"

                obj = current_selection()

                # Header
                if current_selection == Ingredient:
                    header_text = "[dimmed]All"
                else:  # Show pluralized category name in its proper style
                    style = rich_console.styles.get(obj.get_ing_style())
                    if showing_flavored:
                        header_text = Text(f"Flavored {obj.format_type()}s", style=style)
                    else:
                        header_text = Text(f"{obj.format_type()}s", style=style)

                table_settings["box"] = box.MARKDOWN

                shop_tables, shop_list = self.show_inv(table_settings, current_selection, showing_flavored, shop=True)
                inv_table, inv_list = self.show_inv(table_settings, current_selection, showing_flavored)

                # If there are overflow tables
                if isinstance(shop_tables, tuple):
                    shop_table = shop_tables[0]
                    shop_table.columns[0].footer = "continued..."
                    overflow_table = shop_tables[1]
                    if len(shop_tables) == 3:
                        overflow_2 = shop_tables[2]

                else:
                    shop_table = shop_tables

                items = list_ingredients(shop_list, current_selection, type_specific=True)
                if items:  # If there are ingredients in this category
                    if not msg:
                        prompt = "Type a category or product to view"

                shop_panel.renderable = shop_table
                inv_panel.renderable = inv_table

                for command in commands.items_to_commands(shop_list):
                    shop_commands.add(command)

            # Specific ingredient currently selected, show volumes
            elif isinstance(current_selection, Ingredient):
                shop_commands.add("buy")
                prompt = "Buy \[volume], or go back"
                obj = current_selection
                style = obj.get_ing_style()
                header_text = obj.description()

                # <editor-fold desc="inv_table">
                inv_volume = 0
                inv_table = Table(box=None,
                                  padding=(5, 0, 0, 0),
                                  **table_settings)
                inv_table.add_column(justify="center")
                if obj in self.inventory:
                    inv_volume = self.inventory.get(obj)
                inv_table.add_row(Text(f"{inv_volume}oz", style))
                # </editor-fold>

                # <editor-fold desc="vol_table">
                vol_table = Table(
                    **table_settings)
                vol_table.add_column("Volume", justify="center")
                vol_table.add_column("Price", justify="center")
                vol_table.show_header = True

                for volume, price in obj.volumes.items():
                    vol_table.add_row()  # rich.table.Table's leading parameter breaks end_section. Add space between rows manually
                    vol_table.add_row(f"[{style}]{volume}oz[/{style}]",
                                      Text("${:.2f}".format(price), style=Style(color="#cfba02")))
                # </editor-fold>
                shop_panel.renderable = vol_table
                inv_panel.renderable = inv_table
            else:
                console.print("[error]Current category is not category or ingredient")

            # 60 just appears to be the sweet spot here regardless of window size
            shop_layout["shop_header"].size = 8 if len(header_text) > header_table.columns[1].width + 60 else 7
            header_table.add_row(Text(f"${self.balance}", rich_console.styles.get("money")), header_text)

            # </editor-fold>

            console.print(shop_layout)

            if len(overflow_table.rows) != 0:
                console.input("Press 'enter' to continue to next page...")
                shop_panel.renderable = overflow_table
                console.print(shop_layout)
                if len(overflow_2.rows) != 0:
                    console.input("Press 'enter' to continue to next page...")
                    shop_panel.renderable = overflow_2
                    console.print(shop_layout)

            # <editor-fold desc="Input">

            #  Match to any part of command when input > 3
            force_beginning = False
            #  When options on the screen are "Alcohols" and "Non-Alcoholic Drinks"
            if current_selection == ingredients.Drink:
                # Force match to the beginning of the word so "alco"+ doesn't return both commands
                force_beginning = True

            # There's probably a better way to custom loop the input
            primary_cmd = None
            while primary_cmd is None:
                inpt = commands.parse_input(prompt, shop_commands, force_beginning)
                if inpt is None:
                    continue
                primary_cmd, args = inpt
                if primary_cmd == "buy":  # Inside the loop so error messages with buy can be shown on same screen
                    # Inject ingredient from menu into buy command
                    args.insert(0, current_selection)
                    if self.bar_cmd.onecmd([primary_cmd, args], return_result=True):
                        msg = (f"Bought {args[1]}oz of [{style}]{current_selection.name}[/{style}]. "
                               f"Current stock: {self.inventory[current_selection]}oz")
                        self.shop(type(current_selection), msg)  # Go back from the ingredient screen
                    else:
                        primary_cmd = None
                elif primary_cmd == "help":
                    self.bar_cmd.onecmd(primary_cmd, args)
                    primary_cmd = None

            if primary_cmd == "back":
                if current_selection == Ingredient:
                    self.screen = MAIN
                    return
                elif isinstance(current_selection, Ingredient):  # Ingredient selected, go back to category
                    current_selection = type(current_selection)
                elif isinstance(current_selection, type):
                    if showing_flavored:
                        showing_flavored = False
                    else:
                        current_selection = current_selection.__base__  # Back to last category
                else:
                    console.print("current_category is not category or ingredient")
            elif primary_cmd == "shop":  # exit the shop
                self.screen = MAIN
                return
            elif primary_cmd == "flavored":
                showing_flavored = True
            elif commands.command_to_item(primary_cmd, shop_list):
                self.shop(commands.command_to_item(primary_cmd, shop_list))
            else:
                # If no shop-specific command found
                self.bar_cmd.onecmd(primary_cmd)  # Checks for quit

            # </editor-fold>

    def show_menu(self, typ=None, expanded=False):
        # @TODO: Multiple columns to save space
        table = Table(show_header=False, box=box.MINIMAL, expand=expanded, style=rich_console.styles.get("bar_menu"))
        lst = []
        menu_cats = ["Cocktails", "Beer", "Cider", "Wine", "Mead"]
        types_list = [recipe.Recipe, ingredients.Beer,
                      ingredients.Cider, ingredients.Wine,
                      ingredients.Mead]

        # Menu overview
        if typ is None:
            table.add_column("Type")
            table.add_column("Quantity")
            for i in range(5):  # Menu categories
                table.add_row(Text(menu_cats[i], style=rich_console.styles.get(f"{menu_cats[i].lower()}")),
                              str(len(self.menu[i])), end_section=True)
                command = menu_cats[i].lower() if menu_cats[i] == "Cocktails" else f"{menu_cats[i].lower()}s"
                lst.append(commands.command_to_item(command, types_list))

                if expanded:
                    for index, menu_item in enumerate(self.menu[i]):
                        if isinstance(menu_item, ingredients.Beer):
                            beer_spacing = 50
                            table.add_row(Text(f"{menu_item.name}"
                                               f"{rich_console.standardized_spacing(menu_item.name, beer_spacing)}"
                                               f"({menu_item.format_type()})",
                                               style=menu_item.get_ing_style()))
                        elif isinstance(menu_item, Recipe):
                            cocktail_spacing = 30
                            table.add_row(f"{menu_item.name}"
                                          f"{rich_console.standardized_spacing(menu_item.name, cocktail_spacing)}"
                                          f"{self.menu[i][index].format_ingredients()}")
                        else:
                            table.add_row(Text(menu_item.name, style=menu_item.get_ing_style()))
                    table.add_row()

        # Viewing specifically the Beer menu, Cocktail menu, etc
        else:
            table.expand = False
            total_info_spacing = 20
            for i in range(5):
                if typ == types_list[i]:
                    table.add_row(menu_cats[i], str(len(self.menu[i])), end_section=True)  # Cocktails     8
                    if typ == recipe.Recipe:
                        for index, recip in enumerate(self.menu[i]):
                            table.add_row(f"{recip.name}"
                                          f"{rich_console.standardized_spacing(recip.name, total_info_spacing)}"
                                          f"{self.menu[i][index].format_ingredients()}")
                            table.add_row()
                    else:
                        for ingredient in list_ingredients(self.menu[i], typ):
                            table.add_row(f"[{typ().format_type().lower()}]{ingredient.name}", f"[{typ().format_type().lower()}]{ingredient.format_type()}")
                            table.add_row()
                            lst.append(ingredient)
                        if len(table.rows) == 0:
                            table.add_row(Text("[None]", rich_console.styles.get("dimmed")))
                        break

        return table, lst

    # @TODO: '2 whole maraschino cherry'
    def show_recipes(self, off_menu=False):
        recipes_list = []
        recipes_table = Table()
        recipes_table.add_column("name")
        recipes_table.add_column("ingredients")
        for recipe in self.recipes:
            if off_menu:
                if self.recipes[recipe] in self.menu[0]:
                    continue
            ingredients_string = self.recipes[recipe].format_ingredients()
            recipes_table.add_row(Text(recipe, style=rich_console.styles.get("cocktails")), ingredients_string)
            recipes_list.append(self.recipes[recipe])
        return recipes_table, recipes_list

    def new_recipe(self):
        recipe_table = Table(show_header=False, box=None)
        recipe_panel = Panel(recipe_table, title="New Recipe", border_style=rich_console.styles.get("cocktails"))
        new_recipe_layout = Layout(recipe_panel)

        recipe_table.add_column("portion", vertical="middle")
        recipe_table.add_column("of")
        recipe_table.add_column("ingredient/type")
        recipe_table.add_row()  # Spacing

        type_args = set()
        type_lst = set()
        ingredient_args = commands.items_to_commands(ingredients.all_ingredients)
        for typ in ingredients.all_ingredient_types():
            obj = typ()
            type_cmd = unidecode(obj.format_type().lower())
            if type_cmd not in type_args:
                type_args.add(type_cmd)
                type_lst.add(typ)

        writing_recipe = True
        recipe_dict = {}
        while writing_recipe:
            console.print(new_recipe_layout)

            rcp_write_prompt = "Enter a type (e.g. bourbon), an ingredient (e.g. lemon, patron silver), or 'finish'"
            cmd = None
            cmds = type_args | ingredient_args
            cmds.add("back")
            cmds.add("finish")

            while cmd is None:
                cmd = commands.parse_input(rcp_write_prompt, cmds)[0]
                if cmd == "":
                    cmd = None

            if cmd == "finish":
                recipe_name = None
                while recipe_name is None:
                    recipe_name = console.input("[prompt]Name your cocktail: > ")
                    if recipe_name == "":
                        recipe_name = None

                self.recipes[recipe_name] = Recipe(name=recipe_name, r_ingredients=recipe_dict)
                return recipe_name
            elif cmd == "quit":
                self.bar_cmd.onecmd(cmd)
            elif cmd == "back":
                writing_recipe = False

            matching_obj = None
            matching_typ = None
            name = ""
            for type_arg in type_args:
                if cmd == type_arg:
                    matching_typ = commands.command_to_item(type_arg, type_lst)
                    matching_obj = matching_typ()
                    ingredient = matching_obj.format_type()

            if matching_obj is None:
                for ingredient_arg in ingredient_args:
                    if cmd == ingredient_arg:
                        matching_obj = commands.command_to_item(ingredient_arg, ingredients.all_ingredients)
                        ingredient = matching_obj.name

            if matching_obj is None:
                console.print("[error]No matching type or ingredient")
                continue

            portions_table, portions_list = matching_obj.show_portions()
            portions_list.append("back")

            portioning_panel = Panel(title=f"Portioning {ingredient}", renderable=portions_table, border_style=rich_console.styles.get("cocktails"))
            portioning_layout = Layout(portioning_panel)

            console.print(portioning_layout)
            rcp_write_prompt = f"Select a portion of {ingredient}"

            portion_command = None
            while portion_command is None:
                portion_command = commands.parse_input(rcp_write_prompt, portions_list, force_beginning=True)[0]
            if portion_command == "quit":
                self.bar_cmd.do_quit(self)
            elif portion_command == "back":
                continue
            for portion in matching_obj.get_portions():
                if portion_command == portion.lower():
                    of = "" if isinstance(matching_obj, ingredients.Fruit) and portion_command != "slice" else "of"
                    if matching_typ is not None:
                        recipe_dict[matching_typ] = matching_obj.get_portions()[portion]
                        recipe_table.add_row(f"-   {portion}", of, Text(matching_typ().format_type(),
                                                                        matching_obj.get_ing_style()))
                    else:
                        recipe_dict[matching_obj] = matching_obj.get_portions()[portion]
                        recipe_table.add_row(f"-   {portion}", of, Text(matching_obj.name,
                                                                        matching_obj.get_ing_style()))
                    recipe_table.add_row()  # Spacing

    def show_inv(self, table_settings, typ: type = Ingredient, showing_flavored=False, shop=False):
        table = Table(**table_settings)
        lst = []
        container = all_ingredients if shop else self.inventory

        table.add_column(justify="center")
        subclasses = typ.__subclasses__()
        items = list_ingredients(container, typ, type_specific=True)

        showing_flavorable_spirit = False
        if (isinstance(typ(), ingredients.Spirit) or isinstance(typ(),
                                                                ingredients.Liqueur)) and typ is not ingredients.Spirit:
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
            flavored, unflavored = ingredients.categorize_spirits(items)
            if not showing_flavored:
                table.add_row(Text(f"Flavored ({len(flavored)})",
                                   style=rich_console.styles.get("additive")), end_section=True)
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
            table.add_row(Text("[None]", rich_console.styles.get("dimmed")))

        if len(overflow_table.rows) != 0:
            if len(overflow_2.rows) != 0:
                return (table, overflow_table, overflow_2), lst
            return (table, overflow_table), lst
        else:
            return table, lst

    def table_inv(self, typ, off_menu=False):
        inv_ingredients = list_ingredients(self.inventory, typ)
        add_tool_table = Table(expand=True)
        lst = []
        for i in range(3):
            add_tool_table.add_column("Name")
            add_tool_table.add_column("Type")

        row_ings = []
        for ingredient in inv_ingredients:
            if off_menu:
                if ingredient in self.menu[ingredient.get_menu_section()]:
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

    def save_game(self):
        pass
