from langchain_nvidia_ai_endpoints import ChatNVIDIA
from app.services.memory import get_chat_history
from dotenv import load_dotenv
import re

load_dotenv()

model = ChatNVIDIA(model="nvidia/nemotron-3-super-120b-a12b", temperature = 0)

_GREETING_PATTERN = re.compile(r"^\s*(hi|hello|hey|yo|hola|hii+)\s*[!.?]*\s*$", re.IGNORECASE)

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

    response = model.invoke(messages)

    return response.content