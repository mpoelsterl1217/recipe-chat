# import requests
# from bs4 import BeautifulSoup

# response = requests.get("https://www.allrecipes.com/roasted-butternut-squash-and-spinach-lasagna-recipe-7563610")
# # response = requests.get("https://www.allrecipes.com/recipe/218091/classic-and-simple-meat-lasagna/")

# # print(response.content)

# soup = BeautifulSoup(response.content, "html.parser")
# elements=soup.find_all(class_='mm-recipes-structured-ingredients__list-item')

# for i in elements:
#     print(i.text)

# elements=soup.find_all(class_='comp mntl-sc-block mntl-sc-block-html')
# for i in elements:
#     print(i.text)


# import nltk
# from nltk import word_tokenize, pos_tag

# def extract_numbers_nltk(text):
#     tokens = word_tokenize(text)
#     pos_tags = pos_tag(tokens)
#     numbers = []
#     for word, tag in pos_tags:
#         if tag == "CD" or word.lower() in {"next", "previous"}:
#             numbers.append(word)
#     return numbers

# # 示例
# text = "We 1ST"
# num = extract_numbers_nltk(text)
# if num and len(num)==1:
#     print("fuck")
# print(extract_numbers_nltk(text))
# # 输出: ['one', '2nd', 'previous']

# import re

import re

def extract_number(text):
    # Regex to match numbers at the beginning of the string
    match = re.match(r"(\d+)", text)
    if match:
        return int(match.group(1))  # Convert to integer if needed
    return None

# Test cases
examples = ["1st", "2nd", "3rd", "4th", "25th", "100th", "not-a-number", "1"]

for example in examples:
    print(f"{example} -> {extract_number(example)}")
