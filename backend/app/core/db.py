from pymongo import MongoClient

MONGO_URI = "mongodb+srv://bharatbushan03:mrBh%40r%40t12@cluster0.rwiyvjz.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)

db = client["self_defending_gpt"]

logs_collection = db["logs"]