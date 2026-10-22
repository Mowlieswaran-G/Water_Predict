"""
source_verification.py
======================
Manage provenance information for every displayed record.

This module:
- Retains all original source columns present in the CSV.
- Clearly states what IS and what IS NOT available as evidence.
- Never invents report IDs, URLs, or laboratory names.
- Shows users exactly which facts came from the dataset vs. computation.
"""

from __future__ import annotations
import logging
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Known provenance column aliases
# ---------------------------------------------------------------------------

PROVENANCE_ALIASES: dict[str, list[str]] = {
    "source_dataset":   ["source", "Source", "dataset", "Dataset",
                         "data_source", "Data_Source"],
    "source_url":       ["url", "URL", "link", "Link", "source_url",
                         "Source_URL", "reference", "Reference"],
    "station_id":       ["station_id", "Station_ID", "site_id", "Site_ID",
                         "location_id", "Location_ID"],
    "sample_id":        ["sample_id", "Sample_ID", "sample_no", "Sample_No"],
    "lab_name":         ["lab", "Lab", "laboratory", "Laboratory",
                         "lab_name", "Lab_Name"],
    "document_page":    ["page", "Page", "doc_page", "Doc_Page"],
    "retrieval_date":   ["retrieval_date", "Retrieval_Date", "accessed",
                         "Accessed"],
}

# Fixed provenance fields that are always the same for this dataset
DATASET_PROVENANCE = {
    "Dataset_Name":   "Tamil Nadu Groundwater Quality (Cleaned CSV)",
    "Official_Source": "Central Ground Water Board (CGWB) — India",
    "Data_Type":       (
        "Groundwater chemistry samples from monitoring wells. "
        "NOT verified treated drinking-water tap results."
    ),
    "Ward_Mapping":    (
        "No verified ward-to-station mapping is present in this dataset. "
        "Ward matches are unverified proximity associations only."
    ),
}


# ---------------------------------------------------------------------------
# Column discovery
# ---------------------------------------------------------------------------

def discover_provenance_columns(df: pd.DataFrame) -> dict[str, str | None]:
    """
    Return a mapping {role: actual_column_name} for provenance columns.

    Missing roles map to None.
    """
    lower_map = {c.lower(): c for c in df.columns}
    found: dict[str, str | None] = {}
    for role, aliases in PROVENANCE_ALIASES.items():
        matched = None
        for alias in aliases:
            if alias in df.columns:
                matched = alias
                break
            if alias.lower() in lower_map:
                matched = lower_map[alias.lower()]
                break
        found[role] = matched
    return found


# ---------------------------------------------------------------------------
# Evidence builder
# ---------------------------------------------------------------------------

def build_evidence_record(
    row: pd.Series,
    provenance_cols: dict[str, str | None],
) -> dict[str, str]:
    """
    Build a source-evidence dictionary for a single data row.

    Returns a flat dict with both fixed provenance facts and any
    dynamic values found in the row's provenance columns.
    """
    evidence: dict[str, str] = {}

    # Fixed / always-present facts
    evidence.update(DATASET_PROVENANCE)

    # Dynamic: pull actual values from the row
    for role, col in provenance_cols.items():
        if col and col in row.index:
            val = row[col]
            if pd.notna(val) and str(val).strip() not in ("", "nan"):
                evidence[role] = str(val)
            else:
                evidence[role] = "Not available in dataset"
        else:
            evidence[role] = "Not available in dataset"

    # Explicit note about individual lab reports
    if evidence.get("source_url") == "Not available in dataset":
        evidence["Individual_Lab_Report"] = (
            "No individual laboratory report link is available in the "
            "provided CSV file. The record originates from the bulk "
            "dataset listed under Dataset_Name above."
        )

    return evidence


def format_evidence_for_display(evidence: dict[str, str]) -> str:
    """Format evidence dict as a readable multi-line string."""
    lines = ["**Source Evidence**", ""]
    for key, val in evidence.items():
        label = key.replace("_", " ").title()
        lines.append(f"- **{label}:** {val}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Validation helper
# ---------------------------------------------------------------------------

def validate_source_fields(evidence: dict[str, str]) -> list[str]:
    """
    Return a list of warnings about missing provenance fields.

    These are informational — missing evidence does not make data invalid,
    but the user must know what is absent.
    """
    warnings = []
    critical = ["source_url", "station_id", "sample_id"]
    for field in critical:
        if evidence.get(field, "Not available in dataset") == "Not available in dataset":
            warnings.append(
                f"⚠️  '{field.replace('_', ' ').title()}' is not available "
                "in the provided dataset."
            )
    return warnings
