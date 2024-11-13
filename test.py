import requests
from bs4 import BeautifulSoup

response = requests.get("https://www.allrecipes.com/roasted-butternut-squash-and-spinach-lasagna-recipe-7563610")
# response = requests.get("https://www.allrecipes.com/recipe/218091/classic-and-simple-meat-lasagna/")

# print(response.content)

soup = BeautifulSoup(response.content, "html.parser")
elements=soup.find_all(class_='mm-recipes-structured-ingredients__list-item')

for i in elements:
    print(i.text)

elements=soup.find_all(class_='comp mntl-sc-block mntl-sc-block-html')
for i in elements:
    print(i.text)