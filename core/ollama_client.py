import requests
from config import OLLAMA_API_URL, OLLAMA_MODEL

def get_ai_response(prompt: str) -> str:
    try:
        response = requests.post(OLLAMA_API_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        })
        response.raise_for_status()
        data = response.json()
        return data.get("response", "[No response from model]")
    except Exception as e:
        return f"[Error: {e}]"

