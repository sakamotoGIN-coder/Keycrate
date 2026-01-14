from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    vault_entries = relationship("VaultEntry", back_populates="owner", cascade="all, delete-orphan")


class VaultEntry(Base):
    __tablename__ = "vault_entries"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, nullable=False)
    password_encrypted = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="vault_entries")






