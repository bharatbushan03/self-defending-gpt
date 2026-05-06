from ..core.db import db

users_collection = db["users"]

def get_or_create_user(user_id: str):
    user = users_collection.find_one({"user_id": user_id})

    if not user:
        user = {
            "user_id": user_id,
            "trust_score": 50
        }
        users_collection.insert_one(user)

    return user

def update_trust(user_id: str, label: str):
    user = get_or_create_user(user_id)
    trust = user["trust_score"]

    if label == "Safe":
        trust += 2
    elif label == "Suspicious":
        trust -= 5
    elif label == "Malicious":
        trust -= 15

    trust = max(0, min(100, trust))

    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"trust_score": trust}}
    )

    return trust
