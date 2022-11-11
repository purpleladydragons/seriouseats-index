import time
import sqlite3
import lxml.html

conn = sqlite3.connect('urls.db')
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS contents (content text, url text)')

# get all recipes from db
recipes = c.execute('SELECT * FROM urls WHERE category="recipe"').fetchall()

# for each recipe, get corresponding html file in scraped_recipes
failures = 0
for i, recipe in enumerate(recipes):
    if i % 100 == 0:
        print(i)
    if recipe[2] is None:
        continue

    recipe_name = recipe[0].split('/')[-1]
    with open(f'scraped_recipes/{recipe_name}.html', 'r') as f:
        page_source = f.read()

        tree = lxml.html.fromstring(page_source)
        content = tree.xpath('normalize-space(//div[contains(@class, "article-content")])')
        if len(content) == 0:
            failures += 1
            continue

        with open(f'extracted_contents/{recipe_name}.txt', 'w') as f:
            f.write(content)

        c.execute('INSERT INTO contents VALUES (?, ?)', (content, recipe[0]))
        conn.commit()

print(failures, 'failures')