"""
PGx Analyzer
Determines diplotype and phenotype from detected VCF variants.
CPIC-aligned phenotype assignment logic.
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass
from src.parsers.vcf_parser import VCFVariant
from src.models.pgx_knowledge import PGX_VARIANTS, PHENOTYPE_RULES, DRUG_GENE_MAP


@dataclass
class DetectedVariant:
    rsid: str
    gene: str
    star_allele: str
    effect: str
    chrom: str
    pos: int
    ref: str
    alt: str
    genotype: Optional[str]


@dataclass
class GenotypeResult:
    gene: str
    detected_variants: List[DetectedVariant]
    allele1: str
    allele2: str
    diplotype: str
    phenotype: str
    activity_score: Optional[float]


def find_gene_for_drug(drug: str) -> Optional[str]:
    return DRUG_GENE_MAP.get(drug.upper())


def detect_variants(vcf_variants: List[VCFVariant], gene: str) -> List[DetectedVariant]:
    """
    Cross-reference VCF variants against PGx knowledge base for a given gene.
    """
    detected = []
    seen_rsids = set()

    for v in vcf_variants:
        # Match by rsID in knowledge base
        rsid = v.rsid
        if rsid and rsid in PGX_VARIANTS:
            kb_entry = PGX_VARIANTS[rsid]
            if kb_entry["gene"] == gene and rsid not in seen_rsids:
                seen_rsids.add(rsid)
                detected.append(DetectedVariant(
                    rsid=rsid,
                    gene=gene,
                    star_allele=kb_entry["star"],
                    effect=kb_entry["effect"],
                    chrom=v.chrom,
                    pos=v.pos,
                    ref=v.ref,
                    alt=v.alt,
                    genotype=v.genotype
                ))
        # Also match by gene tag in VCF
        elif v.gene and v.gene.upper() == gene and rsid and rsid not in seen_rsids:
            seen_rsids.add(rsid)
            detected.append(DetectedVariant(
                rsid=rsid,
                gene=gene,
                star_allele=v.star_allele or "Unknown",
                effect="unknown",
                chrom=v.chrom,
                pos=v.pos,
                ref=v.ref,
                alt=v.alt,
                genotype=v.genotype
            ))

    return detected


def assign_phenotype(gene: str, detected: List[DetectedVariant]) -> Tuple[str, str, str, Optional[float]]:
    """
    Assign phenotype and construct diplotype from detected variants.

    Returns:
        (allele1, allele2, diplotype, phenotype, activity_score)
    """
    lof = [d for d in detected if d.effect == "loss_of_function"]
    reduced = [d for d in detected if d.effect == "reduced_function"]
    increased = [d for d in detected if d.effect == "increased_function"]

    rules = PHENOTYPE_RULES.get(gene, [{"default": True, "phenotype": "Unknown"}])

    phenotype = "Unknown"
    for rule in rules:
        if rule.get("default"):
            phenotype = rule["phenotype"]
            break
        lof_ok = len(lof) >= rule.get("min_lof", 0)
        red_ok = len(reduced) >= rule.get("min_reduced", 0)
        inc_ok = len(increased) >= rule.get("min_increased", 0)
        checks = []
        if "min_lof" in rule: checks.append(lof_ok)
        if "min_reduced" in rule: checks.append(red_ok)
        if "min_increased" in rule: checks.append(inc_ok)
        if checks and all(checks):
            phenotype = rule["phenotype"]
            break

    # Build diplotype
    all_alleles = [d.star_allele for d in detected if d.star_allele and d.star_allele != "Unknown"]
    if len(all_alleles) == 0:
        allele1, allele2 = "*1", "*1"
    elif len(all_alleles) == 1:
        allele1, allele2 = "*1", all_alleles[0]
    else:
        allele1, allele2 = all_alleles[0], all_alleles[1]

    diplotype = f"{allele1}/{allele2}"

    # Activity score (simplified)
    activity_map = {"loss_of_function": 0, "reduced_function": 0.5, "normal_function": 1, "increased_function": 2}
    if detected:
        scores = [activity_map.get(d.effect, 1) for d in detected]
        activity_score = round(sum(scores) / len(scores), 2)
    else:
        activity_score = 1.0

    return allele1, allele2, diplotype, phenotype, activity_score


def analyze_genotype(vcf_variants: List[VCFVariant], gene: str) -> GenotypeResult:
    """Full genotype analysis for a single gene."""
    detected = detect_variants(vcf_variants, gene)
    allele1, allele2, diplotype, phenotype, activity_score = assign_phenotype(gene, detected)

    return GenotypeResult(
        gene=gene,
        detected_variants=detected,
        allele1=allele1,
        allele2=allele2,
        diplotype=diplotype,
        phenotype=phenotype,
        activity_score=activity_score
    )