import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag

def extract_ingredient_details_nltk(line):
    # Tokenize and tag the input line
    tokens = word_tokenize(line)
    tagged = pos_tag(tokens)
    
    # Define common units and preparation terms
    units = [
        "cup", "teaspoon", "tablespoon", "pinch", "pound", "ounce", "clove",
        "can", "slice", "gram", "ml", "liter", "kg"
    ]
    preparation_terms = ["diced", "minced", "chopped", "shredded", "grated", "sliced", "cut", "softened"]
    
    # Extract quantity (numbers or fractions)
    quantity = next((word for word, tag in tagged if tag == "CD" or word.isdigit() or "½" in word), None)
    
    # Extract measurement (including plural forms)
    measurement = next((word for word in tokens if word.lower().rstrip('s') in units), None)
    
    # Extract preparation details (terms like softened)
    preparation = next((word for word in tokens if word.lower() in preparation_terms), None)
    
    # Extract descriptors (adjectives or specific terms like "salted")
    descriptors = [word for word, tag in tagged if tag == "JJ" or word.lower() in ["freshly", "ripe", "salted", "extra-virgin"]]
    
    # Exclude found tokens to isolate the ingredient name
    exclude = [quantity, measurement, preparation] + descriptors
    ingredient_name = " ".join([word for word in tokens if word not in exclude]).strip(", ")
    
    # In case there are multiple components in the name (like "Salted Butter"), we should keep the first word as descriptor
    if ingredient_name.lower() == "butter" and descriptors:
        ingredient_name = "Butter"
    
    return {
        "quantity": quantity,
        "measurement": measurement if measurement else None,
        "descriptor": ", ".join(descriptors) if descriptors else None,
        "ingredient_name": ingredient_name.title(),
        "preparation": preparation
    }

# Test cases
ingredient_lines = [
    "1 cup salted butter softened",
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

# Extracting details for each ingredient line
parsed_ingredients = [extract_ingredient_details_nltk(line) for line in ingredient_lines]

# Display results
for i in parsed_ingredients:
    print(i)

# import nltk
# import spacy
# from nltk.corpus import wordnet as wn
# from lists import in_tools_list, in_verbs_list
# from spacy.matcher import Matcher
# # from verbnet import VerbNet
# import re

# nltk.download('wordnet')
# nlp = spacy.load("en_core_web_sm")


# def extract_temperature(text):
#     # Define the regex pattern
#     pattern = r"(\d+)\s*(°|degrees)?\s*(F|C|f|c|Fahrenheit|Celsius|fahrenheit|celsius)"
    
#     # Find all matches
#     matches = re.findall(pattern, text)
    
#     # Process matches into a list of dictionaries
#     temperatures = []
#     for match in matches:
#         value = int(match[0])  # The numeric part
#         unit = match[2].lower()  # The unit part
#         temperatures.append({"value": value, "unit": unit})
    
#     return temperatures

# print(extract_temperature("35 degrees f"))



