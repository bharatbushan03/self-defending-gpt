from typing import List, Dict
from pymongo import DESCENDING
from app.core.db import get_database
from app.models.log import SecurityLog

def log_security_event(
    user_id: str,
    prompt: str,
    analysis: Dict,
    decision: Dict,
    user_trust: Dict
):
    """
    Logs a complete security event to the database.

    Args:
        user_id: The ID of the user.
        prompt: The user's prompt.
        analysis: The result from the hybrid risk engine.
        decision: The final decision from the decision engine.
        user_trust: The user's trust score information.
    """
    db = get_database()
    logs_collection = db["logs"]
    
    log_entry = SecurityLog(
        user_id=user_id,
        prompt=prompt,
        label=analysis.get("final_label"),
        risk_score=analysis.get("final_risk_score"),
        action=decision.get("action"),
        reauth_required=decision.get("reauth_required"),
        reasons=analysis.get("reasons", []),
        attack_type=analysis.get("attack_type"),
        trust_score=user_trust.get("trust_score")
    )
    
    logs_collection.insert_one(log_entry.dict())

def get_logs(limit: int = 100) -> List[Dict]:
    """
    Retrieves the latest security logs from the database.

    Args:
        limit: The maximum number of logs to return.

    Returns:
        A list of log documents.
    """
    db = get_database()
    logs_collection = db["logs"]
    
    # Find logs, sort by timestamp descending, and limit the result.
    # The projection `{"_id": 0}` excludes the MongoDB _id field.
    logs = logs_collection.find({}, {"_id": 0}).sort("timestamp", DESCENDING).limit(limit)
    
    return list(logs)
