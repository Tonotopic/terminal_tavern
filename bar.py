import ingredients


class Bar:
    def __init__(self, inventory, balance, menu):
        self.inventory = inventory  # Dictionary: {product_name: fluid_ounces}
        self.balance = balance  # Float: current balance in dollars
        self.menu = menu  # List of Recipe objects

    def purchase(self):
        pass


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
            if isinstance(required_ingredient, type):  # Check if it's a type
                found_match = False
                for provided_ingredient in provided_ingredients:
                    if isinstance(provided_ingredient,
                                  required_ingredient):  # if provided ingredient is an instance of the required type
                        found_match = True
                        break  # Stop checking further for this ingredient
                if not found_match:
                    return False  # Missing required ingredient type
            else:  # It's a specific ingredient
                if required_ingredient not in provided_ingredients:
                    return False  # Missing specific ingredient
                # Add quantity check if needed

        return True  # All ingredients are valid

    def make(self):
        pass

    def calculate_abv(self):
        """Calculates the ABV of the recipe using ingredient ABVs."""
        total_alcohol_fl_oz = 0
        total_volume_fl_oz = 0

        for ingredient, fluid_ounces in self.r_ingredients.items():  # Iterate through Ingredient objects
            if hasattr(ingredient, "abv"):  # Check if ingredient has ABV
                alcohol_fl_oz = fluid_ounces * (ingredient.abv / 100)
                total_alcohol_fl_oz += alcohol_fl_oz

            total_volume_fl_oz += fluid_ounces

        if total_volume_fl_oz == 0:
            return 0

        abv = (total_alcohol_fl_oz / total_volume_fl_oz) * 100
        return abv
