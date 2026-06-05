from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from api import materials, ask, agents

app = FastAPI(
    title="Chacha Backend",
    description="Backend API for Chacha AI Course Agent Platform",
    version="1.0.0"
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(materials.router)
app.include_router(ask.router)
app.include_router(agents.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Chacha API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
