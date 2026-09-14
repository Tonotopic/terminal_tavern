from data.ingredients import all_ingredient_types, all_ingredients
from interface.commands import command_to_item
from recipe import create_recipe

DEFAULT_RECIPE_DICTS = {
    "Manhattan": {
        command_to_item("whiskey", all_ingredient_types()): "Shot",
        command_to_item("sweet vermouth", all_ingredient_types()): "1oz",
        command_to_item("angostura", all_ingredients): "Generous Dash",
        command_to_item("maraschino cherry", all_ingredients): "Whole",
    }
}

DEFAULT_RECIPES = []
for name in DEFAULT_RECIPE_DICTS:
    recipe = create_recipe(name, DEFAULT_RECIPE_DICTS[name])
    DEFAULT_RECIPES.append(recipe)
