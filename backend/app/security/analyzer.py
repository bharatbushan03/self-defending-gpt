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
    

