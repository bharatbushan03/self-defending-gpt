from collections import Counter
from datetime import datetime, timedelta

from ..core.db import logs_collection

LABEL_MAP = {
    "safe": "Safe",
    "suspicious": "Suspicious",
    "malicious": "Malicious"
}


def normalize_label(value):
    if not isinstance(value, str):
        return None
    return LABEL_MAP.get(value.strip().lower())


def get_risk_distribution():
    logs = list(logs_collection.find())

    labels = [normalize_label(log.get("label")) for log in logs]
    count = Counter(label for label in labels if label)

    return {
        "Safe": count.get("Safe", 0),
        "Suspicious": count.get("Suspicious", 0),
        "Malicious": count.get("Malicious", 0)
    }


def get_attack_trends():
    logs = list(logs_collection.find())

    trend = {}

    for log in logs:
        timestamp = log.get("timestamp")
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp)
            except ValueError:
                if timestamp.endswith("Z"):
                    try:
                        timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    except ValueError:
                        continue
                else:
                    continue

        if not isinstance(timestamp, datetime):
            continue

        date = timestamp.strftime("%Y-%m-%d")

        if date not in trend:
            trend[date] = {"Safe": 0, "Suspicious": 0, "Malicious": 0}

        label = normalize_label(log.get("label"))
        if not label:
            continue

        trend[date][label] += 1

    return trend


def get_top_risky_users():
    logs = list(logs_collection.find())

    user_scores = {}

    for log in logs:
        user = log.get("user_id", "unknown")
        score = log.get("risk_score", 0)

        user_scores[user] = user_scores.get(user, 0) + score

    # Sort descending
    sorted_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)

    return sorted_users[:5]
