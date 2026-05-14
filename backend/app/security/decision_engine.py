from typing import Dict
from app.models.decision import Decision

def make_decision(risk_score: float, trust_score: float) -> Decision:
    """
    Makes a final security decision based on risk and trust scores.

    Args:
        risk_score: The final risk score from the hybrid engine (0-100).
        trust_score: The user's current trust score (0-100).

    Returns:
        A Decision object containing the action to take.
    """
    action: str = "ALLOW"
    message: str = "Request is considered safe."
    reauth_required: bool = False

    # Rule 1: Block based on extremely low trust score
    if trust_score < 20:
        action = "BLOCK"
        message = f"Action blocked due to extremely low user trust score ({trust_score:.2f})."
        reauth_required = True
        return Decision(action=action, message=message, reauth_required=reauth_required)

    # Rule 2: Block based on high risk score
    if risk_score >= 70:
        action = "BLOCK"
        message = f"Action blocked due to high prompt risk score ({risk_score:.2f})."
    
    # Rule 3: Warn based on moderate risk score
    elif risk_score >= 30:
        action = "WARN"
        message = f"Suspicious prompt detected. Risk score: {risk_score:.2f}."
        
    # Rule 4: Require re-authentication for low trust score
    if trust_score < 30:
        reauth_required = True
        # Append to the message if it's not already a block message
        if action != "BLOCK":
            message += f" User trust score is low ({trust_score:.2f}), re-authentication is recommended."

    return Decision(action=action, message=message, reauth_required=reauth_required)
