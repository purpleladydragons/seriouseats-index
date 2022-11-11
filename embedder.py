import time
import sqlite3
import lxml.html
import pandas as pd
from transformers import GPT2TokenizerFast
from openai.embeddings_utils import get_embedding

tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

conn = sqlite3.connect('urls.db')
c = conn.cursor()

df = pd.read_sql_query('SELECT * FROM contents', conn)

df['n_tokens'] = df.content.apply(lambda x: len(tokenizer.encode(x)))
df = df[df.n_tokens<2000]

price = (df['n_tokens'].sum() / 1000) * .005 * 2 # times 2 b/c we're embeddingsimilarity and search

inp = input(f"Will cost ${price} - is that okay? y/n")

if inp != 'y':
    exit()

print('embedding')
df['babbage_similarity'] = df.content.apply(lambda x: get_embedding(x, engine='text-similarity-babbage-001'))
df['babbage_search'] = df.content.apply(lambda x: get_embedding(x, engine='text-search-babbage-doc-001'))
df.to_csv('embeddings/seriouseats.csv')
