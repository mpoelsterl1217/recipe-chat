from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# Assuming 'units' is a predefined list of unit words
units = ["cup", "tsp", "liter", "ml", "gram"]

# Helper function to check if a word is related to food
def is_food(word):
    lemma = lemmatizer.lemmatize(word.lower())
    synsets = wn.synsets(lemma, pos=wn.NOUN)
    
    # Iterate through synsets and filter by 'food' or related categories
    for syn in synsets:
        lexname = syn.lexname().lower()
        if 'food' in lexname or 'dairy_product' in lexname:
            return True
    return False

# Function to find possible substitutions (synonyms and hypernyms)
def find_substitutions(word):
    lemma = lemmatizer.lemmatize(word.lower())
    synsets = wn.synsets(lemma, pos=wn.NOUN)
    
    substitutions = set()

    # Iterate through synsets to find synonyms or related words
    for syn in synsets:
        lexname = syn.lexname().lower()
        
        # Add synonyms (lemmas) from the synset
        for lemma in syn.lemmas():
            if 'food' in lexname or 'dairy_product' in lexname:
                substitutions.add(lemma.name())

        # Add hypernyms (broader categories) related to food or ingredients
        for hypernym in syn.hypernyms():
            for lemma in hypernym.lemmas():
                if 'food' in hypernym.lexname().lower() or 'dairy_product' in hypernym.lexname().lower():
                    substitutions.add(lemma.name())

    # Return unique substitutions (excluding the original word)
    return [sub for sub in substitutions if sub != word]

# Example usage
ingredient = "butter"
if is_food(ingredient):
    substitutes = find_substitutions(ingredient)
    print(f"Possible substitutions for {ingredient}: {', '.join(substitutes)}")
else:
    print(f"{ingredient} is not identified as food.")
