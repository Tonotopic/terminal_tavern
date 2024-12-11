import sqlite3

connection = sqlite3.connect("cocktailDB.db")
cursor = connection.cursor()
cursor.execute("SELECT * FROM tastes")
rows = cursor.fetchall()
tastes = {}
for row in rows:
    taste, term, weight = row
    if taste not in tastes:
        tastes[taste] = {}
    tastes[taste][term] = weight

connection.close()

for fruit_taste in ["berry", "melon", "tropical"]:  # Removed citrus
    tastes["fruity"].update(tastes[fruit_taste])
tastes["tart"].update(tastes["citrus"])
tastes["savory"].update(tastes["vegetal"])
tastes["smooth"].update(tastes["creamy"])

hoppy = ["hoppy", "hops", "beer"]

["wine", "bourbon", "rum", "champagne", "complex", "dull", "hazy", "cloudy", "boozey", "funky", "exotic",
 "vibrant", "bright", "balanced", "complex", "minimalistic", "foamy"]
["very", "strongly"]
["lightly", "slightly", "subtl"]

# Creamy reduces dark
# Dull reduces complex, exotic, balanced
# High abv reduces easy-drinking

# Vegetal clashes with sweet
