"""
Analysis Routes
POST /api/analyze  - Main analysis endpoint
GET  /api/drugs    - List supported drugs
GET  /api/genes    - List supported genes
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
import json

from src.services.analysis_service import run_analysis
from src.models.pgx_knowledge import DRUG_GENE_MAP

router = APIRouter()

SUPPORTED_GENES_LIST = ["CYP2D6", "CYP2C19", "CYP2C9", "SLCO1B1", "TPMT", "DPYD"]
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/analyze", summary="Analyze VCF file for pharmacogenomic risk")
async def analyze(
    vcf_file: UploadFile = File(..., description="VCF file (v4.2, max 5MB)"),
    drugs: str = Form(..., description="Comma-separated drug names. e.g., CODEINE,WARFARIN")
):
    """
    **Main Analysis Endpoint**

    Upload a VCF file and specify drug(s) to receive:
    - Pharmacogenomic risk assessment (Safe / Adjust Dosage / Toxic / Ineffective)
    - CPIC-aligned dosing recommendations
    - AI-generated clinical explanations (Claude LLM)
    - Exact JSON schema output per RIFT 2026 specification

    **Supported drugs:** CODEINE, WARFARIN, CLOPIDOGREL, SIMVASTATIN, AZATHIOPRINE, FLUOROURACIL
    """
    # Validate file type
    if not vcf_file.filename.endswith(".vcf"):
        raise HTTPException(status_code=400, detail="Only .vcf files are accepted.")

    # Read and size-check
    content_bytes = await vcf_file.read()
    if len(content_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File size exceeds 5MB limit.")

    # Decode
    try:
        vcf_content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="VCF file must be UTF-8 encoded.")

    # Validate it looks like a VCF
    if "##fileformat=VCF" not in vcf_content and "#CHROM" not in vcf_content:
        raise HTTPException(status_code=400, detail="File does not appear to be a valid VCF. Missing VCF headers.")

    # Parse drug list
    drug_list = [d.strip().upper() for d in drugs.split(",") if d.strip()]
    if not drug_list:
        raise HTTPException(status_code=400, detail="At least one drug name must be provided.")

    if len(drug_list) > 6:
        raise HTTPException(status_code=400, detail="Maximum 6 drugs per request.")

    # Run analysis pipeline
    try:
        result = run_analysis(vcf_content, drug_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis pipeline failed: {str(e)}")

    return JSONResponse(content=result)


@router.get("/drugs", summary="List supported drugs and their primary genes")
async def list_drugs():
    """Returns all supported drugs and their associated pharmacogenomic genes."""
    return {
        "supported_drugs": [
            {"drug": drug, "primary_gene": gene}
            for drug, gene in DRUG_GENE_MAP.items()
        ]
    }


@router.get("/genes", summary="List supported pharmacogenomic genes")
async def list_genes():
    """Returns all pharmacogenomic genes analyzed by PharmaGuard."""
    return {
        "supported_genes": SUPPORTED_GENES_LIST,
        "total": len(SUPPORTED_GENES_LIST)
    }


@router.get("/schema", summary="Get the output JSON schema")
async def get_schema():
    """Returns the expected output JSON schema structure."""
    return {
        "schema": {
            "patient_id": "PATIENT_XXXXXX",
            "drug": "DRUG_NAME",
            "timestamp": "ISO8601",
            "risk_assessment": {
                "risk_label": "Safe|Adjust Dosage|Toxic|Ineffective|Unknown",
                "confidence_score": "0.0-1.0",
                "severity": "none|low|moderate|high|critical"
            },
            "pharmacogenomic_profile": {
                "primary_gene": "GENE_SYMBOL",
                "diplotype": "*X/*Y",
                "phenotype": "PM|IM|NM|RM|URM|Unknown",
                "activity_score": "0.0-2.0",
                "detected_variants": [{"rsid": "...", "gene": "...", "star_allele": "...", "effect": "..."}]
            },
            "clinical_recommendation": {
                "action": "...",
                "dosing_guidance": "...",
                "cpic_recommendation": "...",
                "urgency": "IMMEDIATE|HIGH|ROUTINE"
            },
            "llm_generated_explanation": {
                "summary": "...",
                "mechanism": "...",
                "variant_impact": "...",
                "clinical_context": "...",
                "monitoring_parameters": "...",
                "model_used": "claude-sonnet-4-20250514"
            },
            "quality_metrics": {
                "vcf_parsing_success": True,
                "variants_analyzed_for_drug": 0,
                "confidence_level": "HIGH|MODERATE|LOW"
            }
        }
    }