from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from app.services.password_ai import generate_password_from_hint

router = APIRouter()

class HintRequest(BaseModel):
    hint: str

@router.post("/ai/generate", response_class=PlainTextResponse)
def generate(data: HintRequest):
    return generate_password_from_hint(data.hint)


