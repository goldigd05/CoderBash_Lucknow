"""
PharmaGuard - Pharmacogenomic Risk Prediction System
RIFT 2026 Hackathon | Pharmacogenomics / Explainable AI Track
"""
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.routes import analysis, health

app = FastAPI(
    title="PharmaGuard API",
    description="Pharmacogenomic Risk Prediction System - RIFT 2026",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. API Routes (Inhe pehle rehne dein)
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(analysis.router, prefix="/api", tags=["Analysis"])

# 2. Frontend Files Mounting
# Agar folder ka naam 'Frontend' hai (F capital), toh yahan wahi likhein
if os.path.exists("Frontend"):
    app.mount("/Frontend", StaticFiles(directory="Frontend"), name="Frontend")

# 3. Home Route: Ye index.html ko serve karega
@app.get("/")
async def serve_frontend():
    return FileResponse("Frontend/index.html")