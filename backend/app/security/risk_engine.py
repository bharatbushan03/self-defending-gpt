from typing import Dict, List, TypedDict, Literal
import logging

from app.security.rule_analyzer import analyze_prompt as rule_based_analysis
from app.security.nemotron_analyzer import analyze_prompt_with_nemotron as nemotron_analysis

# Define the structure for the final hybrid analysis result
class HybridAnalysisResult(TypedDict):
    final_label: Literal["Safe", "Suspicious", "Malicious"]
    final_risk_score: float
    reasons: List[str]
    attack_type: str
    confidence: float
    component_scores: Dict[str, float]

# Placeholder for behavior and anomaly scoring.
# In a real implementation, these would come from user session analysis and statistical models.
def get_behavior_score(user_id: str = None) -> float:
    """
    Placeholder function for behavior scoring.
    Returns a score from 0-100. A higher score means higher risk.
    """
    # For now, returns a neutral score.
    return 0.0

def get_prompt_anomaly_score(prompt: str) -> float:
    """
    Placeholder function for prompt anomaly detection.
    Returns a score from 0-100 based on statistical deviation from normal prompts.
    """
    # For now, returns a neutral score.
    return 0.0


def calculate_hybrid_risk(prompt: str, user_id: str = None) -> HybridAnalysisResult:
    """
    Calculates a hybrid risk score by combining multiple analysis layers.

    Args:
        prompt: The user-provided prompt string.
        user_id: The ID of the user making the request (optional).

    Returns:
        A dictionary containing the final hybrid analysis result.
    """
    # 1. Get scores from individual analyzers
    rule_result = rule_based_analysis(prompt)
    ai_result = nemotron_analysis(prompt)
    
    # For now, behavior and anomaly scores are placeholders.
    behavior_score = get_behavior_score(user_id)
    # Anomaly score is not in the formula provided, but we'll get it for future use.
    anomaly_score = get_prompt_anomaly_score(prompt)

    rule_score = rule_result["risk_score"]
    ai_score = ai_result["risk_score"]

    # 2. Apply the weighted formula
    # final_score = (rule_score * 0.35) + (ai_score * 0.45) + (behavior_score * 0.20)
    # The prompt anomaly score is not in the user-provided formula, so it's omitted for now.
    weights = {
        "rule": 0.35,
        "ai": 0.45,
        "behavior": 0.20
    }
    
    final_risk_score = (rule_score * weights["rule"]) + \
                       (ai_score * weights["ai"]) + \
                       (behavior_score * weights["behavior"])
    
    final_risk_score = min(final_risk_score, 100.0) # Cap score at 100

    # 3. Determine the final label
    if final_risk_score >= 75:
        final_label = "Malicious"
    elif final_risk_score >= 30:
        final_label = "Suspicious"
    else:
        final_label = "Safe"

    # 4. Aggregate reasons and determine the primary attack type and confidence
    # We'll prioritize the AI's findings if it's confident, otherwise, fall back to rules.
    reasons = list(set(rule_result["reasons"] + ai_result["reasons"]))
    
    if ai_result["confidence"] > 0.6 and ai_result["attack_type"] != "none":
        attack_type = ai_result["attack_type"]
        confidence = ai_result["confidence"]
    elif rule_result["detected_categories"]:
        attack_type = ", ".join(rule_result["detected_categories"])
        confidence = 0.6 # Confidence for rule-based is generally moderate
    else:
        attack_type = "none"
        confidence = 1.0 - (final_risk_score / 100)


    return {
        "final_label": final_label,
        "final_risk_score": round(final_risk_score, 2),
        "reasons": reasons,
        "attack_type": attack_type,
        "confidence": round(confidence, 2),
        "component_scores": {
            "rule_score": rule_score,
            "ai_score": ai_score,
            "behavior_score": behavior_score,
            "anomaly_score": anomaly_score
        }
    }
