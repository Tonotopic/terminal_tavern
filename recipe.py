from typing import override

from rich_console import console, standardized_spacing
from ingredients import Ingredient, MenuItem


class Recipe(MenuItem):
    def __init__(self, name=None, r_ingredients: dict[type[Ingredient] or Ingredient, float] = None):
        super().__init__()
        self.name = name
        self.r_ingredients = r_ingredients
        self.markup = 0.0
        self.markdown = 0.0
        self.formatted_markdown = ""


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

    @override
    def list_item(self, expanded=False):
        name = self.name
        total_spacing = console.size[0] - 21 if expanded else int(console.size[0] / 2) - 13
        if expanded:
            cocktail_spacing = int(0.3 * total_spacing)
            ingredient_spacing = int(0.7 * total_spacing) - 6

            ingredients = self.format_ingredients(markup=False)
            if len(ingredients) > ingredient_spacing:
                ingredients = ingredients[:-3] + "..."

            return (
                f"[cocktail]{name}[/cocktail]{standardized_spacing(name, cocktail_spacing)}{self.format_ingredients()}"
                f"{standardized_spacing(ingredients, ingredient_spacing)}"
                f"{self.list_price(expanded=True)}")
        else:
            return (f"[cocktail]{name}[/cocktail]{standardized_spacing(name, total_spacing - 6)}"
                    f"{self.list_price(expanded=False)}")

    def format_type(self, plural=False):
        if plural:
            return "Cocktails"
        else:
            return "Cocktail"

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

        # Excludes the comma+space if at the end
        formatted_ing_string = ""
        for index, char in enumerate(ingredients_string):
            if index < len(ingredients_string) - 2:
                formatted_ing_string += char

        return formatted_ing_string

    def select_ingredients(self):
        for r_ingredient in self.r_ingredients:
            if isinstance(r_ingredient, type):
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
