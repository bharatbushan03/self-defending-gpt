from pymongo.database import Database
from app.core.db import get_database
from app.models.user import UserModel
from typing import Dict, Literal

# Define score adjustments
SCORE_ADJUSTMENTS = {
    "Safe": 2,
    "Suspicious": -5,
    "Malicious": -15,
}

def get_or_create_user(user_id: str) -> Dict:
    """
    Retrieves a user from the database or creates a new one if they don't exist.

    Args:
        user_id: The ID of the user.

    Returns:
        The user document as a dictionary.
    """
    db = get_database()
    users_collection = db["users"]
    
    user = users_collection.find_one({"user_id": user_id})
    
    if not user:
        new_user = UserModel(user_id=user_id)
        users_collection.insert_one(new_user.dict())
        return new_user.dict()
        
    return user

def update_trust_score(user_id: str, analysis_label: Literal["Safe", "Suspicious", "Malicious"]) -> Dict:
    """
    Updates a user's trust score based on the analysis of their prompt.

    Args:
        user_id: The ID of the user.
        analysis_label: The security label from the prompt analysis.

    Returns:
        The updated user document.
    """
    db = get_database()
    users_collection = db["users"]
    
    user_data = get_or_create_user(user_id)
    current_score = user_data.get("trust_score", 50.0)
    
    adjustment = SCORE_ADJUSTMENTS.get(analysis_label, 0)
    new_score = current_score + adjustment
    
    # Clamp the score between 0 and 100
    clamped_score = max(0.0, min(100.0, new_score))
    
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"trust_score": clamped_score}},
        upsert=True
    )
    
    updated_user = users_collection.find_one({"user_id": user_id})
    return updated_user
