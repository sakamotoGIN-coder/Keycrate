from cryptography.fernet import Fernet
import os

KEY = os.getenv("VAULT_SECRET_KEY")

if not KEY:
    raise RuntimeError("VAULT_SECRET_KEY environment variable not set")

fernet = Fernet(KEY.encode())


def encrypt_password(plain: str) -> str:
    return fernet.encrypt(plain.encode()).decode()


def decrypt_password(cipher: str) -> str:
    return fernet.decrypt(cipher.encode()).decode()

