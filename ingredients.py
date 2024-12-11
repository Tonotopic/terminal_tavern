from typing import override
import sqlite3
from rich_console import styles
import inspect

all_ingredients = []


# TODO: Soda water always available
# TODO: Better solution for "Crown Royal Black" vs "Blackberry"
# <editor-fold desc="Ingredients">
class Ingredient:
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None,
                 volumes=None):
        self.ingredient_id = ingredient_id
        self.name = name
        self.image = image
        self.flavor = flavor
        if flavor is None:
            self.flavor = ""
        self.character = character
        self.notes = notes
        if volumes is None:
            self.volumes = {}
        else:
            self.volumes = dict(sorted(volumes.items(), key=lambda item: item[1]))

    def a(self):
        """Determines whether "a" or "an" should be printed just before the character attribute."""
        if self.character[0] in "aeiou" or self.character.startswith("herb"):
            return "an"
        else:
            return "a"

    def format_flavor(self):  # Add the necessary space after flavor if there is one
        if self.flavor:
            return f"{self.flavor} "
        else:
            return ""

    def format_type(self, plural=False):
        type_name = type(self).__name__
        if plural:
            return f"{type_name}s"
        else:
            return type_name

    def notes_desc(self):
        if self.notes:
            return f" with notes of {self.notes}"
        else:
            return ""

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

    def description(self):  # {Name} is a/an {character} {flavor}{type}{notes}.
        style = self.get_ing_style()
        desc = (f"[{style}][italic]{self.name.capitalize()}[/{style}][/italic] "
                f"is {self.a()} {self.character} {self.format_flavor()}"
                f"[{style}]{self.format_type().lower()}[/{style}]{self.notes_desc()}.")
        return desc

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

    def get_menu_section(self):
        menu_section = int()
        if isinstance(self, Beer):
            menu_section = 1
        elif isinstance(self, Cider):
            menu_section = 2
        elif isinstance(self, Wine):
            menu_section = 3
        elif isinstance(self, Mead):
            menu_section = 4
        else:
            return None
        return menu_section


# <editor-fold desc="Drinks">
class Drink(Ingredient):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, volumes)

    @override
    def description(self):  # Remove capitalization
        style = self.get_ing_style()
        desc = (f"[{style}][italic]{self.name}[/{style}][/italic] "
                f"is {self.a()} {self.character} {self.format_flavor()}"
                f"[{style}]{self.format_type().lower()}[/{style}]{self.notes_desc()}.")
        return desc


# <editor-fold desc="Alcohols">
class Alcohol(Drink):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, volumes)
        self.abv = abv

    def abv_desc(self):
        if self.abv is not None:
            return f"It is [abv]{self.abv}% ABV[/abv]"


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
    def format_type(self, plural=False):
        type_name = "Milk Stout"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class OatmealStout(Stout):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Oatmeal Stout"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class ImperialStout(Stout):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Imperial Stout"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


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
    def format_type(self, plural=False):
        type_name = "Sour Ale"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class FruitTart(SourAle):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)
    @override
    def format_type(self, plural=False):
        type_name = "Fruit Tart Ale"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class PaleAle(Ale):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Pale Ale"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class IPA(PaleAle):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        return Ingredient.format_type(self, plural)


class DoubleIPA(IPA):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Double IPA"
        if plural:
            return f"{type_name}s"
        else:
            return type_name

class BlackIPA(IPA):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Black IPA"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class Saison(PaleAle):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        return Ingredient.format_type(self, plural)


class BlondeAle(Ale):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Blonde Ale"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class RedAle(Ale):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Red Ale"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class AmberAle(Ale):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Amber Ale"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class BrownAle(Ale):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Brown Ale"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class DarkAle(Ale):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Dark Ale"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class Kolsch(Beer):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Kölsch"
        if plural:
            return f"{type_name}es"
        else:
            return type_name


# </editor-fold>


# <editor-fold desc="Lagers">
class Lager(Beer):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

class RiceLager(Lager):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Rice Lager"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class PaleLager(Lager):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Pale Lager"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class Helles(PaleLager):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        return Ingredient.format_type(self)


class Pilsner(PaleLager):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        return Ingredient.format_type(self, plural)


class AmberLager(Lager):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Amber Lager"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class DarkLager(Lager):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        # TODO: This is boilerplate
        type_name = "Dark Lager"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


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
    def format_type(self, plural=False):
        type_name = "Wheat Beer"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class Witbier(WheatBeer):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        return Ingredient.format_type(self, plural)


