import requests
from bs4 import BeautifulSoup
import nltk
from nltk import word_tokenize, pos_tag
import re
from find_article import find_article
from step import Step
from parse_ingredients import parse_ingredients
from model_state import State
from nltk.tokenize import sent_tokenize

def grab_info(response):
    # todo
    print("parsing...")
    soup = BeautifulSoup(response.content, "html.parser")
    ingredients = soup.find(class_='mm-recipes-structured-ingredients__list')
    ingredients_list = []
    if len(ingredients) == 0:
        print("Sorry, something seems to be going wrong. I'm having trouble finding the ingredients for this recipe. Feel free to ask questions about the steps or restart the program with a new url.")
        ingredients_list = None
    for i in ingredients:
        ingredients_list.append(i.text)
    # ingredients_list.pop(0)
    ingredients_list = [item.strip() for item in ingredients_list]
    ingredients_list = [item for item in ingredients_list if item != ""]   
    ingredients_list = parse_ingredients(ingredients_list)
    
    # steps=soup.find_all(class_='comp mntl-sc-block mntl-sc-block-html')
    steps_list=[]
    steps=[]
    step_content = soup.find_all(class_='comp mm-recipes-steps__content mntl-sc-page mntl-block')# .split()
    step_blocks = step_content[0].find_all('li')
    for b in step_blocks:
        steps.append(b.find_all('p', class_='comp mntl-sc-block mntl-sc-block-html')[0])
    num = 1
    if len(steps) == 0:
        print("Sorry, something seems to be going wrong. I'm having trouble finding the steps for this recipe. Feel free to ask questions about the ingredients or restart the program with a new url.")
        steps_list = None
        

    for i in steps:
        # Pre-split text by semicolons before applying sent_tokenize
        semi_split = i.text.split(";")
        for part in semi_split:
            sentences = sent_tokenize(part.strip())  # Strip whitespace and tokenize
            for j in sentences:
                steps_list.append(Step(num, j.strip(), ingredients_list))

                num += 1

    #for i in steps_list:
       # print(i.text)
        #print(i.details)
        #print()
    # steps_list.pop(0)
    # steps_list = [item.strip() for item in steps_list]
    # steps_list = [item for item in steps_list if item != ""] 
    
    return ingredients_list, steps_list

# access and preprocessing the url. Return true if the url exist.
def confirm_url(url):
    # check url is exist.
    try:
        response = requests.get(url)
        # preprocessing the url.
        return True
    except requests.exceptions.MissingSchema:
        return False
    except requests.ConnectionError:
        return False

def extract_numbers_nltk(text):
    tokens = word_tokenize(text)
    pos_tags = pos_tag(tokens)
    numbers = []
    for word, tag in pos_tags:
        if tag == "CD" or word.lower() in {"next", "previous", "repeat", "current"}:
            numbers.append(word.lower())
    return numbers

def extract_number_re(text):
    # Regex to match numbers at the beginning of the string
    match = re.match(r"(\d+)", text)
    if match:
        return int(match.group(1))  # Convert to integer if needed
    return -1

def format_ingredients_request(ingredients):
    print(f"ingredients: {ingredients}")
    if ingredients == [] or ingredients == None:
        return "Sorry, I'm having trouble retrieving the list. Would you like to ask another question?\n"
    response = "Sure! You will need:"
    for ingredient in ingredients:
        response += f"\n {ingredient}"
    response += "\nWhat else would you like to know?"
    return response

def get_init_info():
    
    print("Please provide a valid AllRecipes.com URL or type 'q' at any time to quit the program.")
    url = input()
    if url.lower()=='q':
        print("Bye!")
        return "q"
    continue_or_quit = confirm_url(url)
    if continue_or_quit:
        response = requests.get(url)
        return grab_info(response)
    else:
        return None
    

def setup(model):

    # TODO: add title of recipe here
    print()
    print("Alright. Let's start working with your recipe. What do you want to do?")
    print("[1] Go over ingredients list ")
    print("[2] Go over recipe steps ")
    print("[3] Ask a question about the recipe")

    num=input()
    output = ""
    model.input_history.append(num)

    while True:
        if num=='1':
            output = format_ingredients_request(model.ingredient_list)
            break
        elif num=='2':
            output = "Great! the first step is: " + model.steps_list[0].text
            model.in_steps = True
            model.current_step = 0
            break
        elif num=="3":
            output = "Great! What is your question?"
            break
        else:
            print()
            print("I don't understand your response. Try again?")
            num = input()
        
    print()
    print(output)
    model.output_history.append(output)
    return model


