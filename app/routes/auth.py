from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import SessionLocal
from app.models import User
from app.password_ai import hash_password, verify_password
from app.services.security import create_token

router = APIRouter(prefix="/auth", tags=["Auth"])

class AuthRequest(BaseModel):
    username: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(data: AuthRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        username=data.username,
        password_hash=hash_password(data.password)
    )
    db.add(user)
    db.commit()

    return {"message": "User registered successfully"}

@router.post("/login")
def login(data: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"sub": user.username})
    return {"access_token": token}


