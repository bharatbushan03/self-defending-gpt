def make_decision(analysis_result):
    score = analysis_result["risk_score"]

    if score >= 70:
        action = "BLOCK"
        message = "Request blocked due to malicious content."
    elif score >= 30:
        action = "WARN"
        message = "This prompt looks suspicious. Proceed with caution."
    else:
        action = "ALLOW"
        message = "Request is safe."

    return {
        "action": action,
        "message": message
    }

