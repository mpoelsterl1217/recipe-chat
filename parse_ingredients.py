
# import re

# pattern = r"""
#     (?P<amount>\d+(\.\d+)?\s?(?:\d+/\d+|[½⅓⅔¼¾⅛⅜⅝⅞])?(?:\s?-\s?\d+(\.\d+)?(?:\s?/\d+|[½⅓⅔¼¾⅛⅜⅝⅞])?)?)\s*  # amount
#     (?:(?P<unit>cups?|tbsp|tsp|tablespoons?|teaspoons?|grams?|g|oz|ounces?|ml|milliliters?|liters?|lbs?|pounds?|kg|kilograms?|pieces?)\.?\s*)? # optional unit
#     (?P<ingredient>[A-Za-z\s-]+)  # ingredient name
#     # (?:,\s?(?P<descriptor>[A-Za-z\s-]+))?  # optional descriptor
# """

# ingredient_regex = re.compile(pattern, re.VERBOSE)

# def parse_ingredient(ingredient_text):
#     match = ingredient_regex.match(ingredient_text)
#     if match:
#         return {
#             "text": ingredient_text,
#             "amount": match.group("amount"),
#             "unit": match.group("unit"),
#             "ingredient": match.group("ingredient")
#         }
#     else:
#         return {
#             "text": ingredient_text,
#             "amount": None,
#             "unit": None,
#             "ingredient": None
#         }
    
# def parse_ingredients(ingredients):
#     result = []
#     for ingredient in ingredients:
#         result.append(parse_ingredient(ingredient))
#     return result
    
# ingredients = ["1 cup salted butter softened",
#     "1 cup granulated sugar",
#     "1 cup light brown sugar packed",
#     "2 teaspoons pure vanilla extract",
#     "2 large eggs",
#     "3 cups all-purpose flour",
#     "1 teaspoon baking soda",
#     "½ teaspoon baking powder",
#     "1 teaspoon sea salt",
#     "2 cups chocolate chips (14 oz)"
# ]

# final = parse_ingredients(ingredients)
# for i in final:
#     print(i)

import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
import unicodedata
from nltk.corpus import wordnet as wn
import spacy
from stanford_parser import IngredientParser
from ingredient import Ingredient

nlp = spacy.load("en_core_web_sm")

lemmatizer = WordNetLemmatizer()

ingredient_parser = IngredientParser()

units = [
        "cup", "teaspoon", "tablespoon", "pinch", "pound", "ounce", "clove", "can",
        "slice", "gram", "g", "kg", "milligram", "mg", "milliliter", "ml", "liter", "l",
        "oz", "fluid ounce", "fl oz", "quart", "qt", "pint", "pt", "gallon", "gal",
        "stick", "dash", "drop", "handful", "package", "bag", "packet", "bar", "bottle",
        "head", "stalk", "bunch", "sheet", "piece", "sprig", "strip", "cube"
    ]

preparation_terms = [
    "dice", "mince", "chop", "shred", "grate", "slice", "cut", "soften",
    "julienne", "peel", "crush", "roast", "bake", "steam", "fry", "boil", 
    "sauté", "stir-fry", "broil", "caramelize", "poach", "grill", "braise",
    "blanch", "whisk", "whip", "knead", "fold", "sear", "toast", "marinate",
    "blend", "purée", "press", "zest", "scald", "deglaze", "mince", "minced"
]

descriptors_terms = [
    "freshly", "ripe", "salted", "extra-virgin", "smoked", "spicy", "sweet",
    "savory", "organic", "ripe", "roasted", "unsalted", "creamy", "aged",
    "mature", "light", "dark", "fermented", "powdered", "ground", "dried",
    "pickled", "raw", "whole", "chilled", "frozen", "canned", "boiled",
    "toasted", "browned", "grated", "sifted", "softened", "dehydrated", "boneless", "cooking", "fresh",
    "oven-ready"
]

def fraction_verify(word):
    if len(word)!=1:
        return False
    name = unicodedata.name(word)
    if name.startswith('VULGAR FRACTION'):
        return True
    else:
        return False

