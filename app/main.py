from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import engine
from app import models
from app.routes import auth, ai, vault

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="KeyCrate")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth.router)   # auth already has prefix="/auth"
app.include_router(ai.router)     # ai already has prefix="/ai"
app.include_router(vault.router)  # vault already has prefix="/vault"

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/vault-ui")
def vault_ui(request: Request):
    return templates.TemplateResponse("vault.html", {"request": request})







#  uvicorn main:app --reload            





