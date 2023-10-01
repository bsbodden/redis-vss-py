# Redis Fashion VSS Demo: Data Loader Script
from dotenv import load_dotenv
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.field import TextField, TagField, NumericField, GeoField
from redis.commands.search.query import Query
from redis.commands.search.aggregation import AggregateRequest
from redis.commands.search.reducers import count, count_distinct

from sentence_transformers import SentenceTransformer, util
import numpy as np

import json
import io
import os
import redis
import pandas as pd

# Load environment variables / secrets from .env file.
load_dotenv()

# Connect to Redis and reset to a known state.
print(f"Connecting to Redis.")

REDIS_URL = os.getenv("REDIS_URL")
REDIS_INDEX = os.getenv("REDIS_INDEX")
DATASET_BASE = os.getenv("DATASET_BASE")
KEY_PREFIX = os.getenv("KEY_PREFIX")
DEMO_PRODUCTS = json.loads(os.environ.get('DEMO_PRODUCTS'))
EXIT_CODE_ERROR = 1

client = redis.from_url(REDIS_URL)

try:
    client.ft(REDIS_INDEX).dropindex(delete_documents = False)
except:
    # Dropping an index that doesn't exist throws an exception
    # but isn't an error in this case - we just want to start
    # from a known point.
    pass


print(f"Loading fashion data set.")
records_loaded = 0

# Load the CSV file into a pandas DataFrame
# CSV Fields:
# id,gender,masterCategory,subCategory,articleType,baseColour,season,year,usage,productDisplayName
df = pd.read_csv(f'{DATASET_BASE}/styles.csv', on_bad_lines='skip')
df.dropna(inplace=True)
df["year"] = df["year"].astype(int)

# Convert the DataFrame to a JSON string
json = df.to_json(orient='records')

# Convert the DataFrame to a list of JSON objects
records = df.to_dict(orient='records')

try:

    # Use a pipeline to load all the bike documents into Redis.
    pipeline = client.pipeline(transaction = False)

    # Loop over each JSON object
    for record in records:
        key = f"{KEY_PREFIX}:{record['id']}"

        record['name'] = str(record['productDisplayName'])
        record['usage'] = str(record['usage'])
        record['season'] = str(record['season'])
        record['color'] = str(record['baseColour'])

        if not pd.isna(record['year']):
            record['year'] = int(record['year'])
        else:
            record['year'] = -1

        record['type'] = str(record['articleType'])
        record['category'] = str(record['masterCategory'])
        # concatenate to get most semantic juice from the text data
        record['description'] = f"{record['productDisplayName']} #{record['masterCategory']} #{record['subCategory']} #{record['articleType']} #{record['baseColour']} #{record['season']} #{record['usage']}"
        record['image_url'] = f"{DATASET_BASE}/images/{record['id']}.jpg"

        del record['productDisplayName']
        del record['baseColour']
        del record['articleType']
        del record['masterCategory']

        pipeline.json().set(key, "$", record)
        records_loaded += 1
        print(f"{key} - {record['name']}")

    pipeline.execute()
except Exception as e:
    print("Failed to load fashion data file:")
    print(e)
    os._exit(EXIT_CODE_ERROR)

print(f"Loaded {records_loaded} records into Redis.")

# Generate Text Embeddings

text_embedder = SentenceTransformer('msmarco-distilbert-base-v4')

keys = sorted(client.keys('fashion:*'))
# keys to vectorize - skip the ones we are doing live in the session
keys = [key for key in keys if not any(key.endswith(str(id)) for id in DEMO_PRODUCTS)]

descriptions = client.json().mget(keys, '$.description')
descriptions = [item for sublist in descriptions for item in sublist]
text_embeddings = text_embedder.encode(descriptions).astype(np.float32).tolist()

pipeline = client.pipeline()

for key, embedding in zip(keys, text_embeddings):
    pipeline.json().set(key, '$.description_embeddings', embedding)

pipeline.execute()
print('Vector Text Embeddings Saved!')

# Generate Image Embeddings
from PIL import Image

image_embedder = SentenceTransformer('clip-ViT-B-32')
image_urls = client.json().mget(keys, '$.image_url')

image_embeddings = []
embedding_keys = []  # To store the keys corresponding to the embeddings

def save_embeddings_to_redis(embedding_keys, image_embeddings):
    """Utility function to save embeddings to Redis."""
    pipeline = client.pipeline()
    for key, embedding in zip(embedding_keys, image_embeddings):
        pipeline.json().set(key, '$.image_embeddings', embedding)
    pipeline.execute()

for filepath, key in zip(image_urls, keys):  # Also loop over keys here
    try:
        image = Image.open(filepath[0]).convert('RGB')
        image = image.resize((224, 224))
        image_embeddings.append(image_embedder.encode(image).astype(np.float32).tolist())
        embedding_keys.append(key)

        # If we have 100 embeddings, save them and clear the lists
        if len(image_embeddings) == 100:
            save_embeddings_to_redis(embedding_keys, image_embeddings)
            image_embeddings = []
            embedding_keys = []

    except Exception as e:
        print(f"Error processing {filepath}: {e}")

# After the loop ends, there might be some embeddings left that are fewer than 100.
# Save those as well.
if image_embeddings:
    save_embeddings_to_redis(embedding_keys, image_embeddings)

print('Vector Image Embeddings Saved!')

client.quit()