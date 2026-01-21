from functools import lru_cache
from pymongo import MongoClient
from app.config import MONGODB_URI, MONGODB_DATABASE


@lru_cache(maxsize=1)
def get_db():
    client = MongoClient(MONGODB_URI)
    return client[MONGODB_DATABASE]
