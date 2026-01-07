from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import VaultItem
from app.services.security import hash_password

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/save")
def save_password(
    user_id: int,
    platform: str,
    password: str,
    db: Session = Depends(get_db)
):
    item = VaultItem(
        user_id=user_id,
        platform=platform,
        password_hash=hash_password(password)
    )
    db.add(item)
    db.commit()
    return {"status": "Password saved securely"}

@router.get("/list")
def list_passwords(user_id: int, db: Session = Depends(get_db)):
    items = db.query(VaultItem).filter(VaultItem.user_id == user_id).all()
    return items
