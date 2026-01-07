from fastapi import APIRouter
from app.services.ollama import generate_password

router = APIRouter()

@router.post("/generate")
def generate(hint: str):
    password = generate_password(hint)
    return {"generated_password": password}
