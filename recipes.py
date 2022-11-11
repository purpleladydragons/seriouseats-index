import os
import sys
import time

import openai
from selenium import webdriver
import lxml.html
from lxml import etree

from calories import fetch_calories

openai.api_key = os.getenv("OPENAI_API_KEY")

recipe_url = sys.argv[1]

fireFoxOptions = webdriver.FirefoxOptions()
fireFoxOptions.headless = True
driver = webdriver.Firefox(executable_path=os.environ['GECKODRIVER_LOC'], options=fireFoxOptions)


# TODO this needs to become more generic if not just seriouseats
def scrape_page(url):
    driver.get(url)
    time.sleep(2)

    # get page source
    page_source = driver.page_source

    # use lxml to get all <a> tags from page source
    tree = lxml.html.fromstring(page_source)
    ingredients_section = tree.xpath('//section[contains(@class, "ingredients")]')[0]
    ingredients_html = etree.tostring(ingredients_section, pretty_print=True).decode('utf-8').replace('\n', '')

    return ingredients_html


def prompt_ai(html):
    prompt = f"""HTML page describing ingredients for a recipe:
    
{html}

|Ingredient|Quantity|Unit|"""

    resp = openai.Completion.create(prompt=prompt, engine="text-davinci-002", max_tokens=350,
                                    temperature=0, top_p=1, frequency_penalty=0.0, presence_penalty=0.0)
    return resp


def parse_ingredients(ingredients):
    # Parse list of ingredients in format |Ingredient|Quantity|Unit| into list of dicts
    ingredients = ingredients.choices[0].text.split('\n')
    print(ingredients)
    ingredients = [i.split('|') for i in ingredients]
    ingredients = [i for i in ingredients if len(i) == 5]
    ingredients = [{'ingredient': i[1], 'quantity': i[2], 'unit': i[3]} for i in ingredients]
    return ingredients


def fetch_ingredients_from_recipe(recipe_url):
    html = scrape_page(recipe_url)

    resp = prompt_ai(html)

    ingredients = parse_ingredients(resp)

    return ingredients


def get_calories(ingredients):
    total_calories = 0
    for ingredient in ingredients:
        calories = fetch_calories(ingredient['ingredient'], ingredient['quantity'])
        print(ingredient['ingredient'], ingredient['quantity'], calories)
        total_calories += calories

    print(total_calories)