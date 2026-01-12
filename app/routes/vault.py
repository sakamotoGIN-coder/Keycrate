from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Vault
from app.dependencies import get_current_user

router = APIRouter(prefix="/vault", tags=["Vault"])

@router.get("/")
def get_vault(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return db.query(Vault).filter(Vault.owner_id == user.id).all()



