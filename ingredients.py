from typing import override
import sqlite3
from rich_console import ing_styles_dict
import inspect


# <editor-fold desc="Ingredients">
class Ingredient:
    def __init__(self, ingredient_id=None, name=None, image=None, character=None, volumes=None):
        self.ingredient_id = ingredient_id
        self.name = name
        self.image = image
        self.character = character
        if volumes is None:
            self.volumes = {}

    def a(self):
        """Determines whether "a" or "an" should be printed just before the character attribute."""
        if self.character[0] in "aeiou" or self.character.startswith("herb"):
            return "an"
        else:
            return "a"

    def description(self):  # {Name} is a/an {character} {type}.
        style = self.get_ing_style()
        desc = (f"[{style}][italic]{self.name.capitalize()}[/{style}][/italic] "
                f"is {self.a()} {self.character} "
                f"[{style}]{self.format_type().lower()}[/{style}].")
        return desc

    def format_type(self):
        return type(self).__name__

    def get_ing_style(self):
        """Gets the style for the given type or its nearest parent in the theme."""
        typ = self.format_type().lower()
        if typ in ing_styles_dict:
            return typ
        else:
            for parent_class in type(self).__bases__:
                parent_object = parent_class()
                style = parent_object.get_ing_style()
                if style:
                    return style
        return self.format_type().lower()

    def get_attributes(self):
        """Returns a list of attribute values in the correct order for the constructor."""
        signature = inspect.signature(type(self).__init__)
        parameters = signature.parameters
        attribute_values = [
            repr(getattr(self, param.name))
            for param in parameters.values()
            if param.kind == param.POSITIONAL_OR_KEYWORD and param.name != 'self'
        ]
        return attribute_values

    def __rich__(self):
        return


# <editor-fold desc="Drinks">
class Drink(Ingredient):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, volumes=None):
        super().__init__(ingredient_id, name, image, character, volumes)
        self.flavor = flavor
        if flavor is None:
            self.flavor = ""
        self.notes = notes

    def format_flavor(self):  # Add the necessary space after flavor if there is one
        if self.flavor:
            return f"{self.flavor} "
        else:
            return ""

    @override
    def description(self):  # Add flavor when applicable
        style = self.get_ing_style()
        desc = (f"[{style}][italic]{self.name}[/{style}][/italic] "
                f"is {self.a()} {self.character} "
                f"[{style}]{self.format_flavor()}{self.format_type().lower()}[/{style}].")
        return desc


# <editor-fold desc="Alcohols">
class Alcohol(Drink):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, volumes)
        self.abv = abv


    def notes_desc(self):
        return f" with notes of {self.notes}"

    def abv_desc(self):
        if self.abv is not None:
            return f"It is [abv]{self.abv}% ABV[/abv]"

    @override
    def description(self):  # Remove the punctuation and add notes and ABV
        desc = super().description()[:-1]
        desc += f"{self.notes_desc()}. {self.abv_desc()}."
        return desc


class Beer(Alcohol):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Stout(Beer):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class MilkStout(Beer):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Milk Stout"


class Ale(Beer):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class BlondeAle(Ale):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Blonde Ale"


# <editor-fold desc="Wine">
class Wine(Alcohol):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Chardonnay(Wine):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class PinotNoir(Wine):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Pinot Noir"


class Merlot(Wine):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Rose(Wine):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Rosé"


class Riesling(Wine):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


# </editor-fold>  # Wine


# <editor-fold desc="Spirits">
class Spirit(Alcohol):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Vodka(Spirit):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


# <editor-fold desc="Whiskey">
class Whiskey(Spirit):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Bourbon(Whiskey):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Scotch(Whiskey):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


# </editor-fold>  # Whiskey


class Gin(Spirit):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Tequila(Spirit):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


# <editor-fold desc="Rum">
class Rum(Spirit):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class WhiteRum(Rum):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "White Rum"


class DarkRum(Rum):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Dark Rum"


# </editor-fold>  # Rum


# </editor-fold>  # Spirits


class Liqueur(Alcohol):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Bitter(Liqueur):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Vermouth(Liqueur):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


# </editor-fold>  # Alcohols

class NonAlcohol(Drink):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, "", volumes)

    @override
    def format_type(self):
        return "Non-Alcoholic Drink"


class Tea(NonAlcohol):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, volumes)

    @override
    def description(self):  # Skip Drink desc and go back to Ingredient to re-capitalize generics
        return Ingredient.description(self)

    @override
    def format_type(self):
        return Ingredient.format_type(self)


class Soda(NonAlcohol):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, volumes)

    @override
    def format_type(self):
        return Ingredient.format_type(self)


# </editor-fold>  # Drinks


# <editor-fold desc="Additives">
class Additive(Ingredient):
    def __init__(self, ingredient_id=None, name=None, image=None, character=None, volumes=None):
        super().__init__(ingredient_id, name, image, character, volumes)


