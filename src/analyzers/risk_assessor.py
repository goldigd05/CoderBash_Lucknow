"""
Risk Assessor
Maps gene phenotype → drug-specific clinical risk using CPIC guidelines.
"""

from dataclasses import dataclass
from typing import Optional
from src.models.pgx_knowledge import RISK_TABLE


@dataclass
class RiskAssessment:
    risk_label: str
    severity: str
    confidence_score: float
    action: str
    dosing_guidance: str
    urgency: str
    cpic_recommendation: str
    cpic_level: str


def assess_risk(drug: str, phenotype: str) -> RiskAssessment:
    """
    Look up clinical risk for a drug/phenotype combination.

    Args:
        drug: Drug name (uppercase).
        phenotype: Metabolizer phenotype (PM, IM, NM, RM, URM, Unknown).

    Returns:
        RiskAssessment dataclass.
    """
    drug_table = RISK_TABLE.get(drug.upper(), {})

    if not drug_table:
        return RiskAssessment(
            risk_label="Unknown",
            severity="none",
            confidence_score=0.50,
            action="Consult clinical pharmacist",
            dosing_guidance="No pharmacogenomic data available for this drug. Consult clinical pharmacist or pharmacogenomics specialist.",
            urgency="ROUTINE",
            cpic_recommendation="No CPIC guideline available for this drug.",
            cpic_level="N/A"
        )

    entry = drug_table.get(phenotype)

    if not entry:
        # Fallback to NM if phenotype not explicitly listed
        entry = drug_table.get("NM", {})
        if not entry:
            return RiskAssessment(
                risk_label="Unknown",
                severity="none",
                confidence_score=0.55,
                action="Consult clinical pharmacist",
                dosing_guidance="Phenotype not covered in current guideline for this drug. Exercise caution.",
                urgency="ROUTINE",
                cpic_recommendation="Phenotype-specific recommendation unavailable. Consult specialist.",
                cpic_level="Optional"
            )

    return RiskAssessment(
        risk_label=entry["risk_label"],
        severity=entry["severity"],
        confidence_score=entry["confidence_score"],
        action=entry["action"],
        dosing_guidance=entry["dosing_guidance"],
        urgency=entry["urgency"],
        cpic_recommendation=entry["cpic_recommendation"],
        cpic_level=entry["cpic_level"]
    )