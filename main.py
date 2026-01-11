from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
import secrets
import string
from argon2 import PasswordHasher

app = FastAPI()
templates = Jinja2Templates(directory="templates")
ph = PasswordHasher()

# Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Generate password (REAL FUNCTION)
@app.get("/generate", response_class=PlainTextResponse)
async def generate_password():
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(16))

    # Hash password (stored/used internally)
    hashed = ph.hash(password)

    # For now we only return the password
    return password

# Health check (optional)
@app.get("/health")
async def health():
    return {"status": "ok"}



