"""
LLM Service - Google Gemini API with retry logic
"""

import os
import json
import time
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import List

from src.analyzers.pgx_analyzer import DetectedVariant


@dataclass
class LLMExplanation:
    summary: str
    mechanism: str
    variant_impact: str
    clinical_context: str
    monitoring_parameters: str
    model_used: str


PHENOTYPE_LABELS = {
    "PM":  "Poor Metabolizer (absent enzyme activity)",
    "IM":  "Intermediate Metabolizer (reduced enzyme activity)",
    "NM":  "Normal Metabolizer (full enzyme activity)",
    "RM":  "Rapid Metabolizer (increased enzyme activity)",
    "URM": "Ultra-Rapid Metabolizer (markedly increased enzyme activity)",
    "Unknown": "Unknown metabolizer status",
}


def build_prompt(drug, gene, diplotype, phenotype, risk_label, severity, detected_variants):
    variant_details = "\n".join([
        f"  - {v.rsid}: {v.star_allele} star allele, effect = {v.effect}"
        for v in detected_variants
    ]) or "  - No pharmacogenomic variants detected (assumed *1/*1 wild-type)"

    phenotype_label = PHENOTYPE_LABELS.get(phenotype, phenotype)

    return f"""You are a senior clinical pharmacogenomics specialist writing an explanation for a clinical decision support system.

PATIENT PHARMACOGENOMIC PROFILE:
- Drug: {drug}
- Gene: {gene}
- Diplotype: {diplotype}
- Phenotype: {phenotype} — {phenotype_label}
- Risk: {risk_label} (Severity: {severity})
- Detected Variants:
{variant_details}

Return ONLY a valid JSON object with EXACTLY these keys, no markdown, no backticks:
{{
  "summary": "2-3 sentence clinical summary mentioning specific rsIDs and phenotype impact on {drug}",
  "mechanism": "How {gene} metabolizes {drug} and how detected variants alter this process",
  "variant_impact": "Specific impact of each detected variant on enzyme function and drug exposure",
  "clinical_context": "Clinical risks if standard {drug} dosing is used given this genotype",
  "monitoring_parameters": "Specific lab values and clinical signs to monitor if {drug} is prescribed"
}}"""


def call_gemini(prompt: str, api_key: str, retries: int = 3) -> dict:
    """Call Google Gemini API with retry on rate limit."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 1024}
    }).encode("utf-8")

    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, data=body,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()
                return json.loads(raw_text)

        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 10 * (attempt + 1)
                print(f"[LLM] Rate limited. Waiting {wait}s before retry {attempt+1}/{retries}")
                time.sleep(wait)
            else:
                raise
        except Exception as e:
            raise

    raise Exception("Gemini API rate limit exceeded after retries")


def generate_explanation(
    drug: str,
    gene: str,
    diplotype: str,
    phenotype: str,
    risk_label: str,
    severity: str,
    detected_variants: List[DetectedVariant]
) -> LLMExplanation:
    api_key = os.getenv("GEMINI_API_KEY", "")
    prompt = build_prompt(drug, gene, diplotype, phenotype, risk_label, severity, detected_variants)

    if api_key and api_key not in ("", "your_gemini_api_key_here"):
        try:
            parsed = call_gemini(prompt, api_key)
            return LLMExplanation(
                summary=parsed.get("summary", ""),
                mechanism=parsed.get("mechanism", ""),
                variant_impact=parsed.get("variant_impact", ""),
                clinical_context=parsed.get("clinical_context", ""),
                monitoring_parameters=parsed.get("monitoring_parameters", ""),
                model_used="gemini-2.0-flash"
            )
        except Exception as e:
            print(f"[LLM] Gemini failed: {e} — using fallback")

    # Structured Clinical Fallback
    variant_list = ", ".join(v.rsid for v in detected_variants) if detected_variants else "none detected"
    phenotype_label = PHENOTYPE_LABELS.get(phenotype, phenotype)

    effect_word = (
        "absent" if phenotype == "PM"
        else "reduced" if phenotype == "IM"
        else "markedly increased" if phenotype == "URM"
        else "altered"
    )
    outcome_word = (
        "therapeutic failure due to absent drug activation" if risk_label == "Ineffective"
        else "severe toxicity and adverse drug reactions" if risk_label == "Toxic"
        else "suboptimal therapeutic outcomes"
    )

    return LLMExplanation(
        summary=(
            f"This patient carries the {diplotype} diplotype for {gene}, "
            f"classified as {phenotype_label}. "
            f"Detected variants ({variant_list}) significantly impair {gene} enzymatic function, "
            f"resulting in a '{risk_label}' risk classification for {drug} therapy per CPIC guidelines."
        ),
        mechanism=(
            f"{gene} encodes a critical enzyme responsible for the biotransformation of {drug}. "
            f"The detected variant(s) — {variant_list} — introduce loss-of-function or reduced-function "
            f"alleles that result in {effect_word} {gene} enzyme activity, directly altering "
            f"{drug} plasma concentrations and therapeutic efficacy."
        ),
        variant_impact=(
            f"The identified variants ({variant_list}) confer {phenotype} metabolizer status. "
            f"Each variant disrupts normal {gene} protein folding or catalytic activity, "
            f"leading to {'complete absence' if phenotype == 'PM' else 'significant reduction'} "
            f"of {gene}-mediated {drug} metabolism and altered drug exposure."
        ),
        clinical_context=(
            f"In patients with {phenotype} status, standard {drug} dosing is associated with {outcome_word}. "
            f"This genotype has been clinically validated across multiple CPIC studies. "
            f"Prescribing {drug} at standard doses without genotype-guided adjustment poses "
            f"{'significant patient safety risks' if severity in ('high', 'critical') else 'therapeutic risks'} "
            f"preventable through pharmacogenomic-guided prescribing."
        ),
        monitoring_parameters=(
            f"If {drug} therapy is initiated, monitor: clinical response and symptom control, "
            f"drug plasma levels where available, signs of toxicity or treatment failure, "
            f"and CBC/LFTs as clinically indicated. "
            f"Consult a clinical pharmacist for individualized pharmacogenomics-guided dosing."
        ),
        model_used="structured-clinical-fallback-v1"
    )