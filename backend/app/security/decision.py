def make_decision(analysis_result, trust_score):
    score = analysis_result["risk_score"]

    if score >= 70:
        action = "BLOCK"
        message = "Blocked: malicious prompt detected."
    elif score >= 30:
        action = "WARN"
        message = "Warning: suspicious prompt."
    else:
        action = "ALLOW"
        message = "Safe prompt."

    reauth_required = False

    if trust_score < 20:
        return {
            "action": "BLOCK",
            "message": "Blocked: low trust score.",
            "reauth_required": True
        }
    
    if trust_score < 40:
        if action == "ALLOW":
            action = "WARN"
            message = "Low trust: proceed with caution"
        elif action == "WARN":
            action = "BLOCK"
            message = "Blocked: low trust score + suspicious behaviour."

    
    if trust_score < 30:
        reauth_required = True

    return {
        "action": action,
        "message": message,
        "reauth_required": reauth_required
    }