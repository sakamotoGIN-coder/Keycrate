from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import SessionLocal
from app.models import VaultEntry
from app.dependencies import get_current_user
from app.services.vault_crypto import encrypt_text, decrypt_text

router = APIRouter(prefix="/vault", tags=["Vault"])


class SaveVaultRequest(BaseModel):
    platform: str
    password: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/save")
def save_to_vault(
    data: SaveVaultRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    platform = data.platform.strip()
    password = data.password.strip()

    if not platform:
        raise HTTPException(status_code=400, detail="Platform is required")
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")

    encrypted = encrypt_text(password)

    entry = VaultEntry(
        platform=platform,
        password_encrypted=encrypted,
        owner_id=user.id
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    return {"message": "Saved to vault", "id": entry.id}


@router.get("/list")
def list_vault(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    entries = (
        db.query(VaultEntry)
        .filter(VaultEntry.owner_id == user.id)
        .order_by(VaultEntry.created_at.desc())
        .all()
    )

    return [
        {
            "id": e.id,
            "platform": e.platform,
            "created_at": e.created_at.isoformat(),
        }
        for e in entries
    ]


@router.get("/{vault_id}/reveal")
def reveal_password(
    vault_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    entry = (
        db.query(VaultEntry)
        .filter(
            VaultEntry.id == vault_id,
            VaultEntry.owner_id == user.id
        )
        .first()
    )

    if not entry:
        raise HTTPException(status_code=404, detail="Vault entry not found")

    plain = decrypt_text(entry.password_encrypted)
    return {"password": plain}


@router.delete("/{vault_id}")
def delete_vault_entry(
    vault_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    entry = (
        db.query(VaultEntry)
        .filter(
            VaultEntry.id == vault_id,
            VaultEntry.owner_id == user.id
        )
        .first()
    )

    if not entry:
        raise HTTPException(status_code=404, detail="Vault entry not found")

    db.delete(entry)
    db.commit()
    return {"message": "Deleted successfully"}






