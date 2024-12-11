from rich.layout import Layout
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from unidecode import unidecode

import bar_menu
import bar_stock
import commands
import ingredients
from rich_console import console, styles, Screen
from recipe import Recipe

global prompt


class Bar:
    def __init__(self, name, balance=1000):
        self.name = name
        self.balance = balance  # Float: current balance in dollars
        self.reputation = 0
        self.stock = bar_stock.BarStock(self)
        self.recipes = {}
        self.menu = bar_menu.BarMenu(self)
        self.screen = Screen.MAIN


    # <editor-fold desc="Recipes">
    # @TODO: '2 whole maraschino cherry'
    def show_recipes(self, off_menu=False):
        recipes_list = []
        recipes_table = Table()
        recipes_table.add_column("name")
        recipes_table.add_column("ingredients")
        for recipe in self.recipes:
            if off_menu:
                if self.recipes[recipe] in self.menu.cocktails:
                    continue
            ingredients_string = self.recipes[recipe].format_ingredients()
            recipes_table.add_row(Text(recipe, style=styles.get("cocktails")), ingredients_string)
            recipes_list.append(self.recipes[recipe])
        return recipes_table, recipes_list

    def new_recipe(self):
        recipe_table = Table(show_header=False, box=None)
        recipe_panel = Panel(recipe_table, title="New Recipe", border_style=styles.get("cocktails"))
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

            cmd = commands.input_loop(rcp_write_prompt, cmds, bar=self)[0]

            if cmd == "finish":
                recipe_name = None
                while recipe_name is None:
                    recipe_name = console.input("[prompt]Name your cocktail: > ")
                    if recipe_name == "":
                        recipe_name = None

                self.recipes[recipe_name] = Recipe(name=recipe_name, r_ingredients=recipe_dict)
                return recipe_name
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

            portioning_panel = Panel(title=f"Portioning {ingredient}", renderable=portions_table,
                                     border_style=styles.get("cocktails"))
            portioning_layout = Layout(portioning_panel)

            console.print(portioning_layout)
            rcp_write_prompt = f"Select a portion of {ingredient}"

            portion_command = commands.input_loop(rcp_write_prompt, portions_list, force_beginning=True, bar=self)[0]
            if portion_command == "back":
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

    # </editor-fold>

    def save(self):
        pass
