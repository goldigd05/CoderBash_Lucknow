"""Health check routes."""
from fastapi import APIRouter
from datetime import datetime, timezone
import os

router = APIRouter()

@router.get("/health", summary="Health check")
async def health():
    return {
        "status": "healthy",
        "service": "PharmaGuard API",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "llm_configured": bool(os.getenv("ANTHROPIC_API_KEY")),
        "supported_drugs": ["CODEINE", "WARFARIN", "CLOPIDOGREL", "SIMVASTATIN", "AZATHIOPRINE", "FLUOROURACIL"],
        "supported_genes": ["CYP2D6", "CYP2C19", "CYP2C9", "SLCO1B1", "TPMT", "DPYD"]
    }