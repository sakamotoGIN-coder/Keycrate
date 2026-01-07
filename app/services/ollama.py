import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_password(hint: str) -> str:
    prompt = f"""
Generate a strong easy-to-remember password (10-12 characters).
Use uppercase, lowercase, numbers, and symbols.
Provide just answer only.

Hint: {hint}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"].strip()
