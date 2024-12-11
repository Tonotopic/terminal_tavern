from typing import override
import sqlite3
from rich_console import styles
import inspect
import traceback

all_ingredients = []


# <editor-fold desc="Ingredients">
class Ingredient:
    def __init__(self, ingredient_id=None, name=None, image=None, character=None, volumes=None):
        self.ingredient_id = ingredient_id
        self.name = name
        self.image = image
        self.character = character
        if volumes is None:
            self.volumes = {}
        else:
            self.volumes = volumes

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
        if typ in styles:
            return typ
        else:
            for parent_class in type(self).__bases__:
                parent_object = parent_class()
                style = parent_object.get_ing_style()
                if style:
                    return style
        return ""

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
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None,
                 volumes=None):
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
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
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


# <editor-fold desc="Beer">
class Beer(Alcohol):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


# <editor-fold desc="Ale">
class Ale(Beer):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Stout(Ale):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class MilkStout(Stout):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Milk Stout"


class OatmealStout(Stout):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Oatmeal Stout"


class ImperialStout(Stout):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Imperial Stout"


class Porter(Ale):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Dubbel(Ale):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class SourAle(Ale):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Sour Ale"


class PaleAle(Ale):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Pale Ale"


class IPA(PaleAle):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return Ingredient.format_type(self)


class DoubleIPA(IPA):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Double IPA"


class Saison(PaleAle):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class BlondeAle(Ale):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Blonde Ale"


class RedAle(Ale):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Red Ale"


class AmberAle(Ale):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Amber Ale"


class BrownAle(Ale):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Brown Ale"


class DarkAle(Ale):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Dark Ale"


class Kolsch(Beer):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Kölsch"


# </editor-fold>


# <editor-fold desc="Lagers">
class Lager(Beer):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class PaleLager(Lager):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Pale Lager"


class Helles(PaleLager):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return Ingredient.format_type(self)


class Pilsner(PaleLager):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return Ingredient.format_type(self)


class AmberLager(Lager):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Amber Lager"


class DarkLager(Lager):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Dark Lager"


class Dunkel(DarkLager):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Bock(Lager):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Doppelbock(Bock):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Maibock(Bock):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


# </editor-fold>


class WheatBeer(Beer):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Wheat Beer"


class Witbier(WheatBeer):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Hefeweizen(WheatBeer):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


# </editor-fold>

class Cider(Alcohol):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


# <editor-fold desc="Wine">
class Wine(Alcohol):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Chardonnay(Wine):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class PinotNoir(Wine):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Pinot Noir"


class Merlot(Wine):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Rose(Wine):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Rosé"


class Riesling(Wine):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


# </editor-fold>  # Wine


# <editor-fold desc="Spirits">
class Spirit(Alcohol):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Vodka(Spirit):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


# <editor-fold desc="Whiskey">
class Whiskey(Spirit):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Bourbon(Whiskey):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Scotch(Whiskey):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


# </editor-fold>  # Whiskey


class Gin(Spirit):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Tequila(Spirit):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


# <editor-fold desc="Rum">
class Rum(Spirit):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class WhiteRum(Rum):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "White Rum"


class DarkRum(Rum):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self):
        return "Dark Rum"


# </editor-fold>  # Rum


# </editor-fold>  # Spirits

class Mead(Alcohol):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


# <editor-fold desc="Liqueur">
class Liqueur(Alcohol):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Bitter(Liqueur):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Vermouth(Liqueur):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


# </editor-fold>


# </editor-fold>  # Alcohols

# TODO: Change non-alcoholic drink description to just say drink
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


class EnergyDrink(NonAlcohol):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, volumes)

    def format_type(self):
        return "Energy Drink"


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

# Database connection
connection = sqlite3.connect('cocktailDB.db')
cursor = connection.cursor()


def get_constructor_args(ingredient_type):
    """Gets the constructor arguments for a given ingredient type.

    Args:
      ingredient_type: The type of ingredient.

    Returns:
      A list of constructor arguments.
    """
    ingredient_class = globals().get(ingredient_type)

    # If the class object is not found, return the arguments for the base Ingredient class.
    if ingredient_class is None:
        return ["name", "image", "character"]

    # Get the constructor parameters.
    constructor_params = ingredient_class.__init__.__code__.co_varnames[1:]  # Exclude 'self'

    # Return the constructor arguments.
    return list(constructor_params)


def create_object(ingredient_type, row_data, column_names):
    # Get the constructor arguments for the ingredient type.
    constructor_args = get_constructor_args(ingredient_type)

    # Create a dictionary mapping argument names to their values
    arg_dict = {arg: row_data[arg] for arg in column_names if arg in constructor_args}
    # If 'oz' is a constructor argument, and is in row_data, add it to the dictionary:
    if 'oz' in constructor_args and 'oz' in row_data:
        arg_dict['oz'] = row_data['oz']
    # If 'id' is a constructor argument, and is in row_data, add it to the dictionary:
    if 'ingredient_id' in constructor_args and 'ingredient_id' in row_data:
        arg_dict['ingredient_id'] = row_data['ingredient_id']

    # Extract the values for the constructor arguments (Updated line)
    arg_values = [arg_dict.get(arg) for arg in constructor_args]

    # Create the ingredient object
    ingredient_class = globals()[ingredient_type]
    ingredient = ingredient_class(*arg_values)

    return ingredient


def load_ingredients_from_db():
    global all_ingredients
    cursor.execute("SELECT * FROM ingredients")
    column_names = [description[0] for description in cursor.description]
    for row in cursor.fetchall():
        ingredient_type = dict(zip(column_names, row))["type"]
        product_name = dict(zip(column_names, row))["name"]  # Get the product name

        # Fetch volume data using product_name as the foreign key
        cursor.execute("SELECT oz, price FROM product_volumes WHERE product_name=?", (product_name,))
        volume_data = cursor.fetchall()  # Fetch all volumes and prices
        volumes = {}

        for vol in volume_data:
            volumes[int(vol[0])] = vol[1]

        # Pass volume data to the create_object function
        ingredient_data = dict(zip(column_names, row))
        ingredient_data['volumes'] = volumes  # Store volumes list in ingredient_data

        ingredient = create_object(ingredient_type, ingredient_data, column_names + ['volumes'])

        if ingredient:
            all_ingredients.append(ingredient)


def list_ingredients(container, typ):
    lst = {}
    i = 0

    for ingredient in container:
        is_instance = isinstance(ingredient, typ)
        if is_instance:
            lst[i] = ingredient
            i += 1
    return lst


def get_ingredient(ingredient_name):
    """Returns the Ingredient object corresponding to the given name."""
    return all_ingredients[ingredient_name]
