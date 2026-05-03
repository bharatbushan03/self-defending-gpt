from langchain_nvidia_ai_endpoints import ChatNVIDIA
from dotenv import load_dotenv
import json

load_dotenv()

client = ChatNVIDIA(model="nvidia/nemotron-3-super-120b-a12b", temperature = 0)

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

    response = client.invoke(messages)

    content = response.content

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "label": "Error",
            "risk_score": 100,
            "reason": f"Invalid JSON response: {content}"
        }
