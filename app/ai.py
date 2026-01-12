# app/ai.py

import subprocess


def generate_password(hint: str) -> str:
    prompt = f"""
Generate a strong, secure password based on this hint:
{hint}

Rules:
- Max 12 characters
- Include uppercase, lowercase, numbers, symbols
- Return ONLY the password, nothing else
"""

    result = subprocess.run(
        ["ollama", "run", "llama3"],
        input=prompt,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError("Ollama failed to generate password")

    return result.stdout.strip()
