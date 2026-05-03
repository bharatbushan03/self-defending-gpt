from langchain_nvidia_ai_endpoints import ChatNVIDIA
from app.services.memory import get_chat_history
from dotenv import load_dotenv
import json

load_dotenv()

model = ChatNVIDIA(model="nvidia/nemotron-3-super-120b-a12b", temperature = 0)

def generate_response(user_id: str, prompt: str):
    history = get_chat_history(user_id)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": prompt})

    response = model.invoke(messages)

    return response.content