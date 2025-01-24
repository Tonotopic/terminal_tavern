from data.db_connect import get_connection, close_connection

# TODO: Taste profiles as percents

connection = get_connection()
cursor = connection.cursor()
cursor.execute("SELECT * FROM tastes")
rows = cursor.fetchall()
tastes = {}
for row in rows:
    taste, term, weight = row
    if taste not in tastes:
        tastes[taste] = {}
    tastes[taste][term] = weight
close_connection(connection)

for fruit_taste in ["berry", "melon-flavored", "tropical"]:  # Removed citrus
    tastes["fruity"].update(tastes[fruit_taste])
tastes["tart"].update(tastes["citrusy"])
tastes["savory"].update(tastes["vegetal"])
tastes["smooth"].update(tastes["creamy"])

keywords = {"chocolate", "green apple", "pineapple", "coconut", "orange", "strawberry", "raspberry", "tea", "lemon",
            "lime", "cherry", "cinnamon", "peach", "orange", "mint", "oak", "earthy", "smoke", "silky", "strong",
            "light-bodied", "full", "aged", "barreled", "hazy", "vibrant", "coffee", "roast"}

hoppy = ["hoppy", "hops", "beer"]

["wine", "bourbon", "rum", "champagne", "complex", "dull", "hazy", "cloudy", "boozey", "funky", "exotic",
 "vibrant", "bright", "balanced", "complex", "minimalistic", "foamy"]
["very", "strongly"]
["lightly", "slightly", "subtl"]

# Creamy reduces dark
# Dull reduces complex, exotic, balanced
# High abv reduces easy-drinking

# Vegetal clashes with sweet
