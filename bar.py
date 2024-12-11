import rich.pretty

import ingredients
from rich.layout import Layout
from rich_console import console
from rich.text import Text
from rich.panel import Panel


class Bar:
    def __init__(self, balance=1000):
        self.inventory = {}  # Dictionary: {ingredient_object: fluid_ounces}
        self.balance = balance  # Float: current balance in dollars
        self.menu = {}  # List of Recipe objects

    def purchase(self):
        purchase_layout = Layout(name="purchase_layout")
        purchase_layout.split_column(
            Layout(name="purchase_header"),
            Layout(name="purchase_screen")
        )
        purchase_layout["purchase_screen"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        purchase_layout["left"].split_column(
            Layout(name="inventory_header", renderable=Text("Your bar", justify="center")),
            Layout(renderable=rich.pretty.Pretty(self.inventory), name="inventory")
        )
        purchase_layout["right"].split_column(
            Layout(name="shop_header", renderable=Text("Available for purchase", justify="center")),
            Layout(name="shop")
        )
        console.print(purchase_layout)

    def list_ingredients(self, typ):
        for ingredient in self.inventory:
            if isinstance(ingredient, typ):
                print(ingredient.description())


class Recipe:
    def __init__(self, name, r_ingredients: dict[type[ingredients.Ingredient] | ingredients.Ingredient, float]):
        self.name = name
        self.r_ingredients = r_ingredients

    def select_ingredients(self):
        for r_ingredient in self.r_ingredients:
            if isinstance(r_ingredient, type):
                pass

    def check_ingredients(self, provided_ingredients: dict[ingredients.Ingredient, float]):
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
