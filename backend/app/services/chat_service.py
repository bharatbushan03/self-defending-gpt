import requests
import logging

from app.core.config import settings

# A simple system prompt for the chatbot persona
CHATBOT_SYSTEM_PROMPT = "You are a helpful and friendly assistant."

def get_chatbot_response(prompt: str) -> str:
    """
    Gets a response from the NVIDIA Nemotron model to a user's prompt.

    Args:
        prompt: The user's prompt.

    Returns:
        The chatbot's response as a string, or an error message if the API call fails.
    """
    if not settings.NEMOTRON_API_KEY or not settings.NEMOTRON_BASE_URL:
        logging.error("NEMOTRON_API_KEY or NEMOTRON_BASE_URL not configured for chatbot.")
        return "I'm sorry, but I'm unable to respond right now due to a configuration issue."

    headers = {
        "Authorization": f"Bearer {settings.NEMOTRON_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "messages": [
            {"role": "system", "content": CHATBOT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "top_p": 1.0,
        "max_tokens": 1024,
        "stream": False
    }

    try:
        response = requests.post(
            settings.NEMOTRON_BASE_URL,
            headers=headers,
            json=payload,
            timeout=25
        )
        response.raise_for_status()
        
        model_response = response.json()["choices"][0]["message"]["content"]
        return model_response

    except requests.exceptions.Timeout:
        logging.error("Request to Nemotron chatbot API timed out.")
        return "I'm sorry, I'm having trouble connecting. Please try again in a moment."
    except requests.exceptions.RequestException as e:
        logging.error(f"Request to Nemotron chatbot API failed: {e}")
        return "I'm sorry, there was an error with my connection. Please try again later."
    except (KeyError, IndexError) as e:
        logging.error(f"Failed to parse response from Nemotron chatbot API: {e}")
        return "I'm sorry, I received an unexpected response. Please try again."
