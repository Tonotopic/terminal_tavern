import re
from typing import override, Literal
import sqlite3
import inspect
from rich.table import Table

from rich_console import console, styles, standardized_spacing
from utils import quarter_round
import flavors

all_ingredients = []

special_formats = {
    "Kolsch": "Kölsch",
    "Rose": "Rosé",
    "SkinContact": "Skin-Contact Wine",
    "NonAlcohol": "Non-Alcoholic Drink"
}
special_plurals = {
    "Chardonnay": "Chardonnays",
    "Amaro": "Amari"
}


class MenuItem:
    def __init__(self):
        self.markup = 0.0
        self.markdown = 0.0
        self.formatted_markdown = ""

    def cost_value(self):
        variable = False
        if self.volumes:
            cost_value = self.price_per_oz("max") * self.pour_vol()
            return cost_value, variable
        else:
            console.print(f"[error]Ingredient {self.name} has no product volumes")

    def profit_base(self):
        cost_value, variable = self.cost_value()
        profit_base = None
        if cost_value < 1.25:
            profit_base = 3.75
        elif 1.25 <= cost_value < 2.5:
            profit_base = cost_value * 3
        elif 2.5 <= cost_value < 4.5:
            profit_base = cost_value * 2
        elif cost_value >= 4.5:
            profit_base = cost_value * 1.25
        return profit_base, variable

    def base_price(self):
        return round(quarter_round(self.profit_base()[0]) + self.markup, 2)

    def mark_up(self, value, percent):
        if percent:
            self.markup = self.base_price() * value
            return True
        else:
            self.markup = value
            return True

    def mark_down(self, value, percent):
        if percent:
            self.markdown = self.current_price() * value
            self.formatted_markdown = f"-{int(value * 100)}%"
            return True
        else:
            self.markdown = value
            if value == 0:
                self.formatted_markdown = ""
            else:
                self.formatted_markdown = f"-${"{:.2f}".format(value)}"
            return True

    def current_price(self):
        return round(self.base_price() - self.markdown, 2)

    def list_price(self, expanded=False):
        price = self.current_price()
        formatted_price = f"[money]${"{:.2f}".format(price)}"
        if self.markdown == 0 or expanded is False:
            return formatted_price
        else:
            return formatted_price + f" ({self.formatted_markdown})"

    def list_item(self, expanded=False):
        # Layout offset (12) and markdown offset (15)
        total_spacing = console.size[0] - 29 if expanded else int(console.size[0] // 2) - 19
        name = self.name

        if isinstance(self, Beer):
            price_spacing = total_spacing // 3
            beer_spacing = 2 * price_spacing
            beer_spacing += total_spacing % 3

            formatted_type = self.format_type()
            abv_str = f"({self.abv}%)" if expanded else ""
            if len(name) > beer_spacing:
                hidden_chars = int(len(name) - beer_spacing)
                name = name[:-(hidden_chars + 3)] + "..."
            if len(self.format_type() + abv_str + "()") > price_spacing:
                hidden_chars = int(len(self.format_type() + abv_str + "()") - (price_spacing))
                formatted_type = formatted_type[:-(hidden_chars + 2)] + ".."

            return (f"[beer]{name}{standardized_spacing(name, beer_spacing)}"
                    f"({formatted_type})[/beer][abv]{abv_str}[/abv]"
                    f"{standardized_spacing(self.format_type() + abv_str + "()", price_spacing)}"
                    f"{self.list_price(expanded=expanded)}")

        elif isinstance(self, Alcohol):
            style = self.get_style()

            if len(name) > total_spacing:
                name = name[:-3] + "..."
            return f"[{style}]{name}[/{style}]{standardized_spacing(name, total_spacing)}{self.list_price()}"

        else:
            console.print(f"[error]Menu item {self.name} not triggering Recipe, Beer, or other Alcohol")


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
            return f"[fruit]{self.flavor}[/fruit] "
        else:
            return ""

    def format_type(self, plural=False):
        type_name = type(self).__name__

        # Check for special formats
        if type_name in special_formats:
            type_name = special_formats[type_name]
        else:
            # Add space before new word (except for first letter and "IPA")
            type_name = re.sub(r'(?<!^)(?=[A-Z])', r' ', type_name)
            type_name = type_name.replace("I P A", "IPA")

        if plural:
            if type_name in special_plurals:
                type_name = special_plurals[type_name]
            elif type_name.endswith("ey"):
                type_name = type_name[:-2] + "ies"  # Replace "ey" with "ies"
            elif type_name.endswith("y"):
                type_name = type_name[:-1] + "ies"  # Replace "y" with "ies"
            elif type_name.endswith("ch") or type_name.endswith("sh") or type_name.endswith("x") or type_name.endswith(
                    "s") or type_name.endswith("z"):
                type_name = f"{type_name}es"
            else:
                type_name = f"{type_name}s"

        return type_name

    def notes_desc(self):
        if self.notes:
            return f" with notes of {self.notes}"
        else:
            return ""

    def get_style(self):
        """Gets the style for the given type or its nearest parent in the theme."""
        typ = self.format_type().lower()
        if typ in styles:
            return typ
        else:
            for parent_class in type(self).__bases__:
                parent_object = parent_class()
                style = parent_object.get_style()
                if style:
                    return style
        return ""

    def description(self, markup=True):  # {Name} is a/an {character} {flavor}{type}{notes}.
        style = self.get_style()
        if markup:
            desc = (f"[{style}][italic]{self.name.capitalize()}[/{style}][/italic] "
                    f"is {self.format_a()} {self.character} {self.format_flavor()}"
                    f"[{style}]{self.format_type().lower()}[/{style}]{self.notes_desc()}.")
        else:
            desc = (f"{self.name.capitalize()} "
                    f"is {self.format_a()} {self.character} {self.format_flavor()}"
                    f"{self.format_type().lower()}{self.notes_desc()}.")
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
        menu_section = None
        if isinstance(self, Beer):
            menu_section = Beer
        elif isinstance(self, Cider):
            menu_section = Cider
        elif isinstance(self, Wine):
            menu_section = Wine
        elif isinstance(self, Mead):
            menu_section = Mead
        else:
            return None
        return menu_section

    def get_portions(self):
        return {}

    def show_portions(self):
        portions_table = Table(show_header=False)
        portions_list = []

        portions = self.get_portions()
        for portion_key in portions:
            portions_table.add_row(portion_key, f"{round(portions[portion_key], 2)} oz")
            portions_table.add_row()
            portions_list.append(portion_key.lower())
        return portions_table, portions_list

    def price_per_oz(self, bound: Literal["max", "min", "avg"]):
        def price_over_vol(index):
            shop_vol = list(self.volumes)[index]
            vol_price = list(self.volumes.values())[index]
            return vol_price / shop_vol

        if self.volumes:
            if bound == "max":
                return price_over_vol(0)
            elif bound == "min":
                return price_over_vol(len(self.volumes) - 1)
            elif bound == "avg":
                total = 0.0
                for i in self.volumes:
                    total += price_over_vol(i)
                return total / len(self.volumes)
        else:
            console.print(f"[error]self.volumes not present for {self.name}")


# <editor-fold desc="Drinks">
class Drink(Ingredient):
    def __init__(self, name=None, flavor=None, character=None, notes=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, volumes)

    @override
    def description(self, markup=True):  # Remove capitalization
        style = self.get_style()
        if markup:
            desc = (f"[{style}][italic]{self.name}[/{style}][/italic] "
                    f"is {self.format_a()} {self.character} {self.format_flavor()}"
                    f"[{style}]{self.format_type().lower()}[/{style}]{self.notes_desc()}.")
        else:
            desc = (f"{self.name} "
                    f"is {self.format_a()} {self.character} {self.format_flavor()}"
                    f"{self.format_type().lower()}{self.notes_desc()}.")
        return desc


# <editor-fold desc="Alcohols">
class Alcohol(Drink):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, volumes)
        self.abv = abv

    def abv_desc(self, markup=True):
        if self.abv is not None:
            if markup:
                return f" It is [abv]{self.abv}% ABV.[/abv]"
            else:
                return f" It is {self.abv}% ABV."

    @override
    def description(self, markup=True):
        return super().description(markup) + self.abv_desc()


