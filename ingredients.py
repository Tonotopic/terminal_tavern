from typing import override
import sqlite3
import inspect
from rich.table import Table

from rich_console import styles

all_ingredients = []


# TODO: Soda water always available
# <editor-fold desc="Ingredients">
class Ingredient:
    def __init__(self, name=None, flavor=None, character=None, notes=None,
                 volumes=None):
        self.name = name
        self.flavor = flavor
        if flavor is None:
            self.flavor = ""
        self.character = character
        self.notes = notes
        if volumes is None:
            self.volumes = {}
        else:
            self.volumes = dict(sorted(volumes.items(), key=lambda item: item[1]))

    def format_a(self):
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
                f"is {self.format_a()} {self.character} {self.format_flavor()}"
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

    def get_portions(self):
        return {}

    def show_portions(self):
        portions_table = Table()
        portions_list = []
        portions_table.add_column("portion title")
        portions_table.add_column("fl oz")

        portions = self.get_portions()
        for portion_key in portions:
            portions_table.add_row(portion_key, f"{portions[portion_key]} fl oz")
            portions_list.append(portion_key.lower())
        return portions_table, portions_list


# <editor-fold desc="Drinks">
class Drink(Ingredient):
    def __init__(self, name=None, flavor=None, character=None, notes=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, volumes)

    @override
    def description(self):  # Remove capitalization
        style = self.get_ing_style()
        desc = (f"[{style}][italic]{self.name}[/{style}][/italic] "
                f"is {self.format_a()} {self.character} {self.format_flavor()}"
                f"[{style}]{self.format_type().lower()}[/{style}]{self.notes_desc()}.")
        return desc


# <editor-fold desc="Alcohols">
class Alcohol(Drink):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, volumes)
        self.abv = abv

    def abv_desc(self):
        if self.abv is not None:
            return f" It is [abv]{self.abv}% ABV.[/abv]"

    @override
    def description(self):
        return super().description() + self.abv_desc()


# <editor-fold desc="Beer">
class Beer(Alcohol):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def get_portions(self):
        return {"8oz": 8, "6oz": 6, "4oz": 4}


# <editor-fold desc="Ale">
class Ale(Beer):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Stout(Ale):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class MilkStout(Stout):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Milk Stout"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class OatmealStout(Stout):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Oatmeal Stout"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class ImperialStout(Stout):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Imperial Stout"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class Porter(Ale):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Dubbel(Ale):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class SourAle(Ale):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Sour Ale"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class FruitTart(SourAle):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Fruit Tart Ale"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class PaleAle(Ale):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Pale Ale"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class IPA(PaleAle):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        return Ingredient.format_type(self, plural)


class DoubleIPA(IPA):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Double IPA"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class BlackIPA(IPA):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Black IPA"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class Saison(PaleAle):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        return Ingredient.format_type(self, plural)


class BlondeAle(Ale):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Blonde Ale"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class AmberAle(Ale):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Amber Ale"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class BrownAle(Ale):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Brown Ale"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class DarkAle(Ale):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Dark Ale"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class Kolsch(Beer):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

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
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class RiceLager(Lager):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Rice Lager"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class PaleLager(Lager):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Pale Lager"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class Helles(PaleLager):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        return Ingredient.format_type(self)


class Pilsner(PaleLager):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        return Ingredient.format_type(self, plural)


class AmberLager(Lager):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Amber Lager"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class DarkLager(Lager):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        # TODO: This is boilerplate
        type_name = "Dark Lager"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class Schwarzbier(DarkLager):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Schwarzbier"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class Dunkel(DarkLager):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Bock(Lager):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Doppelbock(Bock):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Maibock(Bock):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


# </editor-fold>


class WheatBeer(Beer):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Wheat Beer"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class Lambic(WheatBeer):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        if plural:
            return f"{Ingredient.format_type(self)}s"
        else:
            return Ingredient.format_type(self)


class Witbier(WheatBeer):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        return Ingredient.format_type(self, plural)


class Hefeweizen(WheatBeer):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        return Ingredient.format_type(self, plural)


# </editor-fold>

class Cider(Alcohol):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def get_portions(self):
        return {"8oz": 8, "6oz": 6, "4oz": 4}


# <editor-fold desc="Wine">
class Wine(Alcohol):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def get_portions(self):
        return {"Glass Pour": 6, "Spritzer Pour": 4, "Shot": 2}


class RedWine(Wine):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Red Wine"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class WhiteWine(Wine):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "White Wine"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class Rose(Wine):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Rosé"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class Chardonnay(WhiteWine):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        if plural:
            return f"{Ingredient.format_type(self)}s"
        else:
            return Ingredient.format_type(self)


class PinotNoir(RedWine):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Pinot Noir"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class Merlot(RedWine):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        if plural:
            return f"{Ingredient.format_type(self)}s"
        else:
            return Ingredient.format_type(self)


class Riesling(WhiteWine):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        if plural:
            return f"{Ingredient.format_type(self)}s"
        else:
            return Ingredient.format_type(self)


