from pymongo import DESCENDING
from app.core.db import get_database
from datetime import datetime, timedelta

def get_summary_analytics():
    """
    Calculates summary statistics for the SOC dashboard.
    - Total requests by label (Safe, Suspicious, Malicious)
    - Average risk score across all requests
    """
    db = get_database()
    logs_collection = db["logs"]
    
    total_safe = logs_collection.count_documents({"label": "Safe"})
    total_suspicious = logs_collection.count_documents({"label": "Suspicious"})
    total_malicious = logs_collection.count_documents({"label": "Malicious"})
    
    pipeline = [
        {"$group": {"_id": None, "avg_risk_score": {"$avg": "$risk_score"}}}
    ]
    avg_risk_result = list(logs_collection.aggregate(pipeline))
    
    avg_risk_score = avg_risk_result[0]["avg_risk_score"] if avg_risk_result else 0
    
    return {
        "total_safe": total_safe,
        "total_suspicious": total_suspicious,
        "total_malicious": total_malicious,
        "average_risk_score": round(avg_risk_score, 2)
    }

def get_risk_distribution():
    """
    Calculates the distribution of requests by risk label.
    """
    db = get_database()
    logs_collection = db["logs"]
    
    pipeline = [
        {"$group": {"_id": "$label", "count": {"$sum": 1}}},
        {"$project": {"label": "$_id", "count": 1, "_id": 0}}
    ]
    distribution = list(logs_collection.aggregate(pipeline))
    return distribution

def get_attack_trends(days: int = 30):
    """
    Calculates the trend of attacks (Suspicious or Malicious) over the last N days.
    """
    db = get_database()
    logs_collection = db["logs"]
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    pipeline = [
        {"$match": {
            "timestamp": {"$gte": start_date},
            "label": {"$in": ["Suspicious", "Malicious"]}
        }},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}},
        {"$project": {"date": "$_id", "count": 1, "_id": 0}}
    ]
    trends = list(logs_collection.aggregate(pipeline))
    return trends

def get_top_risky_users(limit: int = 5):
    """
    Identifies the top N riskiest users based on their average risk score.
    """
    db = get_database()
    logs_collection = db["logs"]
    
    pipeline = [
        {"$group": {
            "_id": "$user_id",
            "average_risk_score": {"$avg": "$risk_score"},
            "blocked_count": {
                "$sum": {"$cond": [{"$eq": ["$action", "BLOCK"]}, 1, 0]}
            }
        }},
        {"$sort": {"average_risk_score": DESCENDING}},
        {"$limit": limit},
        {"$project": {
            "user_id": "$_id",
            "average_risk_score": {"$round": ["$average_risk_score", 2]},
            "blocked_count": 1,
            "_id": 0
        }}
    ]
    top_users = list(logs_collection.aggregate(pipeline))
    return top_users

def get_recent_attacks(limit: int = 10):
    """
    Retrieves the most recent N attacks that were blocked.
    """
    db = get_database()
    logs_collection = db["logs"]
    
    recent_attacks = logs_collection.find(
        {"action": "BLOCK"}
    ).sort("timestamp", DESCENDING).limit(limit)
    
    # Convert to list and handle ObjectId
    result = []
    for attack in recent_attacks:
        attack["_id"] = str(attack["_id"])
        result.append(attack)
        
    return result
