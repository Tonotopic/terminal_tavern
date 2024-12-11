from rich.console import Console
from rich.theme import Theme
from rich.style import Style

styles = {"abv": Style(color="#d40241"),
          "money": Style(color="#cfba02"),
          "shop": Style(color="#628260"),
          "dimmed": Style(color="#6e6e6e"),
          "dark": Style(color="#5c263a"),
          "panel": Style(color="#3c8fc2"),
          "bar_menu": Style(color="#9c0834"),
          "prompt": Style(color="#429e45"),
          "cmd": Style(color="#429e45"),
          "warn": Style(color="#fcba03"),
          "highlight": Style(color="#a3bfff"),
          "error": Style(color="#ba2318"),
          "l": Style(color="#3c8fc2"),
          # Ingredients
          "cocktails": Style(color="#5de3c1"),
          "drink": Style(color="#db1818"),
          "non-alcoholic drink": Style(color="#8189fc"),
          "additive": Style(color="#a755fa"),
          "fruit": Style(color="#ff66bb"),
          "herb": Style(color="#3b8c0e"),
          "spice": Style(color="#875933"),
          "sweetener": Style(color="#fcd29f"),
          "syrup": Style(color="#a755fa"),
          "energy drink": Style(color="#57d63e"),
          "alcohol": Style(color="#db1818"),
          "hard soda": Style(color="#db5858"),  # Same as soda
          "beer": Style(color="#f2d280"),
          "wine": Style(color="#bd24a8"),
          "brandy": Style(color="#b3566a"),
          "cider": Style(color="#e08700"),
          "mead": Style(color="#b89c00"),
          "spirit": Style(color="#51c9ab"),
          "whiskey": Style(color="#ff781f"),
          "vodka": Style(color="#ff6161"),
          "gin": Style(color="#57ffa9"),
          "tequila": Style(color="#40ecff"),
          "rum": Style(color="#fffa7d"),
          "liqueur": Style(color="#db1818"),
          "absinthe": Style(color="#aae68a"),
          "soda": Style(color="#db5858"),
          "tea": Style(color="#549462")}
taste_styles = {
    "aromatic": styles.get("herb"),
    "berry": styles.get("fruit"),
    "bitter": styles.get("abv"),
    "citrus": styles.get("rum"),
    "creamy": styles.get("sweetener"),
    "dark": styles.get("dark"),
    "dry": styles.get("gin"),
    "easy-drinking": styles.get("beer"),
    "floral": styles.get("additive"),
    "fresh": styles.get("gin"),
    "fruity": styles.get("fruit"),
    "grain-forward": styles.get("beer"),
    "herbal": styles.get("herb"),
    "melon": styles.get("absinthe"),
    "nutty": styles.get("spice"),
    "pungent": styles.get("energy drink"),
    "rich": styles.get("wine"),
    "rustic": styles.get("whiskey"),
    "savory": styles.get("cider"),
    "smooth": styles.get("soda"),
    "spicy": styles.get("abv"),
    "sweet": styles.get("rum"),
    "tart": styles.get("energy drink"),
    "thick": styles.get("wine"),
    "tropical": styles.get("rum"),
    "unique": styles.get("additive"),
    "vegetal": styles.get("herb"),
    "warm": styles.get("whiskey"),
    "woody": styles.get("spice"),
}

theme = Theme(styles)
console = Console(theme=theme)

# Make room for the prompt line when anything renders using display size
width, height = console.size
console.size = width, height - 1


def standardized_spacing(preceding_string, total_spacing):
    item_info_spacing = total_spacing - len(preceding_string)
    info_spacing_string = ""
    for spacing_index in range(int(item_info_spacing)):
        info_spacing_string += " "
    return info_spacing_string