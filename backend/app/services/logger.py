from datetime import datetime
from app.core.db import logs_collection

def log_event(prompt, analysis, decision):
    entry = {
        "prompt": prompt,
        "label": analysis["label"],
        "risk_score": analysis["risk_score"],
        "action": decision["action"],
        "timestamp": datetime.utcnow().isoformat()
    }

    logs_collection.insert_one(entry)

    return entry

def get_logs():
    logs = list(logs_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(100))
    return logs