class Sparkling(Wine):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Sparkling Wine"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class SkinContact(WhiteWine):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

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
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def get_portions(self):
        return {"Shot": 2, "Double": 4}


class Vodka(Spirit):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


# <editor-fold desc="Whiskey">
class Whiskey(Spirit):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Bourbon(Whiskey):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Scotch(Whiskey):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = type(self).__name__
        if plural:
            return f"{type_name}es"
        else:
            return type_name


class Rye(Whiskey):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


# </editor-fold>  # Whiskey


class Gin(Spirit):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class LondonDry(Gin):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    def format_type(self, plural=False):
        type_name = "London Dry Gin"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class Tequila(Spirit):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


# <editor-fold desc="Rum">
class Rum(Spirit):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class WhiteRum(Rum):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "White Rum"
        if plural:
            return f"{type_name}s"
        else:
            return type_name


class DarkRum(Rum):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

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
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    def get_portions(self):
        return {"Glass Pour": 6, "Spritzer Pour": 4, "Shot": 2}


# <editor-fold desc="Liqueur">
class Liqueur(Alcohol):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def get_portions(self):
        return {"Dash": 1 / 48, "Generous Dash": 1 / 24, "Shot": 2, "Double": 4, }


class Bitter(Liqueur):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Vermouth(Liqueur):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


# </editor-fold>

class HardSoda(Alcohol):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def format_type(self, plural=False):
        type_name = "Hard Soda"
        if plural:
            return f"{type_name}s"
        else:
            return type_name

    @override
    def get_portions(self):
        return {"4oz": 4, "6oz": 6, "8oz": 8}


# </editor-fold>  # Alcohols

# <editor-fold desc="NonAlcohols">
class NonAlcohol(Drink):
    def __init__(self, name=None, flavor=None, character=None, notes=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, volumes)

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

    @override
    def get_portions(self):
        return {"4oz": 4, "6oz": 6, "8oz": 8}


class Tea(NonAlcohol):
    def __init__(self, name=None, flavor=None, character=None, notes=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, volumes)

    @override
    def description(self):  # Skip Drink desc and go back to Ingredient to re-capitalize generics
        return Ingredient.description(self)

    @override
    def format_type(self, plural=False):
        return Ingredient.format_type(self, plural)


class Soda(NonAlcohol):
    def __init__(self, name=None, flavor=None, character=None, notes=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, volumes)

    @override
    def format_type(self, plural=False):
        return Ingredient.format_type(self, plural)


class EnergyDrink(NonAlcohol):
    def __init__(self, name=None, flavor=None, character=None, notes=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, volumes)

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
    def __init__(self, name=None, flavor=None, character=None, notes=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, volumes)

    @override
    def get_portions(self):
        return {"Single": 1, "Shared": 3}


class Syrup(Additive):
    def __init__(self, name=None, character=None, flavor=None, notes=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, volumes)


class Spice(Additive):
    def __init__(self, name=None, character=None, volumes=None):
        super().__init__(name, "", character, "", volumes)

    @override
    def get_portions(self):
        return {"Dash": 1 / 24, "Teaspoon": 1 / 6, "On the Rim": 1 / 6}


class Herb(Additive):
    def __init__(self, name=None, character=None, volumes=None):
        super().__init__(name, "", character, "", volumes)

    @override
    def get_portions(self):
        return {"Leaf": 1 / 10, "Sprig": 1}


class Sweetener(Additive):
    def __init__(self, name=None, character=None, volumes=None):
        super().__init__(name, "", character, "", volumes)

    @override
    def get_portions(self):
        return {"Teaspoon": 1 / 6, "Tablespoon": 1 / 2, "1 fl oz": 1}


class Fruit(Additive):
    def __init__(self, name=None, character=None, volumes=None):
        super().__init__(name, "", character, "", volumes)

    def get_portions(self):
        unsliceable = {"maraschino cherry", "raspberry", "lychee", "blackberry", "cranberry"}
        portions = {"Slice": 1 / 8, "Juice": 1 / 2, "Crushed": 1, "Whole": 1}
        if self.name in unsliceable:
            portions.pop("Slice")
            return portions
        else:
            return portions


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

    # Extract the values for the constructor arguments
    arg_values = [arg_dict.get(arg) for arg in constructor_args]

    ingredient_class = globals()[ingredient_type]
    ingredient = ingredient_class(*arg_values)

    return ingredient


def load_ingredients_from_db():
    #  Populates all_ingredients with ingredients from the database, including their available volumes and prices
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


def all_ingredient_types(typ=Ingredient):
    subclasses = typ.__subclasses__()
    for subclass in subclasses:
        subclasses.extend(all_ingredient_types(subclass))
    return subclasses


def get_ingredient(ingredient_name):
    """Returns the Ingredient object corresponding to the given name."""
    return all_ingredients[ingredient_name]


def categorize_spirits(spirits):
    """Categorizes spirits into 'Flavored' and 'Unflavored' groups."""
    flavored = [spirit for spirit in spirits if spirit.flavor]
    unflavored = [spirit for spirit in spirits if not spirit.flavor]
    return flavored, unflavored

# </editor-fold>
