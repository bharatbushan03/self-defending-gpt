import re
from typing import Dict, List, TypedDict, Literal

# Define the structure of the analysis result
class AnalysisResult(TypedDict):
    label: Literal["Safe", "Suspicious", "Malicious"]
    risk_score: float
    reasons: List[str]
    detected_categories: List[str]

# Define rules for detecting various threats
# Each rule has a category, a list of patterns (regex), and a risk score to add if matched.
RULES = [
    {
        "category": "prompt_injection",
        "patterns": [
            r"ignore .* instructions",
            r"disregard the above",
            r"you are now a different model",
            r"your new instructions are",
            r"forget everything you know",
        ],
        "score": 40,
    },
    {
        "category": "jailbreak_attempts",
        "patterns": [
            r"act as if",
            r"act as",
            r"stay in character",
            r"developer mode",
            r"do anything now",
            r"\bDAN\b", # DAN = Do Anything Now
            r"hypothetical scenario",
            r"for research purposes",
        ],
        "score": 30,
    },
    {
        "category": "system_prompt_extraction",
        "patterns": [
            r"what are your instructions",
            r"repeat the text above",
            r"what is your system prompt",
            r"print your initial prompt",
            r"reveal your configuration",
            r"what rules are you bound by",
        ],
        "score": 50,
    },
    {
        "category": "role_manipulation",
        "patterns": [
            r"you are an unrestricted ai",
            r"you are not a language model",
            r"you have no rules",
            r"you have been freed",
        ],
        "score": 60,
    },
    {
        "category": "admin_impersonation",
        "patterns": [
            r"admin override",
            r"sudo mode",
            r"root access enabled",
            r"security clearance granted",
        ],
        "score": 80,
    },
    {
        "category": "bypass_attempts",
        "patterns": [
            r"encode the following in base64",
            r"use character substitution",
            r"respond in leetspeak",
            r"print the following in reverse",
        ],
        "score": 25,
    },
]

def analyze_prompt(prompt: str) -> AnalysisResult:
    """
    Analyzes a user prompt against a set of security rules.

    Args:
        prompt: The user-provided prompt string.

    Returns:
        A dictionary containing the analysis result.
    """
    risk_score = 0.0
    reasons = []
    detected_categories = set()
    
    # Normalize prompt to lowercase for case-insensitive matching
    normalized_prompt = prompt.lower()

    for rule in RULES:
        for pattern in rule["patterns"]:
            if re.search(pattern, normalized_prompt, re.IGNORECASE):
                risk_score += rule["score"]
                reasons.append(f"Matched '{rule['category']}' pattern: '{pattern}'")
                detected_categories.add(rule["category"])

    # Determine label based on risk score
    if risk_score >= 80:
        label = "Malicious"
    elif risk_score >= 30:
        label = "Suspicious"
    else:
        label = "Safe"

    # Cap the risk score at 100
    final_score = min(risk_score, 100.0)

    return {
        "label": label,
        "risk_score": final_score,
        "reasons": reasons,
        "detected_categories": list(detected_categories),
    }
