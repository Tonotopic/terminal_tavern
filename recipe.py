from typing import override
from rich.table import Table
from rich.text import Text

import flavors
import ingredients
import logger
import rich_console
from rich_console import console, standardized_spacing, styles
from ingredients import Ingredient, MenuItem, Fruit


class Recipe(MenuItem):
    def __init__(self, name=None, r_ingredients: dict[type[Ingredient] or Ingredient, str] = None):
        super().__init__()
        self.name = name
        self.r_ingredients = r_ingredients
        self.markup = 0.0
        self.markdown = 0.0
        self.formatted_markdown = ""

    @override
    def list_item(self, expanded=False):
        name = self.name
        total_spacing = console.size[0] - 22 if expanded else int(console.size[0] / 2) - 14
        if expanded:
            cocktail_spacing = int(0.3 * total_spacing)
            ingredient_spacing = int(0.7 * total_spacing) - 5

            ingredients = self.format_ingredients(markup=False)
            formatted_ingredients = self.format_ingredients()
            if len(ingredients) > ingredient_spacing:
                hidden_chars = len(ingredients) - ingredient_spacing
                formatted_ingredients = formatted_ingredients[:-(hidden_chars + 3)] + "..."

            return (
                f"[cocktails]{name}[/cocktails]{standardized_spacing(name, cocktail_spacing)}{formatted_ingredients}"
                f"{standardized_spacing(ingredients, ingredient_spacing)}"
                f"{self.list_price(expanded=True)}")
        else:
            return (f"[cocktails]{name}[/cocktails]{standardized_spacing(name, total_spacing - 5)}"
                    f"{self.list_price(expanded=False)}")

    def format_type(self, plural=False):
        if plural:
            return "Cocktails"
        else:
            return "Cocktail"

    def get_style(self):
        return styles.get("cocktails")

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
                cost_value += portion * r_ingredient.price_per_oz()
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
            profit_base = 2.5 * cost_value
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
        recipe_table = Table(show_header=False, box=None)
        recipe_table.add_column("portion", vertical="middle")
        recipe_table.add_column("of")
        recipe_table.add_column("ingredient/type")
        recipe_table.add_column("cost")
        recipe_table.add_row()  # Spacing

        money_style = rich_console.styles.get("money")

        if len(self.r_ingredients) > 0:
            for ingredient in self.r_ingredients:
                if self.r_ingredients[ingredient] in ["Crushed", "Whole"]:
                    of = ""
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
                    cost = "~${:.2f}".format(ingredient.get_portions()[self.r_ingredients[ingredient]] * ingredient.price_per_oz())

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

    def calculate_abv(self):
        """Calculates the ABV of the recipe using ingredient ABVs."""
        total_alcohol_fl_oz = 0
        total_volume_fl_oz = 0

        for ingredient, portion in self.r_ingredients.items():
            fl_oz = ingredient.get_portions()[portion]
            if hasattr(ingredient, "abv"):
                alcohol_fl_oz = fl_oz * (ingredient.abv / 100)
                total_alcohol_fl_oz += alcohol_fl_oz

            total_volume_fl_oz += fl_oz

        if total_volume_fl_oz == 0:
            return 0

        abv = (total_alcohol_fl_oz / total_volume_fl_oz) * 100
        return abv

    def generate_taste_profile(self):
        logger.log(f"Generating taste profile for {self.name}:")
        taste_profile = {}

        for ingredient in self.r_ingredients:

            if isinstance(ingredient, Ingredient):
                name = ingredient.name
                obj = ingredient
            elif isinstance(ingredient, type):
                obj = ingredient()
                name = obj.format_type()

            volume = round(obj.get_portions()[self.r_ingredients[ingredient]], 2)

            for typ in [ingredients.Liqueur, ingredients.Spice]:
                if isinstance(ingredient, typ) or (isinstance(ingredient, type) and ingredient == typ):
                    if volume < 1:
                        volume = volume * 50

            for taste in flavors.tastes:
                points = 0

                name_to_type = {typ().format_type(): typ for typ in ingredients.all_ingredient_types()}
                for word in flavors.tastes[taste]:
                    desc_weight = 0
                    if word in name_to_type:
                        typ = name_to_type[word]
                        if isinstance(obj, typ):
                            logger.log(f"      {name} is a {word} - adds {taste}")
                            desc_weight += 3
                    if obj.flavor != "":
                        if word in obj.flavor:
                            desc_weight += 5
                    if obj.character:
                        if word in obj.character:
                            desc_weight += 2
                    if obj.notes:
                        if word in obj.notes:
                            desc_weight += 0.75
                    term_weight = flavors.tastes[taste][word]
                    points_added = round(term_weight * desc_weight * volume, 2)
                    points += points_added
                    if desc_weight > 0:
                        logger.log(f"        {term_weight}(term) * {desc_weight}(desc) * {volume}(vol) = {points_added} points in {taste} from \"{word}\" in {name}")

                if points > 0:
                    try:
                        taste_profile[taste] += points
                    except KeyError:
                        taste_profile[taste] = points
                    logger.log(f"    {points} points in {taste} from {name}")

        return taste_profile
