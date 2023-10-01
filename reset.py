# Redis Fashion VSS Demo: Reset for Presentation Script
from dotenv import load_dotenv
import json
import redis
import os
import git

# Load environment variables / secrets from .env file.
load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
DEMO_PRODUCTS = json.loads(os.environ.get('DEMO_PRODUCTS'))
REDIS_INDEX = os.getenv("REDIS_INDEX")

keys = ["fashion:" + str(id) for id in DEMO_PRODUCTS]

# Connect to Redis
print(f"Connecting to Redis.")
client = redis.from_url(REDIS_URL)

try:
    client.ft(REDIS_INDEX).dropindex(delete_documents = False)
except:
    # Dropping an index that doesn't exist throws an exception
    # but isn't an error in this case - we just want to start
    # from a known point.
    pass

print(f"Dropped index {REDIS_INDEX}")

pipeline = client.pipeline()

for key in keys:
    pipeline.json().delete(key, '$.description_embeddings')
    pipeline.json().delete(key, '$.image_embeddings')

pipeline.execute()
print('Deleted Sentence and Image Embeddings for Demo Set!')

repo = git.Repo('.')
repo.git.checkout('HEAD', 'presentation.ipynb')
print('Reset presentation to base state')
