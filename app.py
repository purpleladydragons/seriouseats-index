import pandas as pd
import numpy as np
from openai.embeddings_utils import get_embedding, cosine_similarity

df = pd.read_csv('embeddings/seriouseats.csv')
df['babbage_similarity'] = df.babbage_similarity.apply(eval).apply(np.array)
df['babbage_search'] = df.babbage_search.apply(eval).apply(np.array)

def search_recipes(df, query, n=3):
    embedding = get_embedding(query, engine='text-search-babbage-query-001')

    df['similarities'] = df.babbage_search.apply(lambda x: cosine_similarity(x, embedding))
    res = df.sort_values('similarities', ascending=False).head(n)
    return res

while True:
    query = input("Enter a query: ")

    resp = search_recipes(df, query)
    print(resp)

    urls = resp.url.tolist()

    for url in urls:
        print(url)