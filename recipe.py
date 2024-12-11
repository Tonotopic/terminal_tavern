from rich.text import Text

from rich_console import console
from ingredients import Ingredient


class Recipe:
    def __init__(self, name=None, r_ingredients: dict[type[Ingredient] or Ingredient, float] = None):
        self.name = name
        self.r_ingredients = r_ingredients

    def format_ingredients(self):
        r_ings = []
        for entry in self.r_ingredients:
            if isinstance(entry, type):
                r_ings.append(f"[{entry().get_ing_style()}]{entry().format_type()}")
            elif isinstance(entry, Ingredient):
                r_ings.append(f"[{entry.get_ing_style()}]{entry.name}")
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



