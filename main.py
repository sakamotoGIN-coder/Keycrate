from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.routes import auth, ai, vault

app = FastAPI(title="KeyCrate")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Routes
app.include_router(auth.router)
app.include_router(ai.router)
app.include_router(vault.router)

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



#  uvicorn main:app --reload            





