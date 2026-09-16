from data.ingredients import all_ingredient_types, all_ingredients
from interface.commands import command_to_item
from recipe import create_recipe

DEFAULT_RECIPE_DICTS = {
    "Manhattan": {
        command_to_item("whiskey", all_ingredient_types()): "Shot",
        command_to_item("sweet vermouth", all_ingredient_types()): "1oz",
        command_to_item("angostura", all_ingredients): "Generous Dash",
        command_to_item("maraschino cherry", all_ingredients): "Whole",
    },
    "Old Fashioned": {
        command_to_item("whiskey", all_ingredient_types()): "Shot",
        command_to_item("angostura", all_ingredients): "Generous Dash",
        command_to_item("simple syrup", all_ingredients): "Teaspoon",
        command_to_item("orange", all_ingredients): "Slice",
    },
    "Whiskey Sour": {
        command_to_item("whiskey", all_ingredient_types()): "Shot",
        command_to_item("lemon", all_ingredients): "Juice (1oz)",
        command_to_item("simple syrup", all_ingredients): "Half ounce",
    },
    "Martini": {
        command_to_item("gin", all_ingredient_types()): "Shot",
        command_to_item("dry vermouth", all_ingredient_types()): "Half ounce",
        command_to_item("green olive", all_ingredients): "Whole",
    },
    "Negroni": {
        command_to_item("gin", all_ingredient_types()): "1oz",
        command_to_item("campari", all_ingredients): "1oz",
        command_to_item("sweet vermouth", all_ingredient_types()): "1oz",
        command_to_item("orange", all_ingredients): "Slice"
    },
    "Tom Collins": {
        command_to_item("gin", all_ingredient_types()): "Shot",
        command_to_item("lemon", all_ingredients): "Juice (1oz)",
        command_to_item("simple syrup", all_ingredients): "1oz",
        command_to_item("club soda", all_ingredients): "2oz",
    },
    "Margarita": {
        command_to_item("tequila", all_ingredient_types()): "Shot",
        command_to_item("cointreau", all_ingredients): "1oz",
        command_to_item("lime", all_ingredients): "Juice (1oz)"
    },
    "Moscow Mule": {
        command_to_item("vodka", all_ingredient_types()): "Shot",
        command_to_item("lime", all_ingredients): "Juice (Tbsp)",
        command_to_item("ginger ale", all_ingredient_types()): "4oz",
        command_to_item("lime", all_ingredients): "Slice",
    },
    "Jack & Coke": {
        command_to_item("whiskey", all_ingredient_types()): "Shot",
        command_to_item("cola", all_ingredient_types()): "4oz",
        command_to_item("lemon", all_ingredients): "Slice"
    },
    "Rum & Coke": {
        command_to_item("rum", all_ingredient_types()): "Shot",
        command_to_item("cola", all_ingredient_types()): "4oz",
        command_to_item("lime", all_ingredients): "Juice (Tbsp)",
    },
    "Vodka Cranberry": {
        command_to_item("vodka", all_ingredient_types()): "Shot",
        command_to_item("cranberry", all_ingredients): "Juice (4oz)",
        command_to_item("lime", all_ingredients): "Juice (Tbsp)",
    }
}

DEFAULT_RECIPES = []
for name in DEFAULT_RECIPE_DICTS:
    recipe = create_recipe(name, DEFAULT_RECIPE_DICTS[name])
    DEFAULT_RECIPES.append(recipe)
