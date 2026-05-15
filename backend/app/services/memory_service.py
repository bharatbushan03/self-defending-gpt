from typing import List, Dict
from pymongo import DESCENDING

from app.core.db import get_database
from app.models.history import HistoryMessage

def store_message(user_id: str, role: str, content: str):
    """
    Stores a message in the user's chat history.

    Args:
        user_id: The ID of the user.
        role: The role of the message author ('user' or 'assistant').
        content: The content of the message.
    """
    db = get_database()
    chat_history_collection = db["chat_history"]
    
    message = HistoryMessage(user_id=user_id, role=role, content=content)
    chat_history_collection.insert_one(message.dict())

def get_conversation_history(user_id: str, limit: int = 10) -> List[Dict]:
    """
    Retrieves the most recent conversation history for a user.

    Args:
        user_id: The ID of the user.
        limit: The maximum number of messages to retrieve.

    Returns:
        A list of message dictionaries, formatted for the Nemotron API.
    """
    db = get_database()
    chat_history_collection = db["chat_history"]
    
    # Find messages for the user, sort by timestamp descending, and limit the results
    history_cursor = chat_history_collection.find(
        {"user_id": user_id}
    ).sort("timestamp", DESCENDING).limit(limit)
    
    # The API expects messages in chronological order, so we reverse the list
    history = list(history_cursor)
    history.reverse()
    
    # Format for the API (role and content)
    formatted_history = [
        {"role": msg["role"], "content": msg["content"]} for msg in history
    ]
    
    return formatted_history
