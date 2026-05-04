from datetime import datetime
from app.core.db import db

chat_collection = db["chat_history"]

def get_chat_history(user_id: str, limit = 10):
    chats = list(
        chat_collection.find({"user_id": user_id}, {"_id": 0}).sort("timestamp", 1).limit(limit)
    )
    return chats

def save_message(user_id: str, role: str, content: str):
    chat_collection.insert_one({
        "user_id": user_id,
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow()
    })