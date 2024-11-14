import requests
from bs4 import BeautifulSoup

def grab_info(response):
    # todo
    soup = BeautifulSoup(response.content, "html.parser")
    ingredients = soup.find(class_='mm-recipes-structured-ingredients__list')
    ingredients_list = []
    for i in ingredients:
        ingredients_list.append(i.text)
    
    steps=soup.find_all(class_='comp mntl-sc-block mntl-sc-block-html')
    steps_list=[]
    for i in steps:
        steps_list.append(i.text)
    
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

def main():
    print("Please provide a valid AllRecipes.com URL or type 'q' to quit the program")
    url = input()
    if url.lower()=='q':
        print("Bye!")
        return
    continue_or_quit = conform_url(url)
    if continue_or_quit:
        response = requests.get(url)
        ingredients_list, steps_list = grab_info(response)
        # 
        print("Alright. So let's start working with the url. What do you want to do?")
        print("[1] Go over ingredients list ")
        print("[2] Go over recipe steps. ")

        while True:
            num=input()
            if num=='1':
                print(ingredients_list)
                break
            elif num=='2':
                print(steps_list)
                break
            else:
                print("error input, try again!")
        
        # todo understand what user input and response with what we get from websites

        user_input=input()
        # 5 & 6. Simple "what is" questions. Specific "how to" questions
        if "how" or "what" in user_input.lower():
            reference_url="+".join(user_input.split(" "))
            print("No worries. I found a reference for you: https://www.google.com/search?q=" + reference_url)
        

    else:
        print("URL does not exist on Internet." )
        main()

if __name__ == "__main__": main()