from rich.console import Console
from rich.theme import Theme
from rich.style import Style

title_cards = {"17x70":
                   """[cmd]
 /$$$$$$$$                                /$$                     /$$
|__  $$__/                               |__/                    | $$
   | $$  /$$$$$$   /$$$$$$  /$$$$$$/$$$$  /$$ /$$$$$$$   /$$$$$$ | $$
   | $$ /$$__  $$ /$$__  $$| $$_  $$_  $$| $$| $$__  $$ |____  $$| $$
   | $$| $$$$$$$$| $$  \__/| $$ \ $$ \ $$| $$| $$  \ $$  /$$$$$$$| $$
   | $$| $$_____/| $$      | $$ | $$ | $$| $$| $$  | $$ /$$__  $$| $$
   | $$|  $$$$$$$| $$      | $$ | $$ | $$| $$| $$  | $$|  $$$$$$$| $$
   |__/ \_______/|__/      |__/ |__/ |__/|__/|__/  |__/ \_______/|__/[beer]
                             
       /$$$$$$$$    [dark]~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~[beer]                                                     
      |__  $$__/                                                     
         | $$  /$$$$$$  /$$    /$$ /$$$$$$   /$$$$$$  /$$$$$$$       
         | $$ |____  $$|  $$  /$$//$$__  $$ /$$__  $$| $$__  $$      
         | $$  /$$$$$$$ \  $$/$$/| $$$$$$$$| $$  \__/| $$  \ $$      
         | $$ /$$__  $$  \  $$$/ | $$_____/| $$      | $$  | $$      
         | $$|  $$$$$$$   \  $/  |  $$$$$$$| $$      | $$  | $$      
         |__/ \_______/    \_/    \_______/|__/      |__/  |__/[dark]
         
         ~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
""",
               "11x47":
                   """[cmd]
     _______                     __             __ 
    |       .-----.----.--------|__.-----.---.-|  |
    |.|   | |  -__|   _|        |  |     |  _  |  |
    `-|.  |-|_____|__| |__|__|__|__|__|__|___._|__|
      |:  |[beer]  _______ [dark]~*~*~*~*~*~*~*~*~*~*~*~*~*~*~             
    [cmd]  |::.| [beer]|       .---.-.--.--.-----.----.-----. 
    [cmd]  `---'[beer] |.|   | |  _  |  |  |  -__|   _|     | 
            `-|.  |-|___._|\___/|_____|__| |__|__| 
              |:  |[dark]~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~[beer]                         
              |::.|                                
              `---'                                
                   """,
               "10x42":
                   """[cmd]
     _____                    _             _ 
    /__   \___ _ __ _ __ ___ (_)_ __   __ _| |
      / /\/ _ \ '__| '_ ` _ \| | '_ \ / _` | |
     / / |  __/ |  | | | | | | | | | | (_| | |
     \/   \___|_|  |_| |_| |_|_|_| |_|\__,_|_|
    [dark] ~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~[beer]   
          _____                               
         /__   \__ ___   _____ _ __ _ __      
           / /\/ _` \ \ / / _ \ '__| '_ \     
          / / | (_| |\ V /  __/ |  | | | |    
          \/   \__,_| \_/ \___|_|  |_| |_|    
    [dark]     ~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~   
                   """,
               "11x20":
                   """[cmd]
     _____              
    |_   _|__ _ _ _ __  
      | |/ -_) '_| '  \ 
      |_|\___|_| |_|_|_|
        (_)_ _  __ _| | 
        | | ' \/ _` | | 
    [beer] ___[cmd]|_|_||_\__,_|_| [beer]
    |_   _|_ ___ __     
      | |/ _` \ V /     
      |_|\__,_|\_/ _    
        / -_) '_| ' \   
        \___|_| |_||_|          
                   """
               }
styles = {"abv": Style(color="#d40241"),
          "money": Style(color="#cfba02"),
          "shop": Style(color="#628260"),
          "dimmed": Style(color="#6e6e6e"),
          "dark": Style(color="#5c263a"),
          "panel": Style(color="#3c8fc2"),
          "bar_menu": Style(color="#9c0834"),
          "prompt": Style(color="#429e45"),
          "cmd": Style(color="#429e45"),
          "customer": Style(color="#e09ef7"),
          "warn": Style(color="#fcba03"),
          "attention": Style(color="#ede174"),
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
          "fortified wine": Style(color="#b3566a"),
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
          "soda": Style(color="#8fbddb"),
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
    "fresh": styles.get("tequila"),
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
