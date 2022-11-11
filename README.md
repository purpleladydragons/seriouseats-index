## What is this

Just a rough prototype / experiment for me to use some OpenAI access

The code here can scrape seriouseats.com and index the recipes into a search engine

## Setup
pip install the requirements

You need your own OpenAI key. For the calorie counting, you also need a key for Edamam

For scraping, I used selenium and you'll need geckodriver

You probably also need to create the subdirs yourself: 

```shell
mkdir embeddings;
mkdir extracted_contents;
mkdir scraped_recipes;
```

I finetuned a model for crawling the website to label URLs as recipes or not. You can probably just use some regex rules
if you want, but I didn't want to. I included finetuner.csv with prompt examples if you want to finetune a model

From there you can run the programs in the following order:

```shell
python crawler.py
python scraper.py
python extractor.py
python embedder.py
python app.py
```

If you want to play around with the calorie counting, you can use recipes.py