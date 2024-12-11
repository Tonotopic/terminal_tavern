from typing import override

from rich_console import console, quarter_round, standardized_spacing
from ingredients import Ingredient, MenuItem


class Recipe(MenuItem):
    def __init__(self, name=None, r_ingredients: dict[type[Ingredient] or Ingredient, float] = None):
        self.name = name
        self.r_ingredients = r_ingredients
        self.price = "{:.2f}".format(quarter_round(self.profit_base()[0]))

    @override
    def cost_value(self):
        cost_value = 0
        variable = False
        for r_ingredient in self.r_ingredients:
            if isinstance(r_ingredient, type):
                cost_value += 0
                variable = True
            elif isinstance(r_ingredient, Ingredient):
                portion = self.r_ingredients[r_ingredient]
                cost_value += portion * r_ingredient.price_per_oz()
            else:
                console.print("[error]Recipe cost value received an ingredient not registering as type or ingredient")
        return cost_value, variable

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

    def list_price(self):
        profit_base, variable = self.profit_base()
        if variable:
            return f"[money]${self.price}+"
        else:
            return f"[money]${self.price}"

    def format_ingredients(self, markup=True):
        r_ings = []
        for entry in self.r_ingredients:
            if isinstance(entry, type):
                if markup:
                    r_ings.append(f"[{entry().get_ing_style()}]{entry().format_type()}")
                else:
                    r_ings.append(entry().format_type())
            elif isinstance(entry, Ingredient):
                if markup:
                    r_ings.append(f"[{entry.get_ing_style()}]{entry.name}")
                else:
                    r_ings.append(entry.name)
            else:
                console.print("[error]Recipe ingredients contains item not registering as ingredient or type")
        ingredients_string = ""
        for index, ing_name in enumerate(r_ings):
            ingredients_string += f"{ing_name}, "

        # Removes the comma+space if at the end
        formatted_ing_string = ""
        for index, char in enumerate(ingredients_string):
            if index < len(ingredients_string) - 2:
                formatted_ing_string += char

        return formatted_ing_string

    def list_item(self):
        name = self.name
        cocktail_spacing = 30
        ingredient_spacing = 70
        listing = (f"[cocktail]{name}[/cocktail]{standardized_spacing(name, cocktail_spacing)}{self.format_ingredients()}"
                   f"{standardized_spacing(self.format_ingredients(markup=False), ingredient_spacing)}"
                   f"{self.list_price()}")
        return listing

    def select_ingredients(self):
        for r_ingredient in self.r_ingredients:
            if isinstance(r_ingredient, type):
                pass

    def check_ingredients(self, provided_ingredients: dict[Ingredient, float]):
        """Checks if provided ingredients satisfy the recipe requirements."""
        for required_ingredient, quantity in self.r_ingredients.items():
            if isinstance(required_ingredient, type):  # Check if requirement is a type (accepts any)
                found_match = False
                for provided_ingredient in provided_ingredients:
                    if isinstance(provided_ingredient,
                                  required_ingredient):
                        found_match = True
                        break  # Stop checking further for this ingredient
                if not found_match:
                    return False  # No ingredient of the right type provided
            else:  # Specific ingredient required
                if required_ingredient not in provided_ingredients:
                    return False  # Missing specific ingredient
                # Add quantity check if needed

        return True  # All ingredients are valid

    def make(self):
        provided_ingredients = {}
        if self.check_ingredients(provided_ingredients):
            pass

    def calculate_abv(self):
        """Calculates the ABV of the recipe using ingredient ABVs."""
        total_alcohol_fl_oz = 0
        total_volume_fl_oz = 0

        for ingredient, fluid_ounces in self.r_ingredients.items():
            if hasattr(ingredient, "abv"):
                alcohol_fl_oz = fluid_ounces * (ingredient.abv / 100)
                total_alcohol_fl_oz += alcohol_fl_oz

            total_volume_fl_oz += fluid_ounces

        if total_volume_fl_oz == 0:
            return 0

        abv = (total_alcohol_fl_oz / total_volume_fl_oz) * 100
        return abv
