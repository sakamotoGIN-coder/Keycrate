import os
from cryptography.fernet import Fernet

def _get_fernet() -> Fernet:
    key = os.getenv("VAULT_KEY")
    if not key:
        raise RuntimeError("VAULT_KEY is not set. Set it in your environment.")
    return Fernet(key.encode() if isinstance(key, str) else key)

def encrypt_text(plain: str) -> str:
    f = _get_fernet()
    return f.encrypt(plain.encode()).decode()

def decrypt_text(token: str) -> str:
    f = _get_fernet()
    return f.decrypt(token.encode()).decode()
