import nltk
import spacy
from nltk.corpus import wordnet as wn
from lists import in_tools_list, in_verbs_list
# from verbnet import VerbNet

nltk.download('wordnet')
nlp = spacy.load("en_core_web_sm")
# vn = VerbNet()

class Step:
    def __init__(self, snum, text):
        
        ingredients, tools, actions = parse_step(text.lower())
        
        self.step_num = snum
        self.text = text
        self.details = {}
        # TIME
        self.time = None
        # TEMPERATURE
        if ingredients != []:
            self.details["ingredients"] = ingredients
        if tools != []:
            self.details["tools"] = tools
        if actions != []:
            self.details["actions"] = actions
        # print(self.details)

    def __str__(self):
        return str(self.snum) + self.text # + str(self.details)

def parse_step(text):

    # nlp.add_pipe("merge_noun_chunks")
    doc = nlp(text)

    ingredients, actions, tools = [], [], []
    # print("doc", doc)
    for ent in doc:
        # print(ent)
        word = ent.text
        if ent.pos_ in ["NOUN", "PROPN"]:
            if is_food(word):
                ingredients.append(word)
            if in_tools_list(word) or is_cooking_tool(word):
                tools.append(word)
        if ent.pos_ in ["VERB", "ROOT"]:
            if in_verbs_list(word) or is_cooking_action(word):
                actions.append(word)
                # print(f"Verb: {ent.text}, Object(s): {[child.text for child in ent.children if child.dep_ == 'dobj']}")
    # print("FOOD", [ent.text for ent in doc if ent.label_ in ["PRODUCT", "FOOD"]])
    ingredients = list(set(clean_nouns(ingredients, doc)))
    tools = list(set(clean_nouns(tools, doc)))
    actions = list(set(actions))
    return ingredients, tools, actions

def is_food(word):
    syns = wn.synsets(word, pos = wn.NOUN)
    for syn in syns:
        if 'food' in syn.lexname():
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

# Step(1, "Grease the bowl with butter. Place the dough back into the bowl, cover, and let rise for 30 minutes. Get ice cream from the sharp knife.")