# <editor-fold desc="Beer">
class Beer(Alcohol, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)
        MenuItem.__init__(self)

    @override
    def get_portions(self):
        return {"8oz": 8, "5oz": 5, "2oz": 2, "1oz": 1}

    def pour_vol(self):
        return 12


# <editor-fold desc="Ale">
class Ale(Beer, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Stout(Ale, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class MilkStout(Stout, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class OatmealStout(Stout, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class ImperialStout(Stout, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Porter(Ale, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Dubbel(Ale, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class SourAle(Ale, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class FruitTart(SourAle, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class PaleAle(Ale, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class IPA(PaleAle, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class DoubleIPA(IPA, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class BlackIPA(IPA, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Saison(PaleAle, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class BlondeAle(Ale, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class AmberAle(Ale, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class BrownAle(Ale, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class DarkAle(Ale, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Kolsch(Beer, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


# </editor-fold>


# <editor-fold desc="Lagers">
class Lager(Beer, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class RiceLager(Lager, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class PaleLager(Lager, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Helles(PaleLager, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Pilsner(PaleLager, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class AmberLager(Lager, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class DarkLager(Lager, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Schwarzbier(DarkLager, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Dunkel(DarkLager, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Bock(Lager, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Doppelbock(Bock, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Maibock(Bock, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


# </editor-fold>


# <editor-fold desc="Wheat Beer">
class WheatBeer(Beer, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Lambic(WheatBeer, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Witbier(WheatBeer, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Hefeweizen(WheatBeer, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


# </editor-fold>

class Shandy(Beer, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

# </editor-fold>

class Cider(Alcohol, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)
        MenuItem.__init__(self)

    @override
    def get_portions(self):
        return Beer.get_portions(self)

    def pour_vol(self):
        return 12


# <editor-fold desc="Wine">
class Wine(Alcohol, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)
        MenuItem.__init__(self)

    @override
    def get_portions(self):
        return {"Glass Pour": 6, "Spritzer Pour": 4, "Shot": 2, "1oz": 1, "Half oz": 1 / 2}

    def pour_vol(self):
        return 6


class RedWine(Wine, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class WhiteWine(Wine, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Rose(Wine, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Chardonnay(WhiteWine, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class PinotNoir(RedWine, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Merlot(RedWine, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Riesling(WhiteWine, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class SparklingWine(Wine, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class SkinContact(WhiteWine, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class FortifiedWine(Wine, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Sherry(FortifiedWine):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Brandy(Wine, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Cognac(Brandy):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


# </editor-fold>  # Wine


# <editor-fold desc="Spirits">
class Spirit(Alcohol):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def get_portions(self):
        return {"Splash": 0.25, "Half oz": 1 / 2, "1oz": 1, "Shot": 2, "Double": 4}


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


class Rye(Whiskey):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


# </editor-fold>  # Whiskey


# <editor-fold desc="Gin">
class Gin(Spirit):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class LondonDryGin(Gin):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class OldTomGin(Gin):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


# </editor-fold>


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


class DarkRum(Rum):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


# </editor-fold>  # Rum


class Absinthe(Spirit):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


# </editor-fold>  # Spirits

class Mead(Alcohol, MenuItem):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)
        MenuItem.__init__(self)

    @override
    def get_portions(self):
        return Wine.get_portions(self)

    def pour_vol(self):
        return 6


# <editor-fold desc="Liqueur">
class Liqueur(Alcohol):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def get_portions(self):
        return {"Dash": round(1 / 48, 2), "Generous Dash": round(1 / 24, 2), "Splash": 0.25, "Half oz": 1 / 2, "1oz": 1,
                "Shot": 2, "Double": 4, }


class Bitter(Liqueur):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Vermouth(Liqueur):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class SweetVermouth(Vermouth):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class DryVermouth(Vermouth):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


class Amaro(Liqueur):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)


# </editor-fold>

class HardSoda(Alcohol):
    def __init__(self, name=None, flavor=None, character=None, notes=None, abv=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, abv, volumes)

    @override
    def get_portions(self):
        return Soda.get_portions(self)


# </editor-fold>  # Alcohols

# <editor-fold desc="NonAlcohols">
class NonAlcohol(Drink):
    def __init__(self, name=None, flavor=None, character=None, notes=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, volumes)

    @override
    def get_portions(self):
        return {"Half oz": 1 / 2, "1oz": 1, "2oz": 2, "4oz": 4, "6oz": 6, "8oz": 8}


class Tea(NonAlcohol):
    def __init__(self, name=None, flavor=None, character=None, notes=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, volumes)

    @override
    def description(self, markup=True):  # Skip Drink desc and go back to Ingredient to re-capitalize generics
        return Ingredient.description(self, markup)


class Soda(NonAlcohol):
    def __init__(self, name=None, flavor=None, character=None, notes=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, volumes)


class EnergyDrink(NonAlcohol):
    def __init__(self, name=None, flavor=None, character=None, notes=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, volumes)


# </editor-fold>


# </editor-fold>  # Drinks


# <editor-fold desc="Additives">
class Additive(Ingredient):
    def __init__(self, name=None, flavor=None, character=None, notes=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, volumes)

    @override
    def get_portions(self):
        return {"Dash": round(1 / 24, 2), "Teaspoon": round(1 / 6, 2), "Splash": 0.25, "Half ounce": 1 / 2, "1oz": 1,
                "2oz": 2, "3oz": 3}


class Syrup(Additive):
    def __init__(self, name=None, character=None, flavor=None, notes=None,
                 volumes=None):
        super().__init__(name, flavor, character, notes, volumes)


class Spice(Additive):
    def __init__(self, name=None, character=None, volumes=None):
        super().__init__(name, "", character, "", volumes)

    @override
    def get_portions(self):
        return {"Dash": round(1 / 24, 2), "Teaspoon": round(1 / 6, 2), "Tablespoon": 1 / 2,
                "On the Rim": round(1 / 6, 2)}


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
        portions = {"Teaspoon": round(1 / 6, 2), "Tablespoon": 1 / 2, "1 fl oz": 1}
        if self.name == "sugar":
            portions["On the Rim"] = round(1 / 6, 2)
        return portions


class Fruit(Additive):
    def __init__(self, name=None, character=None, volumes=None):
        super().__init__(name, "", character, "", volumes)

    def get_portions(self):
        unsliceable = {"maraschino cherry", "raspberry", "lychee", "blackberry", "cranberry"}
        portions = {"Juice (Tsp)": round(1 / 6, 2), "Juice (Tbsp)": 1 / 2, "Crushed": 1}
        if self.name in unsliceable:
            portions["Whole"] = round(1 / 8, 2)
            portions["Crushed"] = round(1 / 8, 2)
        else:
            portions["Slice"] = round(1 / 8, 2)
        if self.name in flavors.tastes["citrus"]:
            portions["Rind"] = round(1 / 8, 2)
            portions["Zest"] = round(1 / 24, 2)
        if self.name in flavors.tastes["citrus"] or self.name == "pineapple":
            portions["Wheel"] = 0.25

        return portions


# </editor-fold>  # Additives
# </editor-fold>  # Ingredients


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
    # Database connection
    connection = sqlite3.connect('tavern_db.db')
    cursor = connection.cursor()
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
    connection.close()


def list_ingredients(container, typ, no_inheritance=False):
    lst = []

    for ingredient in container:
        is_instance = False
        if no_inheritance:
            if type(ingredient) is typ:
                is_instance = True
        else:
            is_instance = isinstance(ingredient, typ)
        if is_instance:
            lst.append(ingredient)
    return lst


def all_ingredient_types(typ=Ingredient):
    subclasses = set()
    for subclass in typ.__subclasses__():
        subclasses.add(subclass)
        subclasses.update(all_ingredient_types(subclass))
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