class Hefeweizen(WheatBeer):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        return Ingredient.format_type(self, plural)


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
    def format_type(self, plural=False):
        type_name = "Pinot Noir"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class Merlot(Wine):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Rose(Wine):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Rosé"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class Riesling(Wine):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


class Sparkling(Wine):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Sparkling Wine"
        if plural:
            return f"{type_name}s"
        else:
            return type_name

class SkinContact(Wine):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Skin-Contact Wine"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


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

    @override
    def format_type(self, plural=False):
        type_name = type(self).__name__
        if plural:
            return f"{type_name}es"
        else:
            return type_name


class Rye(Whiskey):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)


# </editor-fold>  # Whiskey


class Gin(Spirit):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

class LondonDry(Gin):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    def format_type(self, plural=False):
        type_name = "London Dry Gin"
        if plural:
            return f"{type_name}s"
        else:
            return type_name
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
    def format_type(self, plural=False):
        type_name = "White Rum"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class DarkRum(Rum):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Dark Rum"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


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

# <editor-fold desc="NonAlcohols">
class NonAlcohol(Drink):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, volumes)

    @override
    def description(self):
        return super().description().replace("non-alcoholic drink", "drink")

    @override
    def format_type(self, plural=False):
        type_name = "Non-Alcoholic Drink"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class Tea(NonAlcohol):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, volumes)

    @override
    def description(self):  # Skip Drink desc and go back to Ingredient to re-capitalize generics
        return Ingredient.description(self)

    @override
    def format_type(self, plural=False):
        return Ingredient.format_type(self, plural)


class Soda(NonAlcohol):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, volumes)

    @override
    def format_type(self, plural=False):
        return Ingredient.format_type(self, plural)


class EnergyDrink(NonAlcohol):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Energy Drink"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


# </editor-fold>


# </editor-fold>  # Drinks


# <editor-fold desc="Additives">
class Additive(Ingredient):
    def __init__(self, ingredient_id=None, name=None, image=None, flavor=None, character=None, notes=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, volumes)


class Syrup(Additive):
    def __init__(self, ingredient_id=None, name=None, image=None, character=None, flavor=None, notes=None,
                 volumes=None):
        super().__init__(ingredient_id, name, image, flavor, character, notes, volumes)


class Spice(Additive):
    def __init__(self, ingredient_id=None, name=None, image=None, character=None, volumes=None):
        super().__init__(ingredient_id, name, image, "", character, "", volumes)


class Herb(Additive):
    def __init__(self, ingredient_id=None, name=None, image=None, character=None, volumes=None):
        super().__init__(ingredient_id, name, image, "", character, "", volumes)


class Sweetener(Additive):
    def __init__(self, ingredient_id=None, name=None, image=None, character=None, volumes=None):
        super().__init__(ingredient_id, name, image, "", character, "", volumes)


class Fruit(Additive):
    def __init__(self, ingredient_id=None, name=None, image=None, character=None, volumes=None):
        super().__init__(ingredient_id, name, image, "", character, "", volumes)

    def crush(self):
        pass

    def juice(self):
        pass


# </editor-fold>  # Additives
# </editor-fold>  # Ingredients

# Database connection
connection = sqlite3.connect('cocktailDB.db')
cursor = connection.cursor()


# <editor-fold desc="Functions">
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
    # If 'volume' is a constructor argument, and is in row_data, add it to the dictionary:
    if 'volume' in constructor_args and 'volume' in row_data:
        arg_dict['volume'] = row_data['volume']
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
        cursor.execute("SELECT volume, price FROM product_volumes WHERE product_name=?", (product_name,))
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


def list_ingredients(container, typ, type_specific=False):
    lst = []

    for ingredient in container:
        is_instance = False
        if type_specific:
            if type(ingredient) is typ:
                is_instance = True
        else:
            is_instance = isinstance(ingredient, typ)
        if is_instance:
            lst.append(ingredient)
    return lst


def get_ingredient(ingredient_name):
    """Returns the Ingredient object corresponding to the given name."""
    return all_ingredients[ingredient_name]


def categorize_spirits(spirits):
    """Categorizes spirits into 'Flavored' and 'Unflavored' groups."""
    flavored = []
    unflavored = []
    for spirit in spirits:
        if spirit.flavor:  # Check if the spirit has a flavor attribute
            flavored.append(spirit)
        else:
            unflavored.append(spirit)
    return flavored, unflavored

# </editor-fold>
