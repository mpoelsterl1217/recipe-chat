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
        # print(self.details)

    def __str__(self):
        return str(self.snum) + self.text # + str(self.details)

def parse_step(text, ingredients_list):
    # print(ingredients_list)

    # nlp.add_pipe("merge_noun_chunks")
    doc = nlp(text)

    ingredients, actions, tools, time, temp = [], [], [], [], []
    # print("doc", doc)

    # tool may not just one word
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower()
        if in_tools_list(chunk_text) or is_cooking_tool(chunk_text):
                tools.append(chunk_text)

    final_ingredients=[]
    for ent in doc:
        # print(ent)
        word = ent.text.lower()
        word = lemmatizer.lemmatize(word)
        if ent.pos_ in ["NOUN", "PROPN"] and (not in_verbs_list(word)) or in_tools_list(word) :
            for ingredient in ingredients_list:
                for j in ingredient.get("ingredient_name",""):
                    if (word in j) and (ingredient not in final_ingredients):
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
    current_usage = extract_quantity_unit_pairs(text)
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

# Function to extract quantity + unit pairs from a sentence
def extract_quantity_unit_pairs(sentence):
    
    # Tokenize the sentence
    tokens = sentence.split()

    quantity_unit_pairs = []

    i=0
    while i < len(tokens) - 1:
        word = tokens[i]
        next_word = tokens[i + 1]

        # Check if the word is a number or fraction
        if is_number_or_fraction(word):
            # Lemmatize the next word (unit) to ensure we get the singular form
            lemma = lemmatizer.lemmatize(next_word.lower())

            while is_number_or_fraction(lemma):
                word += " "+next_word
                next_word = tokens[i + 2]
                lemma = lemmatizer.lemmatize(next_word.lower())
                i = i + 1

            if lemma in units or is_food(lemma) or lemma == "more":
                # If a valid unit follows the number, store the pair
                quantity_unit_pairs.append({"quantity": word, "unit": next_word})
        
        i=i+1
                
            

    
    # print("Hello", quantity_unit_pairs)
    return quantity_unit_pairs


test = Step(1, "Arrange in a single layer on a rimmed baking sheet.",[])

# test = Step(1, "Bake in the preheated oven until softened and lightly browned, 15 to 20 minutes.",[])

print(test.details)
print(test.text)
print(test.step_num)