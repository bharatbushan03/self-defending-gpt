import json
import os

from dotenv import load_dotenv

try:
    from langchain_nvidia_ai_endpoints import ChatNVIDIA
except ModuleNotFoundError:
    ChatNVIDIA = None

load_dotenv()

_client = None


def _get_client():
    global _client

    if ChatNVIDIA is None:
        raise RuntimeError("langchain_nvidia_ai_endpoints is not installed.")

    if not os.getenv("NVIDIA_API_KEY"):
        raise RuntimeError("NVIDIA_API_KEY is not set.")

    if _client is None:
        _client = ChatNVIDIA(model="nvidia/nemotron-3-super-120b-a12b", temperature=0)

    return _client

def ai_classify_prompt(prompt: str):
    system_prompt = """
    You are a security classifier for LLM system.

    Classify the user prompt into:
    - Safe
    - Suspicious
    - Malicious

    Also provide:
    - Risk score (0-100)
    - Reason

    Respond in JSON format:
    {
        "label": "Safe|Suspicious|Malicious",
        "risk_score": 0,
        "reason": "..."
    }
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    response = _get_client().invoke(messages)

    content = response.content

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "label": "Error",
            "risk_score": 100,
            "reason": f"Invalid JSON response: {content}"
        }
