from pymongo.database import Database
from pymongo import DESCENDING
from typing import List, Dict

from app.core.db import get_database
from app.models.log import SecurityLog

def create_security_log(log_data: SecurityLog) -> Dict:
    """
    Inserts a new security log into the database.

    Args:
        log_data: A SecurityLog object containing all the log details.

    Returns:
        The inserted log document as a dictionary.
    """
    db = get_database()
    logs_collection = db["logs"]
    
    inserted_log = logs_collection.insert_one(log_data.dict())
    created_log = logs_collection.find_one({"_id": inserted_log.inserted_id})
    return created_log

def get_security_logs(limit: int = 100) -> List[Dict]:
    """
    Retrieves the latest security logs from the database.

    Args:
        limit: The maximum number of logs to return.

    Returns:
        A list of log documents.
    """
    db = get_database()
    logs_collection = db["logs"]
    
    # Sort by timestamp in descending order to get the latest logs first
    logs = logs_collection.find().sort("timestamp", DESCENDING).limit(limit)
    
    # Hide the internal _id field
    return [{**log, "_id": str(log["_id"])} for log in logs]
