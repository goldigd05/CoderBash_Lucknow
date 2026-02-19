"""
VCF Parser - Parses Variant Call Format (VCF v4.2) files
Extracts pharmacogenomic variants for CYP2D6, CYP2C19, CYP2C9, SLCO1B1, TPMT, DPYD
"""

from dataclasses import dataclass, field
from typing import List, Optional
import re


@dataclass
class VCFVariant:
    chrom: str
    pos: int
    rsid: Optional[str]
    ref: str
    alt: str
    qual: str
    filter_status: str
    gene: Optional[str]
    star_allele: Optional[str]
    genotype: Optional[str]
    raw_info: dict = field(default_factory=dict)


@dataclass
class VCFParseResult:
    success: bool
    variants: List[VCFVariant]
    total_records: int
    pharmacogenomic_variants: int
    errors: List[str]
    metadata: dict


SUPPORTED_GENES = {"CYP2D6", "CYP2C19", "CYP2C9", "SLCO1B1", "TPMT", "DPYD"}


def parse_info_field(info_str: str) -> dict:
    """Parse VCF INFO field into a dictionary."""
    info = {}
    for item in info_str.split(";"):
        if "=" in item:
            k, v = item.split("=", 1)
            info[k.strip()] = v.strip()
        else:
            info[item.strip()] = True
    return info


def parse_genotype(format_str: str, sample_str: str) -> Optional[str]:
    """Extract GT (genotype) from FORMAT/SAMPLE columns."""
    try:
        keys = format_str.split(":")
        values = sample_str.split(":")
        fmt_map = dict(zip(keys, values))
        return fmt_map.get("GT")
    except Exception:
        return None


def parse_vcf_content(content: str) -> VCFParseResult:
    """
    Main VCF parsing function.
    
    Args:
        content: Raw string content of the VCF file.
    
    Returns:
        VCFParseResult with all parsed variants and metadata.
    """
    variants = []
    errors = []
    metadata = {}
    total_records = 0

    lines = content.strip().split("\n")

    for line in lines:
        line = line.strip()

        # Parse metadata headers
        if line.startswith("##"):
            if "=" in line:
                key, val = line[2:].split("=", 1)
                metadata[key] = val
            continue

        # Parse column header
        if line.startswith("#CHROM"):
            continue

        if not line:
            continue

        total_records += 1
        parts = line.split("\t")

        if len(parts) < 8:
            errors.append(f"Line {total_records}: Malformed record (< 8 columns) — skipped")
            continue

        chrom = parts[0]
        pos_str = parts[1]
        id_col = parts[2]
        ref = parts[3]
        alt = parts[4]
        qual = parts[5]
        filter_status = parts[6]
        info_str = parts[7]

        # Validate POS
        try:
            pos = int(pos_str)
        except ValueError:
            errors.append(f"Line {total_records}: Invalid POS '{pos_str}' — skipped")
            continue

        # Parse INFO
        info = parse_info_field(info_str)

        # Extract rsID
        rsid = None
        if id_col and id_col.startswith("rs"):
            rsid = id_col
        elif "RS" in info:
            rsid = f"rs{info['RS']}"

        # Extract gene and star allele
        gene = info.get("GENE") or info.get("Gene")
        star_allele = info.get("STAR") or info.get("Star")

        # Extract genotype (columns 8 and 9 = FORMAT, SAMPLE)
        genotype = None
        if len(parts) >= 10:
            genotype = parse_genotype(parts[8], parts[9])

        variant = VCFVariant(
            chrom=chrom,
            pos=pos,
            rsid=rsid,
            ref=ref,
            alt=alt,
            qual=qual,
            filter_status=filter_status,
            gene=gene,
            star_allele=star_allele,
            genotype=genotype,
            raw_info=info
        )
        variants.append(variant)

    # Count pharmacogenomic variants
    pg_variants = [
        v for v in variants
        if (v.gene and v.gene.upper() in SUPPORTED_GENES)
        or (v.rsid and _is_known_pgx_rsid(v.rsid))
    ]

    return VCFParseResult(
        success=len(errors) < total_records,
        variants=variants,
        total_records=total_records,
        pharmacogenomic_variants=len(pg_variants),
        errors=errors,
        metadata=metadata
    )


def _is_known_pgx_rsid(rsid: str) -> bool:
    """Check if an rsID is in the known pharmacogenomic variant set."""
    from src.models.pgx_knowledge import KNOWN_PGX_RSIDS
    return rsid in KNOWN_PGX_RSIDS