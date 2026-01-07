from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)

class VaultItem(Base):
    __tablename__ = "vault"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    platform = Column(String)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
