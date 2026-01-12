from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import requests

from app.database import get_db
from app.models import Vault
from app.dependencies import get_current_user
from app.security.crypto import encrypt_password

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/generate-and-save")
def generate_and_save(
    hint: str,
    platform: str,
    username: str,
    db: Session = Depends(get_db)
):
    user = get_current_user(username, db)

    prompt = f"Generate ONE strong password based on this hint: {hint}. Only output the password, 12 characters, including upper and lower case letters, numbers, and special characters."

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    password = response.json()["response"].strip()

    encrypted = encrypt_password(password)

    vault = Vault(
        platform=platform,
        password=encrypted,
        owner_id=user.id
    )

    db.add(vault)
    db.commit()

    return {"password": password}









