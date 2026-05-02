from pymongo import MongoClient

MONGO_URI = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.8.2"

client = MongoClient(MONGO_URI)

db = client["self_defending_gpt"]

logs_collection = db["logs"]