class Syrup(Additive):
    def __init__(self, ingredient_id=None, name=None, image=None, character=None, flavor=None, volumes=None):
        super().__init__(ingredient_id, name, image, character, volumes)
        if flavor is None:
            flavor = ""
        self.flavor = flavor


class Spice(Additive):
    def __init__(self, ingredient_id=None, name=None, image=None, character=None, volumes=None):
        super().__init__(ingredient_id, name, image, character, volumes)


class Herb(Additive):
    def __init__(self, ingredient_id=None, name=None, image=None, character=None, volumes=None):
        super().__init__(ingredient_id, name, image, character, volumes)


class Sweetener(Additive):
    def __init__(self, ingredient_id=None, name=None, image=None, character=None, volumes=None):
        super().__init__(ingredient_id, name, image, character, volumes)


class Fruit(Additive):
    def __init__(self, ingredient_id=None, name=None, image=None, character=None, volumes=None):
        super().__init__(ingredient_id, name, image, character, volumes)

    def crush(self):
        pass

    def juice(self):
        pass


# </editor-fold>  # Additives
# </editor-fold>  # Ingredients

# @TODO:  Not sure that there is truly no way to extract this automatically
class_arg_mapping = {
    "Ingredient": ["ingredient_id", "name", "image", "character", "volumes"],
    "Drink": ["ingredient_id", "name", "image", "flavor", "character", "notes", "volumes"],
    "Alcohol": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "Beer": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "Stout": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "MilkStout": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "Ale": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "BlondeAle": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "Wine": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "Chardonnay": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "PinotNoir": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "Merlot": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "Rose": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "Riesling": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "Spirit": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "Vodka": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "Whiskey": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "Bourbon": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "Scotch": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "Gin": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "Tequila": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "Rum": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "WhiteRum": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "DarkRum": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "Liqueur": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "Bitter": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "Vermouth": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv", "volumes"],
    "NonAlcohol": ["ingredient_id", "name", "image", "flavor", "character", "volumes"],
    "Tea": ["ingredient_id", "name", "image", "flavor", "character", "volumes"],
    "Soda": ["ingredient_id", "name", "image", "flavor", "character", "volumes"],
    "Additive": ["ingredient_id", "name", "image", "character", "volumes"],
    "Syrup": ["ingredient_id", "name", "image", "flavor", "character", "volumes"],
    "Spice": ["ingredient_id", "name", "image", "character", "volumes"],
    "Herb": ["ingredient_id", "name", "image", "character", "volumes"],
    "Sweetener": ["ingredient_id", "name", "image", "character", "volumes"],
    "Fruit": ["ingredient_id", "name", "image", "character", "volumes"]
}

# Database connection
connection = sqlite3.connect('cocktailDB.db')
cursor = connection.cursor()


def create_ingredient(ingredient_type, **row_data):
    try:
        if ingredient_type is None:
            return Ingredient(**{k: v for k, v in row_data.items() if k in class_arg_mapping.get("Ingredient", [])})

        required_args = class_arg_mapping.get(ingredient_type.__name__, [])
        # Filter out unexpected keyword arguments
        filtered_data = {key: value for key, value in row_data.items() if key in required_args}
        ingredient = ingredient_type(**filtered_data)
        return ingredient
    except (KeyError, IndexError, TypeError) as e:
        print(f"Error creating object of type {ingredient_type}: {e}")
        # Return a default Ingredient object if creation fails
        return Ingredient(**{k: v for k, v in row_data.items() if k in class_arg_mapping.get("Ingredient", [])})


all_ingredients = {}
product_volumes = {}


def load_ingredients_from_db():
    """Loads ingredients from the database and populates the global dictionary."""
    global all_ingredients  # Declare global variable access

    cursor.execute("SELECT * FROM ingredients")
    column_names = [description[0] for description in cursor.description]

    for row in cursor.fetchall():
        ingredient_data = dict(zip(column_names, row))
        ingredient_type_name = ingredient_data.pop('type')  # Removes type before passing as parameters
        ingredient_class = globals().get(ingredient_type_name) or Ingredient
        ingredient = create_ingredient(ingredient_class, **ingredient_data)
        all_ingredients[ingredient.name] = ingredient  # Use ingredient.name as key

    cursor.execute("SELECT * FROM product_volumes")
    column_names = [description[0] for description in cursor.description]
    for row in cursor.fetchall():
        volume_data = dict(zip(column_names, row))
        product_name = volume_data["product_name"]
        ingredient = all_ingredients.get(product_name)

        if ingredient:
            volume = volume_data["oz"]
            price = volume_data["price"]
            ingredient.volumes[volume] = price

def list_ingredients(container, typ):
    lst = {}
    i = 0
    for ingredient in container.values():
        is_instance = isinstance(ingredient, typ)
        if is_instance:
            lst[i] = ingredient
            i += 1
    return lst


def get_ingredient(ingredient_name):
    """Returns the Ingredient object corresponding to the given name."""
    return all_ingredients.get(ingredient_name)
