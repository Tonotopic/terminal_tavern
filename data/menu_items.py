from display.rich_console import console, standardized_spacing
from utility import logger
from utility.utils import quarter_round


class MenuItem:
    def __init__(self):
        self.markup = 0.0
        self.markdown = 0.0
        self.formatted_markdown = ""

    def cost_value(self):
        """
        Multiplies highest price per oz by serving volume.
        :return: A cost value float, and a bool indicating whether the price is variable (as in some cocktails based
        on ingredient selection)
        """
        variable = False
        if self.volumes:
            cost_value = self.price_per_oz("max") * self.pour_vol()
            return cost_value, variable
        else:
            console.print(f"[error]Ingredient {self.name} has no product volumes")
            return None, False

    def profit_base(self):
        """
        Uses cost value to calculate a profitable baseline price for a drink.
        :return: A non-rounded decimal value, and a bool indicating whether the price is variable (as in some cocktails
        based on ingredient selection).
        """
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
        """Format and round to the nearest quarter the profit base price of a drink (the price before markup)."""
        return round(quarter_round(self.profit_base()[0]) + self.markup, 2)

    def mark_up(self, value, percent: bool):
        """
        Sets markup on the price of a drink, by percentage or dollars/cents.

        :param value: Given value of markup
        :param percent: Bool indicating whether the value represents a percentage of the existing price
        :return: True if successful
        """
        if percent:
            self.markup = self.base_price() * value
            return True
        else:
            self.markup = value
            return True

    def mark_down(self, value, percent: bool):
        """
        Sets markdown on the price of a drink, by percentage or dollars/cents.

        :param value: Given value of markdown
        :param percent: Bool indicating whether the value represents a percentage of the existing price
        :return: True if successful
        """
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
        """Applies markup/markdown to the menu item price."""
        return round(self.base_price() - self.markdown + self.markup, 2)

    def list_price(self, expanded=False):
        """Displays formatted current price."""
        price = self.current_price()
        formatted_price = f"[money]${"{:.2f}".format(price)}"
        if self.markdown == 0 or expanded is False:
            return formatted_price
        else:
            return formatted_price + f" ({self.formatted_markdown})"

    def list_item(self, expanded=False):
        """
        Formats string for listing MenuItems in tables, etc., including relevant info according to type.

        :param expanded: Whether displaying in the full expanded menu window, or the condensed dashboard menu.
        :return: The formatted string
        """
        from data.ingredients import Beer, Alcohol # Imported locally to prevent circular import
        # Layout offset + markdown offset
        total_spacing = console.size[0] - 31 if expanded else int(console.size[0] // 2) - 22
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
            logger.logprint(f"[error]Menu item {self.name} not triggering Recipe, Beer, or other Alcohol")

    def top_flavors(self, n=3, **kwargs):
        """Return the top N flavors as a dict, ordered by percentage."""
        profile = self.generate_taste_profile(**kwargs)
        return dict(list(profile.items())[:n])

    def has_flavor_in_top_n(self, flavor, n=3, **kwargs):
        """Return True if `flavor` appears in the top N taste profile."""
        return flavor in self.top_flavors(n, **kwargs)
