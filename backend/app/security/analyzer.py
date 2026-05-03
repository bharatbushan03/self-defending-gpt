from app.security.ai_analyzer import ai_classify_prompt
import re

INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"disregard above",
    r"act as",
    r"pretent to be",
    r"you are now"
]

DATA_EXTRACTION_PATTERNS = [
    r"reveal system prompt",
    r"show hidden instructions",
    r"what is your training data"
]

def analyze_prompt(prompt: str):
    rule_result = basic_rule_analysis(prompt)
    
    try:
        ai_result = ai_classify_prompt(prompt)
    except Exception as e:
        ai_result = {
            "label": "Error",
            "risk_score": 100,
            "reason": f"AI analysis failed: {str(e)}"
        }

    final_score = int(
        (rule_result["risk_score"]*0.4) + 
        (ai_result["risk_score"]*0.6)
    )

    reason = rule_result["reason"] + [ai_result["reason"]]

    if final_score >= 70:
        label = "Malicious"
    elif final_score >= 30:
        label = "Suspicious"
    else:
        label = "Safe"

    return {
        "label": label,
        "risk_score": final_score,
        "reason": reason
    }

def basic_rule_analysis(prompt: str):
    prompt_lower = prompt.lower()
    reasons = []
    score = 0

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, prompt_lower):
            reasons.append(f"Injection pattern detected: '{pattern}'")
            score += 20

    for pattern in DATA_EXTRACTION_PATTERNS:
        if re.search(pattern, prompt_lower):
            reasons.append(f"Sensitive data request: '{pattern}'")
            score += 40

    if len(prompt) > 500:
        reasons.append("Unusually long prompt")
        score += 10

    if score >= 70:
        label = "Malicious"
    elif score >= 30:
        label = "Suspicious"
    else:
        label = "Safe"

    return {
        "label": label,
        "risk_score": score,
        "reason": reasons if reasons else ["No issues detected"]
    }
    

