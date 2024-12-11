from rich.console import Console
from rich.theme import Theme
from rich.style import Style

ing_styles_dict = {"abv": Style(color="#d40241"),
                   "money": Style(color="#cfba02"),
                   # Ingredients
                   "fruit": Style(color="#ff66bb"),
                   "herb": Style(color="#47b809"),
                   "additive": Style(color="#a755fa"),
                   "drink": Style(color="#8189fc"),
                   "alcohol": Style(color="#db1818"),
                   "beer": Style(color="#ffba59"),
                   "wine": Style(color="#bd24a8"),
                   "spirit": Style(color="#51c9ab"),
                   "whiskey": Style(color="#ff781f"),
                   "vodka": Style(color="#ff6161"),
                   "gin": Style(color="#57ffa9"),
                   "tequila": Style(color="#40ecff"),
                   "rum": Style(color="#fffa7d"),
                   "liqueur": Style(color="#db1818"),
                   "soda": Style(color="#8189fc"),  # same as drink
                   "tea": Style(color="#549462")}
ingredient_styles = Theme(ing_styles_dict)
console = Console(theme=ingredient_styles)





