import os
import re

from dotenv import load_dotenv

from .memory import get_chat_history

try:
    from langchain_nvidia_ai_endpoints import ChatNVIDIA
except ModuleNotFoundError:
    ChatNVIDIA = None

load_dotenv()

_model = None

_GREETING_PATTERN = re.compile(r"^\s*(hi|hello|hey|yo|hola|hii+)\s*[!.?]*\s*$", re.IGNORECASE)


def _get_model():
    global _model

    if ChatNVIDIA is None:
        raise RuntimeError("langchain_nvidia_ai_endpoints is not installed.")

    if not os.getenv("NVIDIA_API_KEY"):
        raise RuntimeError("NVIDIA_API_KEY is not set.")

    if _model is None:
        _model = ChatNVIDIA(model="nvidia/nemotron-3-super-120b-a12b", temperature=0)

    return _model

def generate_response(user_id: str, prompt: str):
    # Keep simple greetings short and natural.
    if _GREETING_PATTERN.match(prompt):
        return "Hey! How can I help?"

    history = get_chat_history(user_id)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. Keep responses concise by default. "
                "For simple greetings, reply in one short sentence (max 12 words) "
                "without emojis. Give longer answers only when the user asks for detail."
            ),
        }
    ]

    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": prompt})

    try:
        response = _get_model().invoke(messages)
    except Exception:
        return "The assistant is temporarily unavailable. Please try again shortly."

    return response.content
