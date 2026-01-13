from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests

router = APIRouter(prefix="/ai", tags=["AI"])

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

class GenerateRequest(BaseModel):
    hint: str

@router.post("/generate")
def generate_password(req: GenerateRequest):
    prompt = f"""
Generate ONE secure password only.
No explanation.
Hint: {req.hint}
"""

    r = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )

    if r.status_code != 200:
        raise HTTPException(status_code=500, detail="Ollama failed")

    data = r.json()
    password = data.get("response", "").strip()

    if not password:
        raise HTTPException(status_code=500, detail="Empty AI response")

    return {"generated_password": password}










