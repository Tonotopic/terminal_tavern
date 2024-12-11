citrus = ["citrus", "lemon", "lime", "orange", "grapefruit", "mandarin", "tangerine", "tangelo", "passionfruit"]
berry = ["berry", "berries", "raspberr", "strawberr", "cranberr", "blackberr", "blueberr", "currant", "boysenberr"]
melon = ["melon", "watermelon", "honeydew", "cantaloupe"]
tropical = ["tropical", "pineapple", "guava", "coconut", "mango", "papaya"]
fruity = ["fruity", "jam", "juic", "cherr", "apple", "apricot", "peach", "lychee", "pear", "banana", "grape",
          "pomegranate", "pulp"]
for taste in [citrus, berry, melon, tropical]:
    fruity.extend(taste)
woody = ["wood", "barrel", "cask", "smoke", "ash", "finished" "pine", "oak", "cedar", "hickory", "maple", "spruce"]
grain = ["grain", "grain", "rye", "malt", "barley", "corn", "biscuit", "cracker", "bread", "crust", "wheat", "oat"]

fresh = ["fresh", "crisp", "clean", "green", "mint", "pine", "eucalyptus", "ginger", "clove", "dill", "cucumber"]
easy_drinking = ["easy-drinking", "fresh", "pale", " light", "crisp", "delicate", "light-bod", "subdued"]
tart = ["tart", "sour", "acid", "pickle", "apple", "pineapple" "lychee", "raspberry", "zest", "green apple", "peel", "tangy"]
tart.extend(citrus)
sweet = ["sweet", "sugar", "cocoa", "caramel", "honey", "vanilla", "cake", "custard", "toffee", "marshmallow",
         "butterscotch", "maple", "carob", "molasses", "bubblegum", "cardamom", "amaretto", "sarsaparilla", "licorice", "fudge"]
warm = ["warm", "cozy", "spice", "cocoa", "chocolate", "coffee", "toffee", "tobacco", "cinnamon", "graham cracker",
        "chamomile", "cardamom", "pumpkin", "smoke"]
bitter = ["bitter", "coffee", "burn", "dark chocolate", "tea", "cacao", "gentian"]
nutty = ["nutty", "peanut", "nutmeg", "pistachio", "almond", "praline", "cardamom", "caraway", "hazelnut", "coriander", "amaretto"]
spicy = ["spicy", "spic", "pepper", "clove", "curry"]
rustic = ["rustic", "paper", "tobacco", "clove", "leather", "earth", "root", "ash", "resin"]
floral = ["floral", "flower", "blossom", "violets", "anise", "rose", "chamomile", "lavender", "dandelion", "saffron", "sarsaparilla", "gentian"]
pungent = ["pungent", "ginger", "anise", "clove"]
dark = ["dark", "roast", "toast", "burn", "cooked", "brown", "black", "molasses", "raisin", "cacao", "coffee"]
creamy = ["creamy", "cream", "lactose", "milk", "chocolate"]
herbal = ["herbal", "herb", "grass", "botanical", "juniper", "tea", "sage", "coriander", "saffron"]
vegetal = ["vegetable", "vegetal", "olive", "onion", "pickle"]
savory = ["savory", "salt"]
savory.extend(vegetal)
dry = ["dry", "tannin"]
hoppy = ["hoppy", "hops", "beer"]
smooth = ["smooth", "silk", "velvet", "fluffy", "luscious"]
smooth.extend(creamy)
thick = ["thick", "chewy", "plush", "fluffy", "heavy", "luscious", "full-bod"]
thick.extend(creamy)
rich = ["rich", "chocolate", "cocoa", "deep", "robust", "aged", "luscious", "bold", "ample", "full"]
aromatic = ["aromatic", "fragrant", "mint", "pine", "eucalyptus", "anise", "clove"]
unique = ["unique", "exotic"]

types = {"Bitter": {"bitter": 3}, "Vermouth": {"bitter": 3, "herbal": 1}, "Gin": {"floral": 2, "herbal": 1}, "Whiskey": {"rich": 1, "smooth": 1}}

tastes = (citrus, berry, melon, tropical, fruity, woody, grain, fresh, easy_drinking, tart, sweet, warm,
          bitter, nutty, spicy, rustic, floral, pungent, dark, creamy, herbal, vegetal, savory, dry, hoppy, smooth,
          thick, rich, aromatic, unique)

["wine", "bourbon", "rum", "champagne", "gentian", "complex", "dull", "hazy", "cloudy", "boozey", "funky", "exotic", "vibrant", "bright", "balanced", "complex", "minimalistic", "foamy"]
["very", "strongly"]
["lightly", "slightly", "subtle"]