def parse_ingredient(line):
    # Tokenize and tag the input line


    try: 
        ingredient = ingredient_parser.parse_line(line)
    except Exception as e: 
        print(f"stanford parser failed: {line}")
        print(e)
    
        line = line.lower()
        doc = nlp(line)
        tokens = word_tokenize(line)
        tagged = pos_tag(tokens)

        preparations = []
        descriptors = []
        ingredient_name = []
        quantity = []
        measurement = []

        # Extract quantity (numbers or fractions)
        for word, tag in tagged:
            match = re.match(r"(\d+/\d+)|(\d*\.\d+)|(\d+)|[\u00BC-\u00BE\u2150-\u215E]", word)
            #if tag == "CD":
            if word.isdigit() or fraction_verify(word) or match:
                quantity.append(word)
        
        # Extract measurement (including plural forms)
        for word, tag in tagged:
            lemma = lemmatizer.lemmatize(word, pos='n')  # Normalize the token to singular form
            if lemma in units:
                measurement.append(word)
        
        # Extract preparation details (terms like softened)
        for word, tag in tagged:
            lemma = lemmatizer.lemmatize(word, pos='v')
            if lemma in preparation_terms:
                preparations.append(word)
        
        # Extract descriptors (adjectives or specific terms like "salted")
        for word, tag in tagged:
            if (tag == "JJ" and word.lower() in descriptors_terms) and not fraction_verify(word):
                descriptors.append(word)
        
        # Exclude found tokens to isolate the ingredient name
        name = []
        exclude = set(quantity + measurement + preparations + descriptors)
        for word in tokens:
            if (word not in exclude) and (not re.match(r'[^\w\s]', word)) and is_food(word):
                name.append(word)
        
        # print(name)
        if not name:
            ingredient_name=[]
            for word in tokens:
                if (word not in exclude) and (not re.match(r'[^\w\s]', word)):
                    ingredient_name.append(word)
        else:
            for i in list(set(clean_nouns(name, doc))):
                for j in exclude:
                    i =i.replace(j, "")
                ingredient_name.append(i)

        ingredient = Ingredient(" ".join(quantity).strip(),
                                " ".join(measurement).strip(),
                                descriptors,
                                " ".join(ingredient_name).strip(),
                                preparations)
    
    #return {
    #    "quantity": quantity if quantity else None,
    #    "measurement": measurement if measurement else None,
    #    "descriptor": descriptors if descriptors else None,
    #    "ingredient_name": ingredient_name if ingredient_name else None,
    #    "preparation": preparations if preparations else None
    #}
    return ingredient

def parse_ingredients(ingredients):
    result = []
    for ingredient in ingredients:
        result.append(parse_ingredient(ingredient))
    return result

def is_food(word):
    lemmatizer = WordNetLemmatizer()
    lemma = lemmatizer.lemmatize(word)
    syns = wn.synsets(word, pos = wn.NOUN)
    for syn in syns:
        if 'food' in syn.lexname() and (not lemma in units):
            return word

def clean_nouns(words, doc):
    words = set(words)
    result = []
    for word in words:
        # print("NOUN CHUNK:", chunk)
        found = False
        for chunk in doc.noun_chunks:
            if word in chunk.text:
                result.append(chunk.text)
                found = True
        if not found:
            result.append(word)
    return result

# ingredients = ["1 cup salted butter softened",
#     "1 cup granulated sugar",
#     "1 cup light brown sugar packed",
#     "2 teaspoons pure vanilla extract",
#     "2 large eggs",
#     "3 cups all-purpose flour",
#     "1 teaspoon baking soda",
#     "½ teaspoon baking powder",
#     "1 teaspoon sea salt",
#     "2 cups chocolate chips (14 oz)"
# ]

# for i in ingredients:
#     final = parse_ingredient(i)
#     print(i)
#     print(final)
#     print()

final = parse_ingredient("5 cups marinara sauce")
print(final)