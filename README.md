# 🧬 PharmaGuard — Pharmacogenomic Risk Prediction System

> **RIFT 2026 Hackathon** | Pharmacogenomics / Explainable AI Track

<h> Live Project demo</h>
https://coderbash-lucknow.onrender.com

<h>CPIC Guidelines </h>
[![CPIC Aligned](https://img.shields.io/badge/CPIC-Aligned-00b4ff?style=for-the-badge)](https://cpicpgx.org)


## 🔗 Important Links

| Resource | URL |
| Live Application |   -:YOUR_DEPLOYED_URL_HERE |
| Demo Video (LinkedIn)|   -: YOUR_LINKEDIN_VIDEO_URL_HERE |
| GitHub Repository** |  -: https://github.com/goldigd05/CoderBash_Lucknow |



## 📌 Project Title

PharmaGuard — AI-powered Pharmacogenomic Risk Prediction System  
RIFT 2026 Hackathon | Pharmacogenomics / Explainable AI Track



## 🎯 Problem Statement

Adverse drug reactions (ADRs) kill over **100,000 Americans annually**. Many of these deaths are preventable through pharmacogenomic testing — analyzing how a patient's genetic variants affect how they metabolize drugs.

Current clinical workflows lack real-time, personalized, AI-powered decision support that can analyze a patient's VCF genetic data and instantly predict drug-specific risks with clinically actionable, CPIC-aligned recommendations.

PharmaGuard solves this by combining VCF parsing, pharmacogenomic knowledge, and Google Gemini LLM to deliver explainable, personalized drug risk predictions in seconds.

## 🏗️ Architecture Overview

┌──────────────────────────────────────────────┐
│            FRONTEND (React + Vite)            │
│  VCF Upload → Drug Input → Results Dashboard  │
└─────────────────────┬────────────────────────┘
                      │ POST /api/analyze
                      ▼
┌──────────────────────────────────────────────┐
│          BACKEND (FastAPI + Python)           │
│                                              │
│  VCF Parser → PGx Analyzer → Risk Assessor  │
│                    ↓                         │
│          Google Gemini LLM (XAI)             │
│                    ↓                         │
│         JSON Output (RIFT Schema)            │
└──────────────────────────────────────────────┘


## 🧪 Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | FastAPI (Python 3.11+) |
| LLM Integration | Google Gemini 2.0 Flash (Free API) |
| VCF Parsing | Custom pure-Python VCF v4.2 parser |
| PGx Knowledge Base | CPIC-curated variant database |
| Frontend | React + Vite |
| Deployment | Render.com |
| API Docs | FastAPI Swagger UI (/docs) |

## 🧬 Genes & Drugs Supported

| Gene | Drug | Clinical Risk (PM) |
|---|---|---|
| CYP2D6 | CODEINE | Ineffective — no morphine conversion |
| CYP2C19 | CLOPIDOGREL | Ineffective — no antiplatelet activation |
| CYP2C9 | WARFARIN | Toxic — severe bleeding risk |
| SLCO1B1 | SIMVASTATIN | Toxic — myopathy/rhabdomyolysis |
| TPMT | AZATHIOPRINE | Toxic (Critical) — fatal myelosuppression |
| DPYD | FLUOROURACIL | Toxic (Critical) — fatal chemo toxicity |



## ⚡ Risk Labels

| Label | Color | Meaning |
|---|---|---|
| Safe | 🟢 Green | Standard dosing appropriate |
| Adjust Dosage | 🟡 Yellow | Dose modification required |
| Toxic | 🔴 Red | High toxicity risk at standard dose |
| Ineffective | 🟣 Purple | Drug will not work — use alternative |
| Unknown | ⚪ Gray | Insufficient pharmacogenomic data |



## 🚀 Installation & Setup

### Prerequisites
- Python 3.11+
- Google Gemini API key (free at aistudio.google.com)

### Backend Setup step by step

bash
# 1. Clone the repository
git clone https://github.com/goldigd05/CoderBash_Lucknow.git
cd CoderBash_Lucknow/Backend

# 2. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Add your GEMINI_API_KEY in .env file

# 5. Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

API live at: http://localhost:8000  
Swagger docs at: http://localhost:8000/docs

## 📡 API Documentation

### POST /api/analyze
Main analysis endpoint

Request — multipart/form-data:

| Field | Type | Required | Description |
|---|---|---|---|
| vcf_file | File (.vcf) | ✅ | Patient VCF file, max 5MB |
| drugs | String | ✅ | Comma-separated drug names |

Example:
bash
curl -X POST http://localhost:8000/api/analyze \
  -F "vcf_file=@sample_vcf/test_patient_001.vcf" \
  -F "drugs=CODEINE,WARFARIN"


Response — Exact  JSON Schema:
json
{
  "patient_id": "PATIENT_XXXXXX",
  "drug": "CODEINE",
  "timestamp": "2026-02-20T10:30:00Z",
  "risk_assessment": {
    "risk_label": "Safe",
    "confidence_score": 0.88,
    "severity": "none"
  },
  "pharmacogenomic_profile": {
    "primary_gene": "CYP2D6",
    "diplotype": "*1/*1",
    "phenotype": "NM",
    "detected_variants": []
  },
  "clinical_recommendation": {
    "action": "Standard dosing",
    "dosing_guidance": "...",
    "cpic_recommendation": "...",
    "urgency": "ROUTINE",
    "cpic_guideline_applicable": true
  },
  "llm_generated_explanation": {
    "summary": "...",
    "mechanism": "...",
    "variant_impact": "...",
    "clinical_context": "...",
    "monitoring_parameters": "...",
    "model_used": "gemini-2.0-flash"
  },
  "quality_metrics": {
    "vcf_parsing_success": true,
    "variants_analyzed_for_drug": 0,
    "confidence_level": "HIGH"
  }
}


### GET /api/health
Returns service status.

### GET /api/drugs
Returns all supported drugs and their genes.

### GET /api/genes
Returns all supported pharmacogenomic genes.

### GET /api/schema
Returns the full output JSON schema.



## 🧪 Usage Examples

Test with Normal Patient (all Safe):
bash
# Upload sample_vcf/test_patient_002_normal.vcf
# Drug: CODEINE,WARFARIN
# Expected: Safe for all drugs

Test with Variant Patient:
bash
# Upload sample_vcf/test_patient_001.vcf
# Drug: AZATHIOPRINE
# Expected: Toxic (critical) — TPMT Poor Metabolizer



## 🤖 LLM Integration (Explainable AI)

PharmaGuard uses **Google Gemini 2.0 Flash** to generate explainable clinical explanations:

- Every explanation **cites specific rsIDs** from the patient's VCF
- 5 structured fields: summary, mechanism, variant impact, clinical context, monitoring
- **Graceful fallback** if API unavailable — structured template used
- Prompt engineered for **clinician-grade** pharmacogenomic language
- CPIC guideline citations included in every response



## 📋 CPIC Alignment

All risk assessments follow **CPIC (Clinical Pharmacogenomics Implementation Consortium)** guidelines:
- Strong/Moderate recommendation levels included
- Dosing guidance from validated CPIC tables
- Reference URLs to cpicpgx.org in every response



## 👥 Team Members

| Name | Role |
|---|---|
| Dilip jagriti goldi|
| CoderBash tema name|


## 📁 Project Structure

Backend/
├── main.py                     ← FastAPI entry point
├── requirements.txt
├── .env.example
├── sample_vcf/
│   ├── test_patient_001.vcf    ← Variant patient test file
│   └── test_patient_002_normal.vcf  ← Normal patient test file
└── src/
    ├── parsers/
    │   └── vcf_parser.py       ← VCF v4.2 parser
    ├── models/
    │   └── pgx_knowledge.py    ← CPIC knowledge base
    ├── analyzers/
    │   ├── pgx_analyzer.py     ← Diplotype/phenotype engine
    │   └── risk_assessor.py    ← Risk lookup
    ├── services/
    │   ├── llm_service.py      ← Gemini API integration
    │   └── analysis_service.py ← Orchestrator
    └── routes/
        ├── analysis.py         ← API endpoints
        └── health.py           ← Health check




## 🌐 Deployment

Deployed on Render.com

Deploy your own:

1. Push code to GitHub
2. render.com → New Web Service
3. Build Command: pip install -r requirements.txt
4. Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
5. Environment Variable: GEMINI_API_KEY = your_key
6. Deploy → get live URL!




*Built with ❤️ at RIFT 2026 Hackathon | May this algorithm save lives.*
