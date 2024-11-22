import nltk
import spacy
import re
from nltk.corpus import wordnet as wn
from lists import in_tools_list, in_verbs_list
from spacy.matcher import Matcher
from parse_ingredients import parse_ingredient, fraction_verify
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize, pos_tag

# from verbnet import VerbNet

nltk.download('wordnet')
nlp = spacy.load("en_core_web_sm")
lemmatizer = WordNetLemmatizer()
# vn = VerbNet()

units = [
        "cup", "teaspoon", "tablespoon", "pinch", "pound", "ounce", "clove",
        "can", "slice", "gram", "ml", "liter", "kg", "oz"
    ]

class Step:
    def __init__(self, snum, text, ingredients_list):
        ingredients, current_uasge, tools, actions, time, temp = parse_step(text.lower(), ingredients_list)
        
        self.step_num = snum
        self.text = text
        self.details = {}
        # self.time = get_times(text)
        if ingredients != []:
            self.details["ingredients"] = ingredients
        if tools != []:
            self.details["tools"] = tools
        if actions != []:
            self.details["actions"] = actions
        if time != None:
            self.details["time"] = time
        if temp !=[]:
            self.details["temp"] = temp
        if current_uasge !=[]:
            self.details["current_uasge"] = current_uasge

    def __str__(self):
        return str(self.step_num) + self.text # + str(self.details)

def parse_step(text, ingredients_list):

    # nlp.add_pipe("merge_noun_chunks")
    doc = nlp(text)

    ingredients, actions, tools, time, temp = [], [], [], [], []

    # tool may not just one word
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower()
        if in_tools_list(chunk_text) or is_cooking_tool(chunk_text):
                tools.append(chunk_text)

    final_ingredients=[]
    for ent in doc:
        word = ent.text.lower()
        word = lemmatizer.lemmatize(word)
        if ent.pos_ in ["NOUN", "PROPN"] and ((not in_verbs_list(word)) or in_tools_list(word)) :
            for ingredient in ingredients_list:
                for j in ingredient.ingredient_name.split():
                    if re.search(fr"\b{word}\b", j) and (ingredient not in final_ingredients):
                        final_ingredients.append(ingredient)
            
            if in_tools_list(word) or is_cooking_tool(word):
                if not word in tools:
                    tools.append(word)
        if ent.pos_ in ["VERB", "ROOT"] or in_verbs_list(word):
            if in_verbs_list(word) or is_cooking_action(word):
                actions.append(word)
                # print(f"Verb: {ent.text}, Object(s): {[child.text for child in ent.children if child.dep_ == 'dobj']}")
    # print("FOOD", [ent.text for ent in doc if ent.label_ in ["PRODUCT", "FOOD"]])

    tools = list(set(clean_nouns(tools, doc)))
    actions = list(set(actions))
    time = get_times(text.lower())
    temp = list(extract_temperature(text.lower()))
    current_usage = extract_quantity_unit_pairs(text, final_ingredients)
    return final_ingredients, current_usage, tools, actions, time, temp

def is_food(word):
    lemma = lemmatizer.lemmatize(word)
    syns = wn.synsets(word, pos = wn.NOUN)
    for syn in syns:
        if 'food' in syn.lexname() and (not lemma in units):
            return word
        
def is_cooking_action(word):
    syns = wn.synsets(word, pos = wn.VERB)
    for syn in syns:
        if 'cook' in syn.lexname() or 'change' in syn.lexname():
            return word
        
# def get_cooking_synsets(word):
#     word = word.lower()
#     syns = wn.synsets(word, pos=wn.VERB)
#     cooking_synsets = [syn for syn in syns if 'cook' in syn.lexname() or 'change' in syn.lexname()]
#     return cooking_synsets
# print(get_cooking_synsets("bake"))

def is_cooking_tool(word):
    syns = wn.synsets(word, pos=wn.NOUN)  
    for syn in syns:
        if "tool" in syn.definition() or "utensil" in syn.definition() or "instrument" in syn.definition():
            return word
        for hypernym in syn.hypernyms():
            if "tool" in hypernym.name() or "utensil" in hypernym.name() or "instrument" in hypernym.name():
                return word
            
def get_times(text):

    doc = nlp(text)
    matcher = Matcher(nlp.vocab)

    # TODO: handle numbers as words
    time_patterns = [
        [{"TEXT": {"REGEX": r"^\d+$"}}, {"LOWER": {"IN": ["hour", "hours", "minute", "minutes", "second", "seconds"]}}],
        [{"TEXT": {"REGEX": r"^\d+$"}}, {"LOWER": {"IN": ["to", "-", "–"]}}, {"TEXT": {"REGEX": r"^\d+$"}}, {"LOWER": {"IN": ["hour", "hours", "minute", "minutes", "second", "seconds"]}}],
        [{"LOWER": {"IN": ["a", "few", "several"]}}, {"LOWER": {"IN": ["hour", "hours", "minute", "minutes", "second", "seconds"]}}],
    ]

    matcher.add("TIME", time_patterns)
    matches = matcher(doc)

    # TODO: handle multiple time mentions in one step
    for match_id, start, end in matches:
        span = doc[start:end]
        return span.text

