"""
Pharmacogenomic Knowledge Base
Based on CPIC (Clinical Pharmacogenomics Implementation Consortium) Guidelines
Covers: CYP2D6, CYP2C19, CYP2C9, SLCO1B1, TPMT, DPYD
"""

# ─────────────────────────────────────────────
# VARIANT DATABASE
# rsID → gene, star allele, functional effect
# ─────────────────────────────────────────────

PGX_VARIANTS = {
    # CYP2D6
    "rs3892097":  {"gene": "CYP2D6",  "star": "*4",    "effect": "loss_of_function"},
    "rs1065852":  {"gene": "CYP2D6",  "star": "*10",   "effect": "reduced_function"},
    "rs5030655":  {"gene": "CYP2D6",  "star": "*6",    "effect": "loss_of_function"},
    "rs16947":    {"gene": "CYP2D6",  "star": "*2",    "effect": "normal_function"},
    "rs1135840":  {"gene": "CYP2D6",  "star": "*2",    "effect": "normal_function"},
    "rs28371706": {"gene": "CYP2D6",  "star": "*41",   "effect": "reduced_function"},
    "rs769258":   {"gene": "CYP2D6",  "star": "*17",   "effect": "reduced_function"},

    # CYP2C19
    "rs4244285":  {"gene": "CYP2C19", "star": "*2",    "effect": "loss_of_function"},
    "rs4986893":  {"gene": "CYP2C19", "star": "*3",    "effect": "loss_of_function"},
    "rs12248560": {"gene": "CYP2C19", "star": "*17",   "effect": "increased_function"},
    "rs28399504": {"gene": "CYP2C19", "star": "*4",    "effect": "loss_of_function"},
    "rs41291556": {"gene": "CYP2C19", "star": "*8",    "effect": "loss_of_function"},

    # CYP2C9
    "rs1799853":  {"gene": "CYP2C9",  "star": "*2",    "effect": "reduced_function"},
    "rs1057910":  {"gene": "CYP2C9",  "star": "*3",    "effect": "loss_of_function"},
    "rs28371686": {"gene": "CYP2C9",  "star": "*5",    "effect": "loss_of_function"},
    "rs9332131":  {"gene": "CYP2C9",  "star": "*6",    "effect": "loss_of_function"},
    "rs7900194":  {"gene": "CYP2C9",  "star": "*8",    "effect": "reduced_function"},

    # SLCO1B1
    "rs4149056":  {"gene": "SLCO1B1", "star": "*5",    "effect": "reduced_function"},
    "rs2306283":  {"gene": "SLCO1B1", "star": "*1B",   "effect": "normal_function"},
    "rs11045852": {"gene": "SLCO1B1", "star": "*14",   "effect": "reduced_function"},

    # TPMT
    "rs1800460":  {"gene": "TPMT",    "star": "*3B",   "effect": "loss_of_function"},
    "rs1142345":  {"gene": "TPMT",    "star": "*3C",   "effect": "loss_of_function"},
    "rs1800462":  {"gene": "TPMT",    "star": "*2",    "effect": "loss_of_function"},
    "rs1800584":  {"gene": "TPMT",    "star": "*4",    "effect": "loss_of_function"},

    # DPYD
    "rs3918290":  {"gene": "DPYD",    "star": "*2A",   "effect": "loss_of_function"},
    "rs55886062": {"gene": "DPYD",    "star": "*13",   "effect": "loss_of_function"},
    "rs67376798": {"gene": "DPYD",    "star": "HapB3", "effect": "reduced_function"},
    "rs75017182": {"gene": "DPYD",    "star": "HapB3", "effect": "reduced_function"},
}

# Set of all known PGx rsIDs for fast lookup
KNOWN_PGX_RSIDS = set(PGX_VARIANTS.keys())

# ─────────────────────────────────────────────
# DRUG → GENE MAPPING
# ─────────────────────────────────────────────

DRUG_GENE_MAP = {
    "CODEINE":      "CYP2D6",
    "WARFARIN":     "CYP2C9",
    "CLOPIDOGREL":  "CYP2C19",
    "SIMVASTATIN":  "SLCO1B1",
    "AZATHIOPRINE": "TPMT",
    "FLUOROURACIL": "DPYD",
}

# ─────────────────────────────────────────────
# PHENOTYPE DETERMINATION RULES
# Per CPIC diplotype → phenotype guidelines
# ─────────────────────────────────────────────

