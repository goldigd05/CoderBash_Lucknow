"""
PharmaGuard - Pharmacogenomic Risk Prediction System
RIFT 2026 Hackathon | Pharmacogenomics / Explainable AI Track
"""
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(analysis.router, prefix="/api", tags=["Analysis"])