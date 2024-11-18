import re

pattern = r"""
    (?P<amount>\d+(\.\d+)?\s?(?:\d+/\d+|[½⅓⅔¼¾⅛⅜⅝⅞])?(?:\s?-\s?\d+(\.\d+)?(?:\s?/\d+|[½⅓⅔¼¾⅛⅜⅝⅞])?)?)\s*  # amount
    (?:(?P<unit>cups?|tbsp|tsp|tablespoons?|teaspoons?|grams?|g|oz|ounces?|ml|milliliters?|liters?|lbs?|pounds?|kg|kilograms?|pieces?)\.?\s*)? # optional unit
    (?P<ingredient>[A-Za-z\s-]+)  # ingredient name
    # (?:,\s?(?P<descriptor>[A-Za-z\s-]+))?  # optional descriptor
"""

ingredient_regex = re.compile(pattern, re.VERBOSE)

def parse_ingredient(ingredient_text):
    match = ingredient_regex.match(ingredient_text)
    if match:
        return {
            "amount": match.group("amount"),
            "unit": match.group("unit"),
            "ingredient": match.group("ingredient")
        }
    
def parse_ingredients(ingredients):
    result = []
    for ingredient in ingredients:
        result.append(parse_ingredient(ingredient))
    return result
    
ingredients = ["1 cup salted butter softened",
    "1 cup granulated sugar",
    "1 cup light brown sugar packed",
    "2 teaspoons pure vanilla extract",
    "2 large eggs",
    "3 cups all-purpose flour",
    "1 teaspoon baking soda",
    "½ teaspoon baking powder",
    "1 teaspoon sea salt",
    "2 cups chocolate chips (14 oz)"
]

final = parse_ingredients(ingredients)
for i in final:
    print(i)