PHENOTYPE_RULES = {
    # (lof_count, reduced_count, increased_count) → phenotype
    "CYP2D6": [
        {"min_lof": 2,                              "phenotype": "PM"},
        {"min_lof": 1, "min_reduced": 1,            "phenotype": "IM"},
        {"min_lof": 1,                              "phenotype": "IM"},
        {"min_reduced": 2,                          "phenotype": "IM"},
        {"min_reduced": 1,                          "phenotype": "IM"},
        {"min_increased": 1,                        "phenotype": "RM"},
        {"default": True,                           "phenotype": "NM"},
    ],
    "CYP2C19": [
        {"min_lof": 2,                              "phenotype": "PM"},
        {"min_lof": 1, "min_reduced": 1,            "phenotype": "IM"},
        {"min_lof": 1,                              "phenotype": "IM"},
        {"min_increased": 2,                        "phenotype": "URM"},
        {"min_increased": 1,                        "phenotype": "RM"},
        {"default": True,                           "phenotype": "NM"},
    ],
    "CYP2C9": [
        {"min_lof": 2,                              "phenotype": "PM"},
        {"min_lof": 1, "min_reduced": 1,            "phenotype": "IM"},
        {"min_lof": 1,                              "phenotype": "IM"},
        {"min_reduced": 2,                          "phenotype": "IM"},
        {"min_reduced": 1,                          "phenotype": "IM"},
        {"default": True,                           "phenotype": "NM"},
    ],
    "SLCO1B1": [
        {"min_reduced": 2,                          "phenotype": "PM"},
        {"min_lof": 1,                              "phenotype": "PM"},
        {"min_reduced": 1,                          "phenotype": "IM"},
        {"default": True,                           "phenotype": "NM"},
    ],
    "TPMT": [
        {"min_lof": 2,                              "phenotype": "PM"},
        {"min_lof": 1,                              "phenotype": "IM"},
        {"min_reduced": 1,                          "phenotype": "IM"},
        {"default": True,                           "phenotype": "NM"},
    ],
    "DPYD": [
        {"min_lof": 2,                              "phenotype": "PM"},
        {"min_lof": 1,                              "phenotype": "IM"},
        {"min_reduced": 2,                          "phenotype": "IM"},
        {"min_reduced": 1,                          "phenotype": "IM"},
        {"default": True,                           "phenotype": "NM"},
    ],
}

# ─────────────────────────────────────────────
# RISK LOOKUP TABLE
# drug + phenotype → clinical risk + CPIC recommendation
# ─────────────────────────────────────────────

