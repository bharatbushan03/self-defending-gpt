import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
	raise ValueError("MONGO_URI is not set. Please configure it in backend/.env")

client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
client.admin.command("ping")

db = client["self_defending_gpt"]
logs_collection = db["logs"]