from datetime import datetime
from ..core.db import logs_collection

def log_event(user_id, prompt, analysis, decision):
    entry = {
        "user_id": user_id,
        "prompt": prompt,
        "label": analysis["label"],
        "risk_score": analysis["risk_score"],
        "action": decision["action"],
        "timestamp": datetime.utcnow()
    }

    logs_collection.insert_one(entry)

    return entry

def get_logs():
    logs = list(logs_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(100))
    return logs
