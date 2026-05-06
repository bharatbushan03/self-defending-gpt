import os
from functools import lru_cache

from dotenv import load_dotenv

try:
    from pymongo import MongoClient
except ModuleNotFoundError:
    MongoClient = None

load_dotenv()


def _get_mongo_uri() -> str:
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise RuntimeError(
            "MONGO_URI is not set. Configure it in the environment or the repo .env file."
        )
    return mongo_uri


@lru_cache(maxsize=1)
def _get_database():
    if MongoClient is None:
        raise RuntimeError("pymongo is not installed.")

    client = MongoClient(_get_mongo_uri(), serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    return client["self_defending_gpt"]


class CollectionProxy:
    def __init__(self, name: str):
        self.name = name

    def _collection(self):
        return _get_database()[self.name]

    def __getattr__(self, attr):
        return getattr(self._collection(), attr)


class DatabaseProxy:
    def __getitem__(self, name: str):
        return CollectionProxy(name)


db = DatabaseProxy()
logs_collection = CollectionProxy("logs")
