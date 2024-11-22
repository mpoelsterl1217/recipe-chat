from nltk.parse.stanford import StanfordParser
import nltk
from ingredient import Ingredient
from pathlib import Path
import subprocess


class IngredientParser:

    def __init__(self):
        parser_path = Path("stanford-corenlp-4.5.7/stanford-corenlp-4.5.7.jar")
        model_path = Path("stanford-corenlp-4.5.7/stanford-corenlp-4.5.7-models.jar")

        if not (parser_path.exists() and model_path.exists()):
            ## Download stanford coreNLP
            print("Need to download Stanford CoreNLP")
            subprocess.run("curl https://downloads.cs.stanford.edu/nlp/software/stanford-corenlp-4.5.7.zip -o stanford-corenlp-4.5.7.zip", shell=True)
            subprocess.run("unzip stanford-corenlp-4.5.7.zip", shell=True)

        self.server = nltk.parse.corenlp.CoreNLPServer(path_to_jar=str(parser_path), path_to_models_jar=str(model_path))
        self.server.start()
        self.parser = nltk.parse.corenlp.CoreNLPParser(url='http://localhost:9000')

    def __del__(self):
        self.server.stop()

    def parse_line(self, line):
        parts = line.split(",")

        if len(parts) > 2:
            raise Exception("Uh oh, there's more than 2 parts to the ingredient")

        if len(parts) == 2:
            ingredient_parse = self.parse_ingredient(parts[0])
            preparation_parse = self.parse_preparation(parts[1])
        elif len(parts) == 1:
            ingredient_parse = self.parse_ingredient(parts[0])
            preparation_parse = []
        else:
            raise Exception("Uh oh, there's more than no parts to ingredient")

        return Ingredient(ingredient_parse["quantity"],
                            ingredient_parse["unit"],
                            ingredient_parse["descriptors"],
                            ingredient_parse["name"],
                            preparation_parse)
        
    def parse_ingredient(self, ingredient_text):
        parse_tree = next(self.parser.raw_parse(ingredient_text))
        
        ingredient_phrase = self.find_ingredient_phrase(parse_tree)
        quantity_unit = self.find_quantity_unit(ingredient_phrase)
        quantity = quantity_unit[0]
        unit = quantity_unit[1]

        ingredient_name = " ".join([word for word in parse_tree.flatten()[0::] if word not in quantity_unit])
        name_tree = next(self.parser.raw_parse(ingredient_name))

        def is_descriptor_phrase(tree):
            if tree.label() == "JJ": return True
            if tree.label() == "ADJP": return True
            if tree.label() == "VBN": return True
            return False

        descriptors = [" ".join(tree.flatten()[0::]) for tree in name_tree.subtrees(is_descriptor_phrase)]
        descriptors = [word for word in descriptors if not any(map(lambda descriptor: word in descriptor and len(word) != len(descriptor), descriptors))]

        for descriptor in descriptors:
            ingredient_name = ingredient_name.replace(descriptor, "")

        ingredient_name = ingredient_name.strip()

        return {"quantity": quantity, "unit": unit, "descriptors": descriptors, "name": ingredient_name}

    def find_ingredient_phrase(self, tree):
        if tree[0].label() == "NP":
            return tree[0]
        elif tree[0][0].label() == "NP":
            return tree[0][0]
           
        raise Exception(f"uh oh, could not find ingredient phrase in {tree}")

    def find_quantity_unit(self, ingredient_phrase):
        if ingredient_phrase[0].label() == "CD":
            if ingredient_phrase[1].label().startswith("NN"): # Cardinal numeral is followed by noun, assumed to be unit
                return [ingredient_phrase[0][-1], ingredient_phrase[1][-1]]
            return [ingredient_phrase[0][-1], ""] # No noun following CD, so no unit
        elif ingredient_phrase[0].label() == "NML" or ingredient_phrase[0].label() == "NP":
            nml_phrase = ingredient_phrase[0]
            if nml_phrase[0].label() == "CD": 
                if nml_phrase[1].label().startswith("NN"): # Cardinal numeral is followed by noun, assumed to be unit
                    return [nml_phrase[0][-1], nml_phrase[1][-1]]
                return [nml_phrase[0][-1], ""]
            
        raise Exception(f"uh oh, could not find quantity and unit in {ingredient_phrase}")


    def parse_preparation(self, preparation_text):
        parse_tree = next(self.parser.raw_parse(preparation_text))
        preparation_phrase = self.find_preparation_phrase(parse_tree)
        def is_prep_step(tree):
            return tree.label() == "VP" and tree[0].label() == "VBN"
        prep_steps = preparation_phrase.subtrees(is_prep_step)
        steps = [" ".join(step.flatten()[0::]) for step in prep_steps]
        return steps

    def find_preparation_phrase(self, tree):
        if tree[0][0].label() == "VP":
            return tree[0][0]
        
        raise Exception(f"uh oh, could not find preparation phrase in {tree}")



if __name__ == "__main__":
    lines = ["3 large russet potatoes, peeled and cut in half lengthwise",
            "½ cup whole milk",
            "¼ cup butter",
            "1 cup butter",
            "2 cups chopped onion",
            "2 tbsp freshly ground pepper"]
    
    parser = IngredientParser()

    for line in lines:
        parser.parse_line(line)

    