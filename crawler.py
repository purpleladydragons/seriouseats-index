import time
from selenium import webdriver
import lxml.html
import openai
from tenacity import retry, wait_random_exponential, stop_after_attempt
import sqlite3
from collections import deque
from colorama import Fore, Style
import os

conn = sqlite3.connect('urls.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS urls (url text, category text, scraped bool default 0)')

fireFoxOptions = webdriver.FirefoxOptions()
fireFoxOptions.headless = True
driver = webdriver.Firefox(executable_path=os.environ['GECKODRIVER_LOC'], options=fireFoxOptions)

start_url = 'https://www.seriouseats.com/all-recipes-5117985'


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def prompt_ai(prompt):
    resp = openai.Completion.create(
        model='ada:ft-personal-2022-11-10-03-39-57',
        prompt=prompt,
        temperature=0,
        max_tokens=1)
    return resp


# TODO this needs to become more generic if not just seriouseats
def scrape_urls(start_url):
    q = deque([start_url])

    recipes = []

    while q:
        url = q.popleft()

        # TODO i think what we can do is for lists, we check if seen
        # TODO if so, then skip, but if not then we still scrape it idk maybe. but i think it works bc the scraped things on it will not be prompted

        # if url exists in table, skip
        c.execute('SELECT * FROM urls WHERE url=?', (url,))
        if c.fetchone():
            continue

        # okay so a bit jank, but q should only ever contain lists so we add them
        # and we don't do it in the for url loop because then they don't execute themselves lol
        c.execute('INSERT INTO urls VALUES (?, ?)', (url, 'list'))
        conn.commit()

        print(Fore.CYAN, 'GETTING NEW LIST', Style.RESET_ALL)
        # TODO try/except around this url get
        driver.get(url)
        time.sleep(2)

        # get page source
        page_source = driver.page_source

        # use lxml to get all <a> tags from page source
        tree = lxml.html.fromstring(page_source)
        urls = tree.xpath('//a/@href')

        for url in urls:
            if 'guides' in url:
                continue

            c.execute('SELECT * FROM urls WHERE url=?', (url,))
            if c.fetchone():
                continue

            prompt = f'{url} ->'
            resp = prompt_ai(prompt)
            category = resp.choices[0].text.strip().lower()
            print(category, url)
            if category == 'list':
                q.append(url)
            elif category == 'recipe':
                recipes.append(url)

            # again very jank, but basically just trying to put all terminal nodes into the db as quick as possible
            if category != 'list':
                c.execute('INSERT INTO urls VALUES (?, ?)', (url, category))
                conn.commit()

    return recipes


recipes = scrape_urls(start_url)
for recipe in recipes:
    print(recipe)