def get_chatbot_response(user_input, model):

    model.input_history.append(user_input)

    inquiries = ["how do i", "how might i", "how can i", "what can i", "what is", "what does __ mean", "what is", "how to"]
    next_step_asks = ["next step", "what's next", "go to the next step", "show me the next step"]
    previous_step_asks = ["previous step", "Go back one step"]
    current_step_asks = ["repeat please", "repeat step", "current step", "show me the current step"]
    first_step_asks = ["1st step", "first step", "where do i begin", "how do i start", "tell me how to start"]
    all_step_asks = ["all the steps", "every step", "the whole steps list", "show me the steps"]
    duration_asks = ["how long", "how much time"] # TODO: add more duration asks
    quantity_regex = re.compile("how (much|many|much of|many of) (.+) do i|I need(.+)")
    descriptor_regex = re.compile("What is the description of (.+)")
    ordinal_regex = r"(?P<ordinal>(?P<numeral>\d*)(th|st|nd|rd))"
    nth_step_regexes = [rf"take me to the {ordinal_regex} step",
                                        rf"what's the {ordinal_regex} step", rf"{ordinal_regex} step"]
    

    # n-th step requests
    matching_regex = None
    for nth_step_regex in nth_step_regexes:
        if re.search(nth_step_regex, user_input):
            matching_regex = nth_step_regex
            break


    # how much ___ do i need?
    if re.search(quantity_regex, user_input):
        output = ""
        # print("Hello")
        # print(re.search(quantity_regex, user_input).group(2))
        ingredient = re.search(quantity_regex, user_input).group(2)
        count=0
        # print(model.steps_list[model.current_step].details)
        for i in model.steps_list[model.current_step].details.get("ingredients"):
            # print(i)
            if ingredient in i.ingredient_name:
                current_usage_list=model.steps_list[model.current_step].details.get("current_uasge")
                for current_usage in current_usage_list:
                    if ingredient in current_usage.get("ingredient_name"):
                        output = "You will need " + current_usage.get("quantity") + " " + current_usage.get("unit") + "."
                        model.output_history.append(current_usage.get("quantity") + " " + current_usage.get("unit") + " " + current_usage.get("ingredient_name"))
                        break
            count+=1
        
        if output == "":
            output = "I'm not sure right now. Let me know if you would like to see the ingredients list."

    # elif re.search(descriptor_regex, user_input):
    #     output = ""
    #     ingredient = re.search(quantity_regex, user_input).group(5)
    #     for i in model.steps_list[model.current_step].details.get("ingredients"):

    elif matching_regex:
        matches = re.search(matching_regex, user_input)
        step_num = int(matches.group("numeral"))
        if step_num > len(model.steps_list) or step_num < 1:
            output = f"Sorry, there are only {len(model.steps_list)} steps."
        else:
            model.current_step = step_num - 1
            model.in_steps = True
            output = f"The {matches.group('ordinal')} step is: " + model.steps_list[model.current_step].text
            model.output_history.append(model.steps_list[model.current_step].text)

    
    # what tools do i need for this recipe?
    elif ("what tools" in user_input or "which tools" in user_input) and "recipe" in user_input:
        output = "For this recipe, you will need:"
        for step in model.steps_list:
            if step.details.get("tools"):
                for t in step.details["tools"]:
                    output += "\n" + t
                model.output_history.append(output)
        if output == "For this recipe, you will need:":
            output = "Sorry, I'm having trouble retrieving that information right now. Would you like to ask another question?"
        
    # what tools do i need for this step?
    elif ("what tools" in user_input or "which tools" in user_input) and "this step" in user_input:
        if not model.in_steps:
            output = "We haven't looked at the steps yet."
        elif model.steps_list[model.current_step].details.get("tools"):
            output = "For this step, you will need:"
            for t in model.steps_list[model.current_step].details["tools"]:
                output += "\n" + t
            model.output_history.append(output)
        else:
            output = "I don't believe you need any new tools right now. Let me know if you would like to repeat the step."

    # what methods do i need for this step?
    elif ("what methods" in user_input or "which methods" in user_input) and "this step" in user_input:
        if not model.in_steps:
            output = "We haven't looked at the steps yet."
        elif model.steps_list[model.current_step].details.get("actions"):
            output = "For this step, you will need:"
            for t in model.steps_list[model.current_step].details["actions"]:
                output += "\n" + t
            model.output_history.append(output)
        else:
            output = "I don't believe you need any new actions right now. Let me know if you would like to repeat the step."
        
    # what ingredients do i need for this step?
    elif ("what ingredients" in user_input or "which ingredients" in user_input) and "this step" in user_input:
        if not model.in_steps:
            output = "We haven't looked at the steps yet."
        elif model.steps_list[model.current_step].details.get("ingredients"):
            output = format_ingredients_request(model.steps_list[model.current_step].details["ingredients"])
            model.output_history.append(output)
        else:
            output = "I don't believe you need any new ingredients right now. Let me know if you would like me to repeat the step."

    # what ingredients do i need?
    elif (("what ingredients" in user_input or "which ingredients" in user_input) and "recipe" in user_input) \
        or "ingredients list" in user_input:
        output = format_ingredients_request(model.ingredient_list)
        model.output_history.append(output)
    
    # tell me the first step / where do i begin?
    elif any(asks in user_input for asks in first_step_asks):
        model.in_steps = True
        model.current_step = 0
        output = "The first step is: " + model.steps_list[0].text
        model.output_history.append(output)

    # tell me the current step?
    elif any(asks in user_input for asks in current_step_asks):
        model.in_steps = True
        output = "The current step is: " + model.steps_list[model.current_step].text
        model.output_history.append(output)

    # show me the next step
    elif any(asks in user_input for asks in next_step_asks):
        if not model.in_steps:
            output = "The first step is: " + model.steps_list[0].text
            model.output_history.append(output)
            model.current_step = 0
        elif model.current_step + 1 >= len(model.steps_list):
            output = "There is no next step! You're done!"
        else:
            output = "The next step is: " + model.steps_list[model.current_step + 1].text
            model.output_history.append(output)
            model.current_step += 1
    
    # show me the previous step
    elif any(asks in user_input for asks in previous_step_asks):
        if not model.in_steps:
            output = "The first step is: " + model.steps_list[0].text
            model.output_history.append(output)
            model.current_step = 0
        elif model.current_step - 1 < 0:
            output = "There is no previous step! You're done!"
        else:
            output = "The previous step is: " + model.steps_list[model.current_step - 1].text
            model.output_history.append(output)
            model.current_step -= 1

    # show me the steps list
    elif any(asks in user_input for asks in all_step_asks):
        output = "Sure. The steps list is as follows:\n"
        for step in model.steps_list:
            output += step.text + "\n"
        model.output_history.append(output)

    # What temperature
    elif "temp" in user_input:
        current_step_num = model.current_step
        current_step = model.steps_list[current_step_num]
        if current_step.details.get("temp") != None:
            temp_info = current_step.details["temp"]
            temps = [f"{temp['value']}{temp['unit'].upper()}" for temp in temp_info]
            output = f"The temperature should be : {'/'.join(temps)}"
            model.output_history.append(output)
        else:
            # TODO: improve this response
            output = "The step you are are currently on does not have a temperature."

    elif any(asks in user_input for asks in duration_asks):
        # TODO: improve this
        if model.current_step != None:
            current_step_num = model.current_step
            current_step = model.steps_list[current_step_num]
            if current_step.details.get("time") != None:
                output = f"{current_step.details['time']}"
                model.output_history.append(output)
            else:
                output = "If you're done with the last step, you can move on to the next"


    # how do i preheat the oven? (any question that requires external knowledge)
    elif any(inquiry in user_input for inquiry in inquiries):
        if user_input[-1] == "?":
            user_input = user_input[:-1]
        # 6 use conversation history to infer what “that” refers to. may use SpaCy to deal with it.
        that_list=["that", "this", "these", "those", "them", "it"]
        if  ("that" in user_input or "this" in user_input or "these" in user_input or "those" in user_input or "them" in user_input or "it" in user_input):
            # TODO: FIX THIS
            if model.output_history:
                reference_url = model.output_history[-1]
                reference_url = reference_url.split(":")[-1]
                reference_url = reference_url.replace("\n", " ")
                reference_url="+".join(reference_url.split(" "))
        else:
            reference_url="+".join(user_input.split(" "))
        output = "I found a reference for you: https://www.google.com/search?q=" + reference_url
         # print("Would you like me to find a video or another reference?")
            # answer = input()
            # if answer == "yes"

    # thank you!
    elif "thank" in user_input:
        output = "You're welcome! What would you like to know next?"

    # anything else
    else:
        output = "I'm sorry, I don't understand. Can you rephrase your input?"

    print()
    print(output)
    print()
    # model.output_history.append(output)

    return model


def main():

    print()
    print("Hello! My name is Dirk. Let's get you started!")

    init_info = get_init_info()
    if init_info == 'q':
        return
    while init_info is None:
        print()
        print("I'm sorry, I don't understand your input.")
        init_info = get_init_info()
        if init_info == 'q':
            return
    in_list, step_list = init_info
    model = State(step_list, in_list)
    model = setup(model)

    while True:
        user_input = input().lower()
        if user_input == "q":
            print("It was nice chatting with you!")
            return
        model = get_chatbot_response(user_input, model)


if __name__ == "__main__": main()