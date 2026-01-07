from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from app.routes import auth, ai, vault

app = FastAPI(
    title="KeyCrate API",
    description="AI-assisted password generator and secure vault system",
    version="1.0.0"
)

# CORS (important for frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint (Railway health check)
@app.get("/")
def read_root():
    return {"message": "KeyCrate backend is running"}

# Include routes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(ai.router, prefix="/ai", tags=["AI Generator"])
app.include_router(vault.router, prefix="/vault", tags=["Vault"])

