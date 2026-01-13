from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import engine
from app import models
from app.routes import auth, ai, vault

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="KeyCrate")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(ai.router, prefix="/ai", tags=["AI"])
app.include_router(vault.router, prefix="/vault", tags=["Vault"])


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})




#  uvicorn main:app --reload            





