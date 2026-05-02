from enum import Enum

from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from unidecode import unidecode

import recipe
from bar_pkg import bar_menu, stock, occupancy, stats
from data import ingredients
from display.rich_console import console
from interface import commands
from recipe import Recipe
from utility import logger


class Screen(Enum):
    MAIN = 1
    SHOP = 2
    BAR_MENU = 3
    MENU_ADD = 4
    PLAY = 5


reputation_levels = {
    0: 0,
    1: 100
}


class Bar:
    def __init__(self, bar_name, balance=1000):
        self.bar_stats = stats.BarStats(self, bar_name, balance)
        self.stock = stock.BarStock(self)
        self.menu = bar_menu.BarMenu(self)
        self.occupancy = occupancy.Occupancy(self)
        self.recipes = {}
        self.screen = Screen.MAIN

    # <editor-fold desc="Recipes">
    # @TODO: '2 whole maraschino cherry'
    def table_recipes(self, off_menu_only=False):
        """
        Table all stored recipes, or optionally, just those that are not already on the menu currently.

        :param off_menu_only: Set true to exclude recipes already on the menu, such as when adding to the menu
        :return: A table displaying the cocktail's name and recipe, and a list of the recipe objects
        """
        recipes_list = []
        recipes_table = Table()

        recipes_table.add_column("name")
        recipes_table.add_column("ingredients")

        for recipe_name in self.recipes:
            # Skip if on the menu already, and we're only displaying off-menu drinks
            if off_menu_only and self.recipes[recipe_name] in self.menu.cocktails:
                continue
            ingredients_string = self.recipes[recipe_name].format_ingredients()
            recipes_table.add_row(Text(recipe_name, style=console.get_style("cocktails")), ingredients_string)
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
            # Table a breakdown of the ingredients so far
            recip = Recipe(name="in-progress", r_ingredients=recipe_dict)
            recipe_table = recip.breakdown_ingredients()

            recipe_panel = Panel(title="New Recipe", border_style=console.get_style("cocktails"),
                                 renderable=recipe_table)
            new_recipe_layout = Layout(recipe_panel)

            console.print(new_recipe_layout)

            # Find the ingredient to add
            rcp_write_prompt = "Enter a type (e.g. bourbon), an ingredient (e.g. lemon, patron silver), or 'finish'"
            cmds = type_args | ingredient_args
            cmds.add("back")
            cmds.add("finish")

            # Get input
            cmd = commands.input_loop(rcp_write_prompt, cmds, bar=self)[0]

            if cmd == "finish":
                recipe_name = None
                while recipe_name is None:
                    recipe_name = console.input("[prompt]Name your cocktail: > ")
                    if recipe_name == "":
                        recipe_name = None

                self.recipes[recipe_name] = recipe.create_recipe(recipe_name, recipe_dict)
                return recipe_name
            elif cmd == "back":
                writing_recipe = False

            # If not a command, try to match input to a type of ingredient
            matching_type = None
            matching_type_object = None
            for type_arg in type_args:
                if cmd == type_arg:
                    matching_type = commands.command_to_item(type_arg, type_lst)
                    matching_type_object = matching_type()
                    ingredient = matching_type_object.format_type()

            # If not a type of ingredient, match to a specific ingredient
            if matching_type_object is None:
                for ingredient_arg in ingredient_args:
                    if cmd == ingredient_arg:
                        matching_type_object = commands.command_to_item(ingredient_arg, ingredients.all_ingredients)
                        ingredient = matching_type_object.name

            if matching_type_object is None:
                console.print("[error]No matching type or ingredient")
                continue

            # Select portion
            portions_table, portions_list = matching_type_object.table_portions()
            portions_list.append("back")

            portioning_panel = Panel(title=f"Portioning {ingredient}", renderable=portions_table,
                                     border_style=console.get_style("cocktails"))
            portioning_layout = Layout(portioning_panel)

            console.print(portioning_layout)
            rcp_write_prompt = f"Select a portion of {ingredient}"

            portion_command = commands.input_loop(rcp_write_prompt, portions_list, force_beginning=True, bar=self)[0]
            if portion_command == "back":
                continue
            for portion in matching_type_object.get_portions():
                if portion_command == portion.lower():
                    if matching_type:
                        recipe_dict[type(matching_type_object)] = portion
                    else:
                        recipe_dict[matching_type_object] = portion

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

            new_recipe = recipe.create_recipe(name=cocktail_name, r_ingredients=new_ings)
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

    def make_sale(self, menu_item: ingredients.MenuItem):
        if self.stock.has_enough(menu_item):
            self.stock.pour(menu_item)
            self.bar_stats.balance += menu_item.current_price()
            logger.log(f"Balance +${menu_item.current_price()} ({self.bar_stats.balance})")
            '''self.reputation += 1
            logger.log(f"Reputation +1 ({self.reputation})")'''
            return True
        else:
            self.occupancy.print_msg(f"[error]Not enough {menu_item.name}![/error]")
            return False