def extract_temperature(text):
    # Define the regex pattern
    pattern = r"(\d+)\s*(°|degrees)?\s*(?<![a-zA-Z])(F|C|f|c|Fahrenheit|Celsius|fahrenheit|celsius)(?![a-zA-Z])"
    
    # Find all matches
    matches = re.findall(pattern, text)
    
    # Process matches into a list of dictionaries
    temperatures = []
    for match in matches:
        value = int(match[0])  # The numeric part
        unit = match[2].lower()  # The unit part
        temperatures.append({"value": value, "unit": unit})
    
    return temperatures
           
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


# Function to identify if a word is a number or fraction
def is_number_or_fraction(word):
    return bool(re.match(r"(\d+/\d+|\d*\.\d+|\d+)", word)) or fraction_verify(word)

# # Function to extract quantity + unit pairs from a sentence
# def extract_quantity_unit_pairs(sentence, final_ingredients):
#     print(final_ingredients)
    
#     # Tokenize the sentence
#     tokens = sentence.split()

#     quantity_unit_pairs = []

#     i=0
#     while i < len(tokens) - 1:
#         word = tokens[i]
#         next_word = tokens[i + 1]

#         # Check if the word is a number or fraction
#         if is_number_or_fraction(word):
#             # Lemmatize the next word (unit) to ensure we get the singular form
#             lemma = lemmatizer.lemmatize(next_word.lower())

#             while is_number_or_fraction(lemma):
#                 word += " "+next_word
#                 next_word = tokens[i + 2]
#                 lemma = lemmatizer.lemmatize(next_word.lower())
#                 i = i + 1

#             if lemma in units or is_food(lemma) or lemma == "more":
#                 # If a valid unit follows the number, store the pair
#                 i = i+1

#                 # try to find corresponding ingredients name
#                 count=i + 1
#                 while count < len(tokens) - 1:
#                     current = lemmatizer.lemmatize(tokens[count])
#                     # current = tokens[count]
#                     current = re.sub(r"[,\.!@#$%^&*()\-+=:;\"'<>?/\\\[\]{}|`~]", "", current)
#                     print("Hello ", current)
#                     # no corresponding ingredients name
#                     if (current == "oil"):
#                         print(current in units)
#                     if current in units:
#                         quantity_unit_pairs.append({"quantity": word, "unit": next_word, "ingredient_name": ""})
#                         break
                    
#                     for ingredient in final_ingredients:
#                         print("What !", ingredient.ingredient_name)
#                         if current in ingredient.ingredient_name:
#                             quantity_unit_pairs.append({"quantity": word, "unit": next_word, "ingredient_name": ingredient.ingredient_name})
#                             break
#                     count +=1
#                 continue
                
#         i=i+1
                
#     return quantity_unit_pairs


def extract_quantity_unit_pairs(sentence, final_ingredients):
    print(final_ingredients)

    # Tokenize the sentence
    tokens = sentence.split()
    quantity_unit_pairs = []
    i = 0

    while i < len(tokens) - 1:
        word = tokens[i]
        next_word = tokens[i + 1]

        # Check if the current word is a number or fraction
        if is_number_or_fraction(word):
            # Lemmatize the next word (unit) to ensure it's in singular form
            lemma = lemmatizer.lemmatize(next_word.lower())

            # Handle cases where multiple numbers or fractions are grouped together
            while is_number_or_fraction(lemma):
                word += " " + next_word  # Combine with the next word
                i += 1
                if i + 1 < len(tokens):
                    next_word = tokens[i + 1]
                    lemma = lemmatizer.lemmatize(next_word.lower())
                else:
                    break

            # Check if the lemmatized word is a valid unit or food
            if lemma in units or is_food(lemma) or lemma == "more":
                # Move past the quantity and unit
                i += 1
                ingredient_name = ""
                count = i + 1

                # Try to find a corresponding ingredient name
                while count < len(tokens):
                    current = lemmatizer.lemmatize(tokens[count].lower())
                    # Remove special characters from the current token
                    current = re.sub(r"[,\.!@#$%^&*()\-+=:;\"'<>?/\\\[\]{}|`~]", "", current)
                    
                    # Check if the current token is in the units (invalid ingredient name)
                    if current in units:
                        break
                    
                    # Match the current token against ingredients
                    for ingredient in final_ingredients:
                        if current in ingredient.ingredient_name:
                            ingredient_name = ingredient.ingredient_name
                            break

                    if ingredient_name:  # Stop if an ingredient name is found
                        break

                    count += 1

                # Append the extracted pair
                quantity_unit_pairs.append({
                    "quantity": word,
                    "unit": next_word,
                    "ingredient_name": ingredient_name
                })

        i += 1  # Move to the next token
    
    return quantity_unit_pairs
#test = Step(1, "Arrange in a single layer on a rimmed baking sheet.",[])

test = Step(1, "Toss together butternut squash, 2 teaspoons of the oil, 1/2 teaspoon of the salt, and 1/4 teaspoon of the pepper.",[])

print(test.details)
print(test.text)
print(test.step_num)