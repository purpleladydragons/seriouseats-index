import time
import selenium.common
from selenium import webdriver
import sqlite3

fireFoxOptions = webdriver.FirefoxOptions()
fireFoxOptions.headless = True
driver = webdriver.Firefox(executable_path='/Users/austinsteady/Downloads/geckodriver', options=fireFoxOptions)

conn = sqlite3.connect('urls.db')
c = conn.cursor()

# get all recipes from db
recipes = c.execute('SELECT * FROM urls WHERE category="recipe"').fetchall()

for recipe in recipes:
    if recipe[2]:
        continue

    print(recipe)
    try:
        driver.get(recipe[0])
        time.sleep(1)
    except selenium.common.exceptions.InvalidArgumentException:
        print('invalid url', recipe[0])
        continue
    except selenium.common.exceptions.TimeoutException:
        print('timeout', recipe[0])
        continue
    page_source = driver.page_source
    with open(f'scraped_recipes/{recipe[0].split("/")[-1]}.html', 'w') as f:
        f.write(page_source)

    c.execute('UPDATE urls SET scraped=1 WHERE url=?', (recipe[0],))
    conn.commit()





