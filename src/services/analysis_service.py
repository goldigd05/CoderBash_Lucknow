"""
Analysis Orchestrator Service
Ties together: VCF parsing → PGx analysis → Risk assessment → LLM explanation → JSON output
"""

import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any

from src.parsers.vcf_parser import parse_vcf_content
from src.analyzers.pgx_analyzer import analyze_genotype, find_gene_for_drug
from src.analyzers.risk_assessor import assess_risk
from src.services.llm_service import generate_explanation


def build_output_json(
    patient_id: str,
    drug: str,
    gene: str,
    genotype_result,
    risk,
    llm_explanation,
    vcf_parse_result
) -> Dict[str, Any]:
    """Build the exact JSON schema required by RIFT 2026 hackathon."""
    return {
        "patient_id": patient_id,
        "drug": drug.upper(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "risk_assessment": {
            "risk_label": risk.risk_label,
            "confidence_score": risk.confidence_score,
            "severity": risk.severity
        },
        "pharmacogenomic_profile": {
            "primary_gene": gene,
            "diplotype": genotype_result.diplotype,
            "phenotype": genotype_result.phenotype,
            "activity_score": genotype_result.activity_score,
            "detected_variants": [
                {
                    "rsid": v.rsid,
                    "gene": v.gene,
                    "star_allele": v.star_allele,
                    "effect": v.effect,
                    "chrom": v.chrom,
                    "pos": v.pos,
                    "ref": v.ref,
                    "alt": v.alt,
                    "genotype": v.genotype,
                    "clinical_significance": "Pharmacogenomic variant — CPIC curated"
                }
                for v in genotype_result.detected_variants
            ]
        },
        "clinical_recommendation": {
            "action": risk.action,
            "risk_label": risk.risk_label,
            "dosing_guidance": risk.dosing_guidance,
            "cpic_recommendation": risk.cpic_recommendation,
            "cpic_guideline_level": risk.cpic_level,
            "urgency": risk.urgency,
            "cpic_guideline_applicable": True,
            "cpic_reference_url": f"https://cpicpgx.org/guidelines/"
        },
        "llm_generated_explanation": {
            "summary": llm_explanation.summary,
            "mechanism": llm_explanation.mechanism,
            "variant_impact": llm_explanation.variant_impact,
            "clinical_context": llm_explanation.clinical_context,
            "monitoring_parameters": llm_explanation.monitoring_parameters,
            "model_used": llm_explanation.model_used,
            "explanation_method": "Anthropic Claude LLM with CPIC knowledge base"
        },
        "quality_metrics": {
            "vcf_parsing_success": vcf_parse_result.success,
            "total_vcf_records": vcf_parse_result.total_records,
            "pharmacogenomic_variants_in_vcf": vcf_parse_result.pharmacogenomic_variants,
            "variants_analyzed_for_drug": len(genotype_result.detected_variants),
            "gene_coverage": [gene],
            "confidence_level": (
                "HIGH" if risk.confidence_score >= 0.85
                else "MODERATE" if risk.confidence_score >= 0.70
                else "LOW"
            ),
            "parse_errors": vcf_parse_result.errors
        }
    }


def run_analysis(vcf_content: str, drugs: List[str]) -> Dict[str, Any]:
    """
    Main analysis pipeline.

    Args:
        vcf_content: Raw VCF file content as string.
        drugs: List of drug names to analyze.

    Returns:
        Dict with patient_id and list of per-drug results.
    """
    patient_id = f"PATIENT_{uuid.uuid4().hex[:6].upper()}"

    # Step 1: Parse VCF
    vcf_result = parse_vcf_content(vcf_content)

    results = []
    errors = []

    for drug in drugs:
        drug = drug.strip().upper()

        # Step 2: Map drug → gene
        gene = find_gene_for_drug(drug)
        if not gene:
            errors.append({
                "drug": drug,
                "error": f"Drug '{drug}' is not supported. Supported drugs: CODEINE, WARFARIN, CLOPIDOGREL, SIMVASTATIN, AZATHIOPRINE, FLUOROURACIL"
            })
            continue

        # Step 3: Genotype analysis
        genotype_result = analyze_genotype(vcf_result.variants, gene)

        # Step 4: Risk assessment
        risk = assess_risk(drug, genotype_result.phenotype)

        # Step 5: LLM explanation
        llm = generate_explanation(
            drug=drug,
            gene=gene,
            diplotype=genotype_result.diplotype,
            phenotype=genotype_result.phenotype,
            risk_label=risk.risk_label,
            severity=risk.severity,
            detected_variants=genotype_result.detected_variants
        )

        # Step 6: Build output JSON
        output = build_output_json(
            patient_id=patient_id,
            drug=drug,
            gene=gene,
            genotype_result=genotype_result,
            risk=risk,
            llm_explanation=llm,
            vcf_parse_result=vcf_result
        )
        results.append(output)

    return {
        "patient_id": patient_id,
        "analysis_count": len(results),
        "vcf_parse_success": vcf_result.success,
        "results": results,
        "errors": errors
    }