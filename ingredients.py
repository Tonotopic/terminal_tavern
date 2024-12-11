from typing import override
import sqlite3
from rich_console import ing_styles_dict
import inspect


# <editor-fold desc="Ingredients">
class Ingredient:
    def __init__(self, ingredient_id=None, name=None, image=None, character=None):
        self.ingredient_id = ingredient_id
        self.name = name
        self.image = image
        self.character = character

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
                attributes = self.get_attributes()
                if isinstance(self, Syrup):
                    attributes.pop()
                parent_object = parent_class(*attributes)
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
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None):
        super().__init__(ingredient_id, name, image, character)
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
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes)
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
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)


class Stout(Beer):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)


class MilkStout(Beer):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)

    @override
    def format_type(self):
        return "Milk Stout"


class Ale(Beer):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)


class BlondeAle(Ale):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)

    @override
    def format_type(self):
        return "Blonde Ale"


# <editor-fold desc="Wine">
class Wine(Alcohol):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)


class Chardonnay(Wine):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)


class PinotNoir(Wine):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)

    @override
    def format_type(self):
        return "Pinot Noir"


class Merlot(Wine):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)


class Rose(Wine):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)

    @override
    def format_type(self):
        return "Rosé"


class Riesling(Wine):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)


# </editor-fold>  # Wine


# <editor-fold desc="Spirits">
class Spirit(Alcohol):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)


class Vodka(Spirit):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)


# <editor-fold desc="Whiskey">
class Whiskey(Spirit):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)


class Bourbon(Whiskey):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)


class Scotch(Whiskey):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)


# </editor-fold>  # Whiskey


class Gin(Spirit):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)


class Tequila(Spirit):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)


# <editor-fold desc="Rum">
class Rum(Spirit):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)


class WhiteRum(Rum):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)

    @override
    def format_type(self):
        return "White Rum"


class DarkRum(Rum):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)

    @override
    def format_type(self):
        return "Dark Rum"


# </editor-fold>  # Rum


# </editor-fold>  # Spirits


class Liqueur(Alcohol):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)


class Bitter(Liqueur):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)


class Vermouth(Liqueur):
    def __init__(self, ingredient_id, name, image, flavor, character, notes, abv):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv)


# </editor-fold>  # Alcohols


class Tea(Drink):
    def __init__(self, ingredient_id, name, image, flavor, character):
        super().__init__(ingredient_id, name, image, flavor, character, "")

    @override
    def description(self):  # Skip Drink desc and go back to Ingredient to re-capitalize generics
        return Ingredient.description(self)


class Soda(Drink):
    def __init__(self, ingredient_id, name, image, flavor, character):
        super().__init__(ingredient_id, name, image, flavor, character, "")


# </editor-fold>  # Drinks


# <editor-fold desc="Additives">
class Additive(Ingredient):
    def __init__(self, ingredient_id=None, name=None, image=None, character=None):
        super().__init__(ingredient_id, name, image, character)


class Syrup(Additive):
    def __init__(self, ingredient_id, name, image, character, flavor=""):
        super().__init__(ingredient_id, name, image, character)
        self.flavor = flavor


class Spice(Additive):
    def __init__(self, ingredient_id, name, image, character):
        super().__init__(ingredient_id, name, image, character)


class Herb(Additive):
    def __init__(self, ingredient_id, name, image, character):
        super().__init__(ingredient_id, name, image, character)


class Sweetener(Additive):
    def __init__(self, ingredient_id, name, image, character):
        super().__init__(ingredient_id, name, image, character)


class Fruit(Additive):
    def __init__(self, ingredient_id, name, image, character):
        super().__init__(ingredient_id, name, image, character)

    def crush(self):
        pass

    def juice(self):
        pass


# </editor-fold>  # Additives
# </editor-fold>  # Ingredients

# @TODO:  Not sure that there is truly no way to extract this automatically
class_arg_mapping = {
    "Ingredient": ["ingredient_id", "name", "image", "character"],
    "Drink": ["ingredient_id", "name", "image", "flavor", "character", "notes"],
    "Alcohol": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "Beer": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "Stout": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "MilkStout": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "Ale": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "BlondeAle": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "Wine": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "Chardonnay": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "PinotNoir": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "Merlot": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "Rose": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "Riesling": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "Spirit": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "Vodka": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "Whiskey": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "Bourbon": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "Scotch": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "Gin": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "Tequila": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "Rum": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "WhiteRum": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "DarkRum": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "Liqueur": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "Bitter": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "Vermouth": ["ingredient_id", "name", "image", "flavor", "character", "notes", "abv"],
    "Tea": ["ingredient_id", "name", "image", "flavor", "character"],
    "Soda": ["ingredient_id", "name", "image", "flavor", "character"],
    "Additive": ["ingredient_id", "name", "image", "character"],
    "Syrup": ["ingredient_id", "name", "image", "flavor", "character"],
    "Spice": ["ingredient_id", "name", "image", "character"],
    "Herb": ["ingredient_id", "name", "image", "character"],
    "Sweetener": ["ingredient_id", "name", "image", "character"],
    "Fruit": ["ingredient_id", "name", "image", "character"]
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
