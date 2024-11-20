import requests
from bs4 import BeautifulSoup
import nltk
from nltk import word_tokenize, pos_tag
import re
from find_article import find_article

def grab_info(response):
    # todo
    soup = BeautifulSoup(response.content, "html.parser")
    ingredients = soup.find(class_='mm-recipes-structured-ingredients__list')
    ingredients_list = []
    for i in ingredients:
        ingredients_list.append(i.text)
    # ingredients_list.pop(0)
    ingredients_list = [item.strip() for item in ingredients_list]
    ingredients_list = [item for item in ingredients_list if item != ""]   
    
    steps=soup.find_all(class_='comp mntl-sc-block mntl-sc-block-html')
    steps_list=[]
    for i in steps:
        steps_list.append(i.text)
    # steps_list.pop(0)
    steps_list = [item.strip() for item in steps_list]
    steps_list = [item for item in steps_list if item != ""] 
    
    return ingredients_list, steps_list

# access and preprocessing the url. Return true if the url exist.
def conform_url(url):
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

def main():
    input_history = []
    respond_history = []
    current_step = 0
    current_ingredient = 0
    print("Please provide a valid AllRecipes.com URL or type 'q' to quit the program")
    # url = input()
    url = "https://www.allrecipes.com/recipe/244765/easy-mexican-chicken-spaghetti/"
    if url.lower()=='q':
        print("Bye!")
        return
    continue_or_quit = conform_url(url)
    if continue_or_quit:
        response = requests.get(url)
        ingredients_list, steps_list = grab_info(response)
        # 
        print("Alright. So let's start working with your recipe. What do you want to do?")
        print("[1] Go over ingredients list ")
        print("[2] Go over recipe steps. ")
        # print("[3] Ask a question about the recipe")

        while True:
            num=input()
            if num=='1':
                print(ingredients_list[0])
                input_history.append("1")
                respond_history.append(ingredients_list[0])
                current_ingredient = 0
                break
            elif num=='2':
                print(steps_list[0])
                input_history.append("2")
                respond_history.append(steps_list[0])
                current_step = 0
                break
            else:
                print("error input, try again!")
        
        # todo understand what user input and response with what we get from websites
        while True:
            user_input=input()
            print("cuurent input:", user_input)
            input_history.append(user_input)
            # 1 example
            if "Show me the ingredients list" in user_input:
                print(ingredients_list)
                print()
                respond_history.append(ingredients_list)
                continue
        
            if "Show me the step list" in user_input:
                print(steps_list)
                print()
                respond_history.append(steps_list)

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
                    elif "next" in num:
                        if current_step + 1 >= len(steps_list):
                            print("no next step")
                            print()
                            continue
                        else:
                            current_step +=1
                            print(steps_list[current_step])
                            print()
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



            # 4 & 5 & 6. Simple "what is" questions. Specific "how to" questions
            # ["how do i", "how might i", "how can i", "what can i", "what is", "how long does it take to", "what does __ mean"]
            if "how to" in user_input.lower() or "what is" in user_input.lower():
                # print("4,5,6")

            # 6 use conversation history to infer what “that” refers to. may use SpaCy to deal with it.
                if "how to" in user_input.lower() and ("that" in user_input.lower() or "this" in user_input.lower() or "these" in user_input.lower() or "those" in user_input.lower()):
                    reference_url = respond_history[-1]
                    reference_url="+".join(reference_url.split(" "))
                    # should we get the first article that comes up or just search on google directly??
                    print("No worries. I found a reference for you: " + find_article(user_input))
                    # print("Would you like me to find a video or another reference?")
                    # answer = input()
                    # if answer == "yes"
                    # 
                    print()
                    continue
            
                reference_url="+".join(user_input.split(" "))
                print("No worries. I found a reference for you: " + find_article(user_input))
                print()
                continue
            
            # invaild input
            # print("I'm sorry, I don't understand. Can you rephrase your input?")
            print("Please provide an vaild input !")
            print()

            continue
        

    else:
        print("URL does not exist on Internet." )
        main()

if __name__ == "__main__": main()