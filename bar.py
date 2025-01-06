from unidecode import unidecode
from enum import Enum

from rich.layout import Layout
from rich.text import Text
from rich.panel import Panel
from rich.table import Table

import bar_menu
import logger
import stock
import commands
import ingredients
from rich_console import console, styles
from recipe import Recipe

global prompt


class Screen(Enum):
    MAIN = 1
    SHOP = 2
    BAR_MENU = 3
    ADD = 4


reputation_levels = {
    0: 0,
    1: 100
}


class Bar:
    def __init__(self, name, balance=1000):
        self.name = name
        self.balance = balance  # Float: current balance in dollars
        self.reputation = 0
        self.rep_level = 0
        self.stock = stock.BarStock(self)
        self.recipes = {}
        self.menu = bar_menu.BarMenu(self)
        self.screen = Screen.MAIN

    # <editor-fold desc="Recipes">
    # @TODO: '2 whole maraschino cherry'
    def table_recipes(self, off_menu=False):
        """
        Table all stored recipes, or just those that are not currently on the menu.

        :param off_menu: Set true to exclude recipes already on the menu, such as when adding to the menu
        :return: A table displaying the cocktail's name and recipe, and a list of the recipe objects
        """
        recipes_list = []
        recipes_table = Table()
        recipes_table.add_column("name")
        recipes_table.add_column("ingredients")
        for recipe_name in self.recipes:
            if off_menu and self.recipes[recipe_name] in self.menu.cocktails:
                continue
            ingredients_string = self.recipes[recipe_name].format_ingredients()
            recipes_table.add_row(Text(recipe_name, style=styles.get("cocktails")), ingredients_string)
            recipes_table.add_row()
            recipes_list.append(self.recipes[recipe_name])
        return recipes_table, recipes_list

    def new_recipe(self):
        """
        Allow the user to search ingredients and assign quantities to a new recipe.

        :return: The name of the newly added recipe
        """
        logger.log("Drawing new recipe screen...")

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
            recipe = Recipe(name="in-progress", r_ingredients=recipe_dict)
            recipe_table = recipe.breakdown_ingredients()

            recipe_panel = Panel(title="New Recipe", border_style=styles.get("cocktails"), renderable=recipe_table)
            new_recipe_layout = Layout(recipe_panel)

            console.print(new_recipe_layout)

            rcp_write_prompt = "Enter a type (e.g. bourbon), an ingredient (e.g. lemon, patron silver), or 'finish'"
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

            matching_typ = None
            matching_obj = None
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
                    if matching_typ:
                        recipe_dict[type(matching_obj)] = portion
                    else:
                        recipe_dict[matching_obj] = portion

    def reload_ingredients(self):
        """
        Recreate all ingredient objects in stored recipes, the bar menu, and inventory, to update any changes and ensure
        that all instances of an ingredient point to the same object.
        """
        self.reload_recipes()
        self.menu.reload()
        self.stock.reload()

    def reload_recipes(self):
        """
        Reload the ingredient objects in all stored recipes to stay up-to-date with the database.
        """
        new_recipes = {}
        for cocktail_name in self.recipes:
            recip = self.recipes[cocktail_name]
            new_ings = {}

            for r_ing in recip.r_ingredients:
                if isinstance(r_ing, type):
                    new_ings[r_ing] = recip.r_ingredients[r_ing]
                elif isinstance(r_ing, ingredients.Ingredient):
                    for db_ing in ingredients.all_ingredients:
                        if r_ing.name == db_ing.name:
                            new_ings[db_ing] = recip.r_ingredients[r_ing]

            new_recipe = Recipe(name=cocktail_name, r_ingredients=new_ings)
            new_recipe.markup = recip.markup
            new_recipe.markdown = recip.markdown
            new_recipe.formatted_markdown = recip.formatted_markdown
            new_recipes[cocktail_name] = new_recipe

        self.recipes = new_recipes
        logger.log("Recipes reloaded.")

    # </editor-fold>

    def get_screen(self):
        """Get the name of the screen the bar is currently on."""
        return self.screen.name

    def set_screen(self, screen_arg: str):
        """Set the bar screen value."""
        screen_arg = screen_arg.strip().upper()
        for screen in Screen:
            if screen_arg == screen.name:
                self.screen = screen
                break

    def start_day(self):
        if self.menu.check_stock():
            return True
        else:
            return False

    def make_sale(self, menu_item: ingredients.MenuItem):
        if self.stock.has_enough(menu_item):
            self.stock.pour(menu_item)
            self.balance += menu_item.current_price()
            logger.log(f"Balance +${menu_item.current_price()} ({self.balance})")
            self.reputation += 1
            logger.log(f"Reputation +1 ({self.reputation})")
            return True
