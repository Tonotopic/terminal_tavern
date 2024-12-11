from rich.console import Console
from rich.theme import Theme
from rich.style import Style


styles = {"abv": Style(color="#d40241"),
          "money": Style(color="#cfba02"),
          "dimmed": Style(color="#6e6e6e"),
          "panel": Style(color="#3c8fc2"),
          "prompt": Style(color="#429e45"),
          "error": Style(color="#ba2318"),
          # Ingredients
          "drink": Style(color="#8189fc"),
          "additive": Style(color="#ff66bb"),
          "fruit": Style(color="#ff66bb"),
          "herb": Style(color="#3b8c0e"),
          "spice": Style(color="#875933"),
          "sweetener": Style(color="#fcd29f"),
          "syrup": Style(color="#a755fa"),
          "energy drink": Style(color="#57d63e"),
          "alcohol": Style(color="#db1818"),
          "beer": Style(color="#ffba59"),
          "wine": Style(color="#bd24a8"),
          "cider": Style(color="#eb7a34"),
          "mead": Style(color="#c2a61d"),
          "spirit": Style(color="#51c9ab"),
          "whiskey": Style(color="#ff781f"),
          "vodka": Style(color="#ff6161"),
          "gin": Style(color="#57ffa9"),
          "tequila": Style(color="#40ecff"),
          "rum": Style(color="#fffa7d"),
          "liqueur": Style(color="#db1818"),
          "soda": Style(color="#db5858"),
          "tea": Style(color="#549462")}

theme = Theme(styles)
console = Console(theme=theme)

# Make room for the prompt line when anything renders using display size
width, height = console.size
console.size = width, height - 1