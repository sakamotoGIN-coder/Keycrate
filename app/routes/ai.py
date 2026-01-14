import os
import re
import secrets
import string
import requests

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.dependencies import get_current_user

router = APIRouter(prefix="/ai", tags=["AI"])

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

# Password policy (tweak if needed)
MIN_LEN = 12
MAX_LEN = 18

class Prompt(BaseModel):
    hint: str

def _clean_model_output(text: str) -> str:
    """Extract the first plausible password token from model output."""
    if not text:
        return ""
    text = text.strip()

    # Sometimes models wrap in quotes or code
    text = text.strip("`").strip().strip('"').strip("'")

    # If multi-line, take first non-empty
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if lines:
        text = lines[0]

    # If the model returns extra words, try to pick first token with symbols
    # e.g. "Password: Star#9A..." -> extract after colon
    if ":" in text:
        parts = [p.strip() for p in text.split(":") if p.strip()]
        text = parts[-1] if parts else text

    # Remove surrounding spaces again
    return text.strip()

def _meets_policy(pw: str) -> bool:
    if not pw:
        return False
    if len(pw) < MIN_LEN or len(pw) > 64:
        return False

    has_lower = any(c.islower() for c in pw)
    has_upper = any(c.isupper() for c in pw)
    has_digit = any(c.isdigit() for c in pw)
    has_symbol = any(c in "!@#$%^&*()-_=+[]{};:,.?/" for c in pw)

    # require at least 3 categories
    categories = sum([has_lower, has_upper, has_digit, has_symbol])
    return categories >= 3

def _fallback_from_hint(hint: str) -> str:
    """
    Deterministic-ish but still secure: uses hint + random tail.
    This keeps it "recognizable" without being guessable.
    """
    base = re.sub(r"[^a-zA-Z0-9]", "", hint.strip())
    base = base[:6] if base else "Key"

    # Make it a bit structured and readable
    base = base.capitalize()

    symbols = "!@#$%^&*"
    tail = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(6))
    sym = secrets.choice(symbols)
    num = secrets.randbelow(90) + 10  # 2 digits

    pw = f"{base}{sym}{num}{tail}"
    # ensure length bounds
    if len(pw) < MIN_LEN:
        pw += "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(MIN_LEN - len(pw)))
    return pw[:MAX_LEN]

def _ask_ollama_for_password(hint: str) -> str:
    prompt = f"""
Generate ONE strong password based on this user hint: "{hint}"

Rules:
- Output ONLY the password, nothing else (no labels, no quotes).
- Length must be between {MIN_LEN} and {MAX_LEN} characters.
- Must include at least 3 of these groups: lowercase, uppercase, digits, symbols.
- Do NOT use spaces.
- Do NOT output very short passwords.
- Make it loosely memorable / related to the hint, but still secure.

Return exactly one line.
""".strip()

    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 40
                }
            },
            timeout=60
        )
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Ollama connection error: {e}")

    if not r.ok:
        raise HTTPException(status_code=502, detail=f"Ollama error: {r.text}")

    data = r.json()
    # Ollama typically returns {"response": "..."} for /api/generate
    raw = data.get("response", "")
    return _clean_model_output(raw)

@router.post("/generate")
def generate_password(data: Prompt, user=Depends(get_current_user)):
    hint = (data.hint or "").strip()
    if len(hint) < 2:
        raise HTTPException(status_code=400, detail="Hint is too short.")

    pw = _ask_ollama_for_password(hint)

    # If model output is bad, fallback
    if not _meets_policy(pw):
        pw = _fallback_from_hint(hint)

    return {"password": pw}













