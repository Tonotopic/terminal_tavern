import ingredients
from ingredients import all_ingredients, get_ingredient, load_ingredients_from_db
from bar import Recipe

load_ingredients_from_db()

for ingredient in all_ingredients.values():
    print(ingredient.description())

manhattan = Recipe(
    "Manhattan",
    {
        ingredients.Whiskey: 2.0,
        ingredients.Vermouth: 1.0,
        get_ingredient("Angostura"): 1 / 30,
        get_ingredient("maraschino cherry"): 1.0
    }
)


