from decimal import Decimal
from typing import override

from rich.table import Table
from rich.text import Text

from data import ingredients, flavors
from data.ingredients import Ingredient, MenuItem
from display import rich_console
from display.rich_console import console, standardized_spacing
from utility import logger


# TODO Specify ingredients like Coffee liqueur

class Recipe(MenuItem):
    def __init__(self, name=None, r_ingredients: dict[type[Ingredient] or Ingredient, str] = None):
        super().__init__()
        self.name = name
        self.r_ingredients = r_ingredients
        self.taste_profile = None
        self.markup = 0.0
        self.markdown = 0.0
        self.formatted_markdown = ""

    # <editor-fold desc="Display">
    @override
    def list_item(self, expanded=False):
        """Displays cocktail name and price, including ingredients if viewing the full-screen menu."""
        name = self.name
        total_spacing = console.size[0] - 29 if expanded else int(console.size[0] // 2) - 19
        if expanded:
            cocktail_spacing = total_spacing // 4
            ingredient_spacing = 3 * cocktail_spacing
            cocktail_spacing += total_spacing % 4
            trunc_index = ingredient_spacing

            ingredients = self.format_ingredients(markup=False)
            formatted_ingredients = self.format_ingredients()
            if len(ingredients) > ingredient_spacing:
                trunc_index -= 2
                f_trunc_index = -2
                true_str_index = 0
                in_markup = False
                for i, char in enumerate(formatted_ingredients):
                    f_trunc_index += 1
                    if true_str_index >= ingredient_spacing - 4:
                        break
                    if not in_markup and char == "[":
                        in_markup = True
                    elif in_markup:
                        if char == "]":
                            in_markup = False
                    elif not in_markup:
                        true_str_index += 1

                formatted_ingredients = formatted_ingredients[:(f_trunc_index)] + "[dimmed]..."
            return (
                f"[cocktails]{name}[/cocktails]{standardized_spacing(name, cocktail_spacing)}{formatted_ingredients}"
                f"{standardized_spacing(ingredients[:trunc_index], ingredient_spacing)}"
                f"{self.list_price(expanded=True)}")
        else:
            return (f"[cocktails]{name}[/cocktails]{standardized_spacing(name, total_spacing)}"
                    f"{self.list_price(expanded=False)}")

    @staticmethod
    def format_type(plural=False):
        if plural:
            return "Cocktails"
        else:
            return "Cocktail"

    @staticmethod
    def get_style():
        return console.get_style("cocktails")

    # </editor-fold>

    # <editor-fold desc="Price">
    @override
    def cost_value(self):
        cost_value = 0
        variable = False
        for r_ingredient in self.r_ingredients:
            if isinstance(r_ingredient, type):
                cost_value += 0
                variable = True
            elif isinstance(r_ingredient, Ingredient):
                portion = r_ingredient.get_portions()[self.r_ingredients[r_ingredient]]
                cost_value += portion * r_ingredient.price_per_oz("max")
            else:
                console.print("[error]Recipe cost value received an ingredient not registering as type or ingredient")
        return cost_value, variable

    @override
    def profit_base(self):
        cost_value, variable = self.cost_value()
        profit_base = None
        if cost_value <= 1.50:
            profit_base = 4.50
        elif 1.50 < cost_value <= 4:
            profit_base = 3 * cost_value
        elif cost_value > 4:
            profit_base = 2 * cost_value
        return profit_base, variable

    @override
    def list_price(self, expanded=False):
        variable = self.profit_base()[1]
        price = self.current_price()
        formatted_price = f"[money]${"{:.2f}".format(price)}"
        if variable:
            formatted_price += "+"

        if self.markdown == 0 or expanded is False:
            return formatted_price
        else:
            return f"{formatted_price} ({self.formatted_markdown})"

    # </editor-fold>

    # <editor-fold desc="Ingredients">
    def format_ingredients(self, markup=True):
        """Gets a string of comma-separated recipe ingredients, with optional markup characters to delineate types by color."""
        r_ings = []
        for entry in self.r_ingredients:
            if isinstance(entry, type):
                if markup:
                    r_ings.append(f"[{entry().get_style()}]{entry().format_type()}")
                else:
                    r_ings.append(entry().format_type())
            elif isinstance(entry, Ingredient):
                if markup:
                    r_ings.append(f"[{entry.get_style()}]{entry.name}")
                else:
                    r_ings.append(entry.name)
            else:
                console.print("[error]Recipe ingredients contains item not registering as ingredient or type")
        ingredients_string = ""
        for index, ing_name in enumerate(r_ings):
            ingredients_string += f"{ing_name}, "

        # Excludes the comma+space if at the end
        formatted_ing_string = ""
        for index, char in enumerate(ingredients_string):
            if index < len(ingredients_string) - 2:
                formatted_ing_string += char

        return formatted_ing_string

    def breakdown_ingredients(self):
        """Table ingredient portions (i.e. "shot of Bourbon") and costs, totaling cost at the bottom."""
        recipe_table = Table(show_header=False, box=None)
        recipe_table.add_column("portion", vertical="middle")
        recipe_table.add_column("of")
        recipe_table.add_column("ingredient/type")
        recipe_table.add_column("cost")
        recipe_table.add_row()  # Spacing

        money_style = console.get_style("money")

        if len(self.r_ingredients) > 0:
            for ingredient in self.r_ingredients:
                if self.r_ingredients[ingredient] in ["Crushed", "Whole"]:
                    of = ""
                elif self.r_ingredients[ingredient] in ["On the Rim"]:
                    of = ":"
                else:
                    of = "of"

                if isinstance(ingredient, type):
                    obj = ingredient()
                    name = obj.format_type()
                    style = obj.get_style()
                    cost = "?"
                else:
                    name = ingredient.name
                    style = ingredient.get_style()
                    cost = "~${:.2f}".format(
                        ingredient.get_portions()[self.r_ingredients[ingredient]] * ingredient.price_per_oz("max"))

                recipe_table.add_row(f"-   {self.r_ingredients[ingredient]}", of, Text(name, style),
                                     Text(cost, money_style))
                recipe_table.add_row()  # Spacing

            cost_value = self.cost_value()
            variable_tag = "+" if cost_value[1] else ""
            recipe_table.add_row("Cost:", Text("${:.2f}".format(cost_value[0]) + variable_tag, money_style))
            recipe_table.add_row()
            recipe_table.add_row("Price:", Text("${:.2f}".format(self.profit_base()[0]) + variable_tag, money_style))

        return recipe_table

    # </editor-fold>

    # <editor-fold desc="Calculations">
    def calculate_abv(self):
        """Calculates the ABV of the recipe using ingredient ABVs."""
        total_alcohol_fl_oz = 0
        total_volume_fl_oz = 0

        for ingredient, portion in self.r_ingredients.items():
            if isinstance(ingredient, Ingredient):
                obj = ingredient
            elif isinstance(ingredient, type):
                obj = ingredient()

            fl_oz = obj.get_portions()[portion]

            if hasattr(ingredient, "abv"):
                alcohol_fl_oz = fl_oz * (ingredient.abv / 100)
                total_alcohol_fl_oz += alcohol_fl_oz

            total_volume_fl_oz += fl_oz

        if total_volume_fl_oz == 0:
            return 0

        abv = (total_alcohol_fl_oz / total_volume_fl_oz) * 100
        return abv

    def generate_taste_profile(self):
        """
        Generate a dict of tastes (i.e. fruity, bitter) present in the cocktail, and corresponding weight values.
        """

        taste_profile = {}

        for ingredient in self.r_ingredients:
            if isinstance(ingredient, type):
                continue

            logger.log(f"Generating taste profile for {self.name}:")

            volume = round(Decimal(ingredient.get_portions()[self.r_ingredients[ingredient]]), 2)

            for typ in [ingredients.Liqueur, ingredients.Spice]:
                if isinstance(ingredient, typ) or (isinstance(ingredient, type) and ingredient == typ):
                    if typ in [ingredients.Liqueur, ingredients.Spice]:
                        if volume < 0.2:
                            volume = round(volume * 20, 2)
                        elif 0.2 < volume < 0.5:
                            volume = round(volume * 10, 2)

            ing_profile = dict(Ingredient.generate_taste_profile(ingredient, volume))
            for taste in ing_profile:
                points = ing_profile[taste]
                try:
                    taste_profile[taste] += points
                except KeyError:
                    taste_profile[taste] = Decimal()
                    taste_profile[taste] += points
                logger.log(f"    {points} points in {taste} from {ingredient.name}")

        sorted_taste_profile = dict(sorted(taste_profile.items(), key=lambda x: x[1], reverse=True))
        return sorted_taste_profile

    def print_taste_profile(self):
        """Print the item's tastes and their values, in order and in color markup."""
        taste_spacing = 15

        string = ""
        for taste in self.taste_profile:
            points = self.taste_profile[taste]
            # points = points.normalize()
            style = console.get_style(taste)
            string = string + (
                f"[{style}]{taste}[/{style}]{standardized_spacing(taste, taste_spacing)}=    "
                f"{points}\n")
        return string


def create_recipe(name=None, r_ingredients: dict[type[Ingredient] or Ingredient, str] = None):
    recipe = Recipe(name, r_ingredients)
    recipe.taste_profile = recipe.generate_taste_profile()
    return recipe

    # </editor-fold>
