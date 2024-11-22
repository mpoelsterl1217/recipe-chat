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
        
    # print("Hello!!")

    for i in steps:
        # Pre-split text by semicolons before applying sent_tokenize
        semi_split = i.text.split(";")
        for part in semi_split:
            sentences = sent_tokenize(part.strip())  # Strip whitespace and tokenize
            for j in sentences:
                steps_list.append(Step(num, j.strip(), ingredients_list))  # Remove extra spaces
                num += 1

    for i in steps_list:
        print(i.text)
        print(i.details)
        print()
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
    if ingredients == [] or ingredients == None:
        return "Sorry, I'm having trouble retrieving the list. Would you like to ask another question?\n"
    response = "Sure! You will need:"
    for ingredient in ingredients:
        response += "\n"+ingredient["text"]
    response += "\nWhat else would you like to know?"
    return response

def main1():
    # input_history = []
    # respond_history = []
    # current_step = 0
    # # current_ingredient = 0
    # print("Please provide a valid AllRecipes.com URL or type 'q' to quit the program")
    # url = input()
    # if url.lower()=='q':
    #     print("Bye!")
    #     return
    # continue_or_quit = confirm_url(url)
    # if continue_or_quit:
    #     response = requests.get(url)
    #     ingredients_list, steps_list = grab_info(response)
    #     # 
    #     print("Alright. Let's start working with your recipe. What do you want to do?")
    #     print("[1] Go over ingredients list ")
    #     print("[2] Go over recipe steps ")
    #     print("[3] Ask a question about the recipe")

    #     while True:
    #         num=input()
    #         if num=='1':
    #             print(format_ingredients_request(ingredients_list))
    #             input_history.append("1")
    #             respond_history.append(format_ingredients_request(ingredients_list))
    #             break
    #         elif num=='2':
    #             print(steps_list[0])
    #             input_history.append("2")
    #             respond_history.append(steps_list[0])
    #             current_step = 0
    #             break
    #         elif num=="3":
    #             break
    #         else:
    #             print("I don't understand your response. Try again?")
        
        # TODO: understand what user input and response with what we get from websites
        while True:
            user_input = input().lower()
            print("current input:", user_input)
            input_history.append(user_input)
            # 1 example
            # if "show me the ingredients list" in user_input:
            #     print(ingredients_list)
            #     print()
            #     respond_history.append(ingredients_list)
            #     continue
        
            # if "show me the step" in user_input or "show me the recipe steps" in user_input:
            #     print(steps_list)
            #     print()
            #     respond_history.append(steps_list)

            # 2 exmaple
            num = extract_numbers_nltk(user_input)
            if num and len(num)==1 and not "how" in user_input and not "what" in user_input:
                if "repeat" in num:
                    print(steps_list[current_step])
                    print()
                    continue
                if "step" in user_input:
                    if "previous" in num:
                        if current_step-1 < 0:
                            print("no previous step")
                            print()
                            continue
                        else:
                            current_step -=1
                            print(steps_list[current_step])
                            print()
                    # elif "next" in num:
                    #     if current_step + 1 >= len(steps_list):
                    #         print("no next step")
                    #         print()
                    #         continue
                    #     else:
                    #         current_step +=1
                    #         print(steps_list[current_step])
                    #         print()
                    elif "repeat" in num or "current" in num:
                        print(steps_list[current_step])
                        print()
                    else:
                        if extract_number_re(num[-1]) - 1 < 0 or extract_number_re(num[-1]) - 1 >= len(steps_list):
                            print("no such step")
                            print()
                            continue
                        else:
                            current_step = extract_number_re(num[-1]) - 1
                            print(steps_list[current_step])
                            print()
                    
                    respond_history.append(steps_list[current_step])
                    
                    continue
            
            # 3 exmple



    #         # 4 & 5 & 6. Simple "what is" questions. Specific "how to" questions
    #         inquiries = ["how do i", "how might i", "how can i", "what can i", "what is", "how long does it take to", "what does __ mean"]
    #         if any(inquiries in user_input):
    #             # print("4,5,6")

    #         # 6 use conversation history to infer what “that” refers to. may use SpaCy to deal with it.
    #             if "how to" in user_input and ("that" in user_input or "this" in user_input or "these" in user_input or "those" in user_input):
    #                 reference_url = respond_history[-1]
    #                 reference_url="+".join(reference_url.split(" "))
    #                 # should we get the first article that comes up or just search on google directly??
    #                 print("I found a reference for you: " + find_article(user_input))
    #                 # print("Would you like me to find a video or another reference?")
    #                 # answer = input()
    #                 # if answer == "yes"
    #                 # 
    #                 print()
    #                 continue
            
    #             reference_url="+".join(user_input.split(" "))
    #             print("I found a reference for you: " + find_article(user_input))
    #             continue
            
    #         # invaild input
    #         print("I'm sorry, I don't understand. Can you rephrase your input?")

    #         continue
        

    # else:
    #     print("URL does not exist on Internet." )
    #     main()


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

    inquiries = ["how do i", "how might i", "how can i", "what can i", "what is", "how long does it take to", "what does __ mean"]
    next_step_asks = ["next step"]
    first_step_asks = ["1st step", "first step", "where do i begin", "how do i start", "tell me how to start"]
    all_step_asks = ["all the steps", "every step", "the whole steps list", "show me the steps"]
    quantity_regex = re.compile("how (much|many|much of|many of) (.+) do i need(.+)")

    # how much ___ do i need?
    if re.search(quantity_regex, user_input):
        output = ""
        ingredient = re.search(quantity_regex, user_input).group[1]
        for i in model.ingredient_list:
            if ingredient in i.text:
                output = "You will need " + i.text + "."
        if output == "":
            output = "I'm not sure right now. Let me know if you would like to see the ingredients list."
    
    # what tools do i need for this recipe?
    if ("what tools" in user_input or "which tools" in user_input) and "recipe" in user_input:
        output = "For this recipe, you will need:"
        for step in model.steps_list:
            if step.tools:
                for t in step.tools:
                    output += "\n" + t
        if output == "For this recipe, you will need:":
            output = "Sorry, I'm having trouble retrieving that information right now. Would you like to ask another question?"
        
    # what tools do i need for this step?
    elif ("what tools" in user_input or "which tools" in user_input) and "this step" in user_input:
        if not model.in_steps:
            output = "We haven't looked at the steps yet."
        elif model.steps_list[model.current_step].tools:
            output = "For this step, you will need:"
            for t in model.steps_list[model.current_step].tools:
                output += "\n" + t
        else:
            output = "I don't believe you need any new tools right now. Let me know if you would like to repeat the step."
        
    # what ingredients do i need for this step?
    elif ("what ingredients" in user_input or "which ingredients" in user_input) and "this step" in user_input:
        if not model.in_steps:
            output = "We haven't looked at the steps yet."
        elif model.steps_list[model.current_step].ingredients:
            output = format_ingredients_request(model.steps_list[model.current_step].ingredients)
        else:
            output = "I don't believe you need any new ingredients right now. Let me know if you would like me to repeat the step."

    # what ingredients do i need?
    elif (("what ingredients" in user_input or "which ingredients" in user_input) and "recipe" in user_input) \
        or "ingredients list" in user_input:
        output = format_ingredients_request(model.ingredient_list)
    
    # tell me the first step / where do i begin?
    elif any(asks in user_input for asks in first_step_asks):
        model.in_steps = True
        model.current_step = 0
        output = "The first step is: " + model.steps_list[0].text

    # show me the next step
    elif any(asks in user_input for asks in next_step_asks):
        if not model.in_steps:
            output = "The first step is: " + model.steps_list[0].text
            model.current_step = 0
        elif model.current_step + 1 >= len(model.steps_list):
            output = "There is no next step! You're done!"
        else:
            output = "The next step is: " + model.steps_list[model.current_step + 1].text
            model.current_step += 1

    # show me the steps list
    elif any(asks in user_input for asks in all_step_asks):
        output = "Sure. The steps list is as follows:\n"
        for step in model.steps_list:
            output += step.text + "\n"

    # how do i preheat the oven? (any question that requires external knowledge)
    elif any(inquiry in user_input for inquiry in inquiries):
        if user_input[-1] == "?":
            user_input = user_input[:-1]
        # 6 use conversation history to infer what “that” refers to. may use SpaCy to deal with it.
        if "how to" in user_input and ("that" in user_input or "this" in user_input or "these" in user_input or "those" in user_input):
            # TODO: FIX THIS
            reference_url = model.response_history[-1]
            reference_url="+".join(reference_url.split(" "))
        else:
            reference_url="+".join(user_input.split(" "))
        output = "I found a reference for you: " + find_article(user_input)
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
    model.output_history.append(output)

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