RISK_TABLE = {
    "CODEINE": {
        "PM":  {
            "risk_label": "Ineffective",
            "severity": "moderate",
            "confidence_score": 0.91,
            "action": "Use alternative analgesic",
            "dosing_guidance": "Codeine is a prodrug converted to morphine by CYP2D6. Poor metabolizers cannot perform this conversion. Select a non-opioid analgesic or tramadol with caution. Avoid codeine entirely.",
            "urgency": "HIGH",
            "cpic_recommendation": "Avoid codeine. Use alternative such as morphine (not tramadol) or a non-opioid analgesic.",
            "cpic_level": "Strong"
        },
        "IM":  {
            "risk_label": "Adjust Dosage",
            "severity": "low",
            "confidence_score": 0.82,
            "action": "Reduce dose or use alternative",
            "dosing_guidance": "Intermediate metabolizers have reduced CYP2D6 activity. Codeine conversion to morphine is slower, leading to reduced efficacy. Consider dose adjustment or alternative analgesic.",
            "urgency": "ROUTINE",
            "cpic_recommendation": "Use label-recommended age- or weight-specific dosing. If no response, consider alternative analgesic.",
            "cpic_level": "Moderate"
        },
        "NM":  {
            "risk_label": "Safe",
            "severity": "none",
            "confidence_score": 0.88,
            "action": "Standard dosing",
            "dosing_guidance": "Normal CYP2D6 activity. Standard codeine dosing is appropriate. Monitor for typical opioid side effects.",
            "urgency": "ROUTINE",
            "cpic_recommendation": "Use label-recommended dosing.",
            "cpic_level": "Strong"
        },
        "RM":  {
            "risk_label": "Safe",
            "severity": "low",
            "confidence_score": 0.84,
            "action": "Standard dosing with monitoring",
            "dosing_guidance": "Rapid metabolizer. Slightly enhanced conversion. Standard dosing generally appropriate. Monitor analgesic response.",
            "urgency": "ROUTINE",
            "cpic_recommendation": "Use label-recommended dosing.",
            "cpic_level": "Moderate"
        },
        "URM": {
            "risk_label": "Toxic",
            "severity": "critical",
            "confidence_score": 0.96,
            "action": "CONTRAINDICATED",
            "dosing_guidance": "CONTRAINDICATED. Ultra-rapid metabolism produces excessive morphine causing life-threatening respiratory depression. Documented fatalities reported. Use non-opioid analgesic.",
            "urgency": "IMMEDIATE",
            "cpic_recommendation": "Avoid codeine. Risk of life-threatening or fatal respiratory depression.",
            "cpic_level": "Strong"
        },
    },
    "WARFARIN": {
        "PM":  {
            "risk_label": "Toxic",
            "severity": "high",
            "confidence_score": 0.94,
            "action": "Significant dose reduction required",
            "dosing_guidance": "Significantly reduced CYP2C9 metabolism. Warfarin clearance is markedly decreased. Start at 20-40% of standard dose. Frequent INR monitoring mandatory. Target INR range 2.0-3.0.",
            "urgency": "HIGH",
            "cpic_recommendation": "Use CPIC warfarin dosing algorithm incorporating CYP2C9 and VKORC1 genotype.",
            "cpic_level": "Strong"
        },
        "IM":  {
            "risk_label": "Adjust Dosage",
            "severity": "moderate",
            "confidence_score": 0.89,
            "action": "Reduce starting dose",
            "dosing_guidance": "Reduced warfarin clearance. Initiate at lower dose. Weekly INR checks for first month. Use pharmacogenomics-based dosing calculator (e.g., warfarindosing.org).",
            "urgency": "HIGH",
            "cpic_recommendation": "Use CPIC warfarin dosing algorithm. Reduce starting dose by 15-30%.",
            "cpic_level": "Strong"
        },
        "NM":  {
            "risk_label": "Safe",
            "severity": "none",
            "confidence_score": 0.88,
            "action": "Standard dosing",
            "dosing_guidance": "Normal warfarin metabolism expected. Use standard warfarin initiation protocol with routine INR monitoring.",
            "urgency": "ROUTINE",
            "cpic_recommendation": "Use standard warfarin dosing.",
            "cpic_level": "Strong"
        },
    },
    "CLOPIDOGREL": {
        "PM":  {
            "risk_label": "Ineffective",
            "severity": "high",
            "confidence_score": 0.93,
            "action": "Use alternative antiplatelet",
            "dosing_guidance": "Clopidogrel requires CYP2C19 for bioactivation. Poor metabolizers cannot generate active metabolite, leading to inadequate platelet inhibition and increased MACE risk. Switch to prasugrel or ticagrelor.",
            "urgency": "HIGH",
            "cpic_recommendation": "Use alternative antiplatelet therapy (prasugrel or ticagrelor) if no contraindication.",
            "cpic_level": "Strong"
        },
        "IM":  {
            "risk_label": "Adjust Dosage",
            "severity": "moderate",
            "confidence_score": 0.87,
            "action": "Consider alternative or increased monitoring",
            "dosing_guidance": "Reduced clopidogrel activation. Clinical significance depends on indication. Consider prasugrel or ticagrelor for high-risk ACS patients.",
            "urgency": "ROUTINE",
            "cpic_recommendation": "Use alternative antiplatelet therapy if clinically indicated.",
            "cpic_level": "Moderate"
        },
        "NM":  {
            "risk_label": "Safe",
            "severity": "none",
            "confidence_score": 0.90,
            "action": "Standard dosing",
            "dosing_guidance": "Normal clopidogrel activation. Standard dosing appropriate. 75mg daily per label.",
            "urgency": "ROUTINE",
            "cpic_recommendation": "Use label-recommended dosing.",
            "cpic_level": "Strong"
        },
        "RM":  {
            "risk_label": "Safe",
            "severity": "none",
            "confidence_score": 0.86,
            "action": "Standard dosing",
            "dosing_guidance": "Rapid CYP2C19 metabolism. Enhanced clopidogrel activation. Standard dosing appropriate.",
            "urgency": "ROUTINE",
            "cpic_recommendation": "Use label-recommended dosing.",
            "cpic_level": "Moderate"
        },
        "URM": {
            "risk_label": "Safe",
            "severity": "low",
            "confidence_score": 0.83,
            "action": "Standard dosing with monitoring",
            "dosing_guidance": "Ultra-rapid metabolism. Monitor for enhanced antiplatelet effect and bleeding risk.",
            "urgency": "ROUTINE",
            "cpic_recommendation": "Use label-recommended dosing. Monitor for bleeding.",
            "cpic_level": "Moderate"
        },
    },
    "SIMVASTATIN": {
        "PM":  {
            "risk_label": "Toxic",
            "severity": "high",
            "confidence_score": 0.92,
            "action": "Avoid simvastatin or use lowest dose",
            "dosing_guidance": "Significantly increased simvastatin plasma levels due to reduced SLCO1B1-mediated hepatic uptake. High risk of myopathy and rhabdomyolysis. Use rosuvastatin, pravastatin, or fluvastatin as alternatives.",
            "urgency": "HIGH",
            "cpic_recommendation": "Avoid simvastatin 80mg. Consider lower-risk statin (rosuvastatin, pravastatin).",
            "cpic_level": "Strong"
        },
        "IM":  {
            "risk_label": "Adjust Dosage",
            "severity": "moderate",
            "confidence_score": 0.85,
            "action": "Use simvastatin ≤20mg or switch statin",
            "dosing_guidance": "Moderately increased simvastatin exposure. Limit dose to ≤20mg or switch to rosuvastatin/pravastatin. Monitor CK levels periodically.",
            "urgency": "ROUTINE",
            "cpic_recommendation": "Prescribe simvastatin ≤20mg daily or use alternative statin.",
            "cpic_level": "Strong"
        },
        "NM":  {
            "risk_label": "Safe",
            "severity": "none",
            "confidence_score": 0.87,
            "action": "Standard dosing",
            "dosing_guidance": "Normal SLCO1B1 function. Standard simvastatin dosing appropriate with routine hepatic and muscular monitoring.",
            "urgency": "ROUTINE",
            "cpic_recommendation": "Use label-recommended dosing.",
            "cpic_level": "Strong"
        },
    },
    "AZATHIOPRINE": {
        "PM":  {
            "risk_label": "Toxic",
            "severity": "critical",
            "confidence_score": 0.97,
            "action": "CONTRAINDICATED",
            "dosing_guidance": "CONTRAINDICATED. TPMT-deficient patients accumulate toxic thioguanine nucleotides causing severe, potentially fatal myelosuppression (bone marrow failure). Use alternative immunosuppressant (mycophenolate mofetil, cyclosporine).",
            "urgency": "IMMEDIATE",
            "cpic_recommendation": "Avoid azathioprine/6-mercaptopurine. Use alternative non-thiopurine immunosuppressant.",
            "cpic_level": "Strong"
        },
        "IM":  {
            "risk_label": "Adjust Dosage",
            "severity": "high",
            "confidence_score": 0.91,
            "action": "Reduce dose significantly",
            "dosing_guidance": "Start at 30-70% of standard dose. Strict CBC monitoring weekly for 4 weeks, then monthly. Dose escalation should be very gradual.",
            "urgency": "HIGH",
            "cpic_recommendation": "Start with 30-70% of recommended dose. Allow 4 weeks to reach steady state before further dose adjustments.",
            "cpic_level": "Strong"
        },
        "NM":  {
            "risk_label": "Safe",
            "severity": "none",
            "confidence_score": 0.89,
            "action": "Standard dosing",
            "dosing_guidance": "Normal TPMT activity. Standard azathioprine dosing. Routine CBC monitoring as per label.",
            "urgency": "ROUTINE",
            "cpic_recommendation": "Use label-recommended dosing.",
            "cpic_level": "Strong"
        },
    },
    "FLUOROURACIL": {
        "PM":  {
            "risk_label": "Toxic",
            "severity": "critical",
            "confidence_score": 0.96,
            "action": "CONTRAINDICATED",
            "dosing_guidance": "CONTRAINDICATED. DPYD-deficient patients cannot catabolize fluorouracil, resulting in severe or fatal toxicity (mucositis, neutropenia, neurotoxicity, death). Use alternative chemotherapy.",
            "urgency": "IMMEDIATE",
            "cpic_recommendation": "Avoid fluorouracil/capecitabine. Select alternative chemotherapeutic agent.",
            "cpic_level": "Strong"
        },
        "IM":  {
            "risk_label": "Adjust Dosage",
            "severity": "high",
            "confidence_score": 0.90,
            "action": "50% dose reduction",
            "dosing_guidance": "50% dose reduction recommended per EMA and CPIC guidance. Enhanced toxicity monitoring at each cycle. Consider DPD phenotyping (uracil breath test) before treatment initiation.",
            "urgency": "HIGH",
            "cpic_recommendation": "Reduce starting dose by 50%. Titrate based on toxicity and efficacy.",
            "cpic_level": "Strong"
        },
        "NM":  {
            "risk_label": "Safe",
            "severity": "none",
            "confidence_score": 0.88,
            "action": "Standard dosing",
            "dosing_guidance": "Normal DPYD function. Standard fluorouracil dosing per oncology protocol. Routine toxicity monitoring.",
            "urgency": "ROUTINE",
            "cpic_recommendation": "Use label-recommended dosing per oncology protocol.",
            "cpic_level": "Strong"
        },
    },
}