"""
report_generator.py
===================
Create draft reports from search results.

Rules:
- Reports are DRAFT until explicitly approved by a human.
- Reports are labelled as groundwater reports, NOT drinking-water certificates.
- No invented data is added.
- Each report has a unique ID derived from timestamp + parameters.
"""

from __future__ import annotations
import hashlib
import logging
import uuid
from datetime import datetime

import pandas as pd

from .date_utils import today

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Report ID
# ---------------------------------------------------------------------------

def create_report_id(district: str, station: str) -> str:
    """
    Generate a short, reproducible-ish report ID.

    Format: WWQR-<timestamp>-<hash4>
    The hash is based on district+station to help identify duplicates.
    """
    seed = f"{district}|{station}|{datetime.utcnow().isoformat()}"
    h = hashlib.md5(seed.encode()).hexdigest()[:4].upper()
    ts = datetime.utcnow().strftime("%Y%m%d%H%M")
    return f"WWQR-{ts}-{h}"


# ---------------------------------------------------------------------------
# Draft report builder
# ---------------------------------------------------------------------------

def build_draft_report(
    report_id: str,
    district: str,
    station: str,
    ward_input: str,
    period: str,
    records: pd.DataFrame,
    param_cols: list[str],
    ward_match: dict,
    warnings: list[str],
    latest_date: str | None,
    period_empty: bool,
    total_found: int,
    period_found: int,
    parsed_date_col: str | None,
) -> dict:
    """
    Assemble a draft report dictionary.

    This dict is the single source of truth for the report preview
    and the approval workflow.
    """
    generated_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    # Measurement summary
    meas_summary = _measure_summary(records, param_cols)

    # Date range in the records
    date_range = _extract_date_range(records, parsed_date_col)

    # Source references
    source_refs = _build_source_refs(records)

    # Limitations
    limitations = _build_limitations(ward_match, period_empty, param_cols)

    report = {
        # ── Identification ──────────────────────────────────────────────────
        "Report_ID":          report_id,
        "Generated_At":       generated_at,
        "Report_Type":        "Groundwater Quality Report (NOT a drinking-water certificate)",

        # ── Search parameters ────────────────────────────────────────────────
        "State":              "Tamil Nadu",
        "District":           district,
        "Station":            station,
        "Ward_Input":         ward_input or "Not specified",
        "Period_Requested":   period,

        # ── Record counts ────────────────────────────────────────────────────
        "Total_Records_Found":  total_found,
        "Period_Records_Found": period_found,
        "Latest_Sample_Date":   latest_date or "Unknown",
        "Sample_Date_Range":    date_range,

        # ── Ward match ───────────────────────────────────────────────────────
        "Ward_Match_Status":  ward_match.get("status", "Unknown"),
        "Ward_Match_Message": ward_match.get("message", ""),

        # ── Measurement summary ──────────────────────────────────────────────
        "Measurement_Summary": meas_summary,

        # ── Warnings & limitations ───────────────────────────────────────────
        "Warnings":           warnings,
        "Limitations":        limitations,

        # ── Source references ────────────────────────────────────────────────
        "Source_References":  source_refs,

        # ── Approval ─────────────────────────────────────────────────────────
        "Approval_Status":    "DRAFT — awaiting human review",
        "Approved_By":        None,
        "Approved_At":        None,
        "Rejection_Reason":   None,
    }

    return report


# ---------------------------------------------------------------------------
# Export helpers
# ---------------------------------------------------------------------------

def report_to_dataframe(report: dict, records: pd.DataFrame) -> pd.DataFrame:
    """
    Convert the report dict + records into a single wide DataFrame
    suitable for CSV export.
    """
    meta_rows = []
    for key, val in report.items():
        if key == "Measurement_Summary":
            continue
        meta_rows.append({"Field": key, "Value": str(val)})
    meta_df = pd.DataFrame(meta_rows)

    # Blank separator row
    sep = pd.DataFrame([{"Field": "--- RECORDS ---", "Value": ""}])

    # Records (only use string representation to keep CSV clean)
    rec_df = records.copy().astype(str)

    # Stack meta + separator + records side by side (best effort)
    return pd.concat([meta_df, sep, rec_df], ignore_index=True)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _measure_summary(df: pd.DataFrame, param_cols: list[str]) -> list[dict]:
    rows = []
    for col in param_cols:
        if col not in df.columns:
            continue
        numeric = pd.to_numeric(df[col], errors="coerce")
        count = int(numeric.notna().sum())
        if count == 0:
            continue
        rows.append({
            "Parameter": col,
            "Count":     count,
            "Min":       round(float(numeric.min()), 4),
            "Max":       round(float(numeric.max()), 4),
            "Mean":      round(float(numeric.mean()), 4),
        })
    return rows


def _extract_date_range(df: pd.DataFrame, date_col: str | None) -> str:
    if not date_col or date_col not in df.columns:
        return "Unknown"
    valid = df[date_col].dropna()
    if valid.empty:
        return "Unknown"
    return f"{valid.min().date()} to {valid.max().date()}"


def _build_source_refs(df: pd.DataFrame) -> list[str]:
    refs = [
        "Dataset: Tamil Nadu Groundwater Quality (Cleaned CSV)",
        "Official Source: Central Ground Water Board (CGWB) — India",
        ("Data Type: Groundwater chemistry samples from monitoring wells. "
         "NOT verified treated drinking-water tap results."),
    ]
    # Include any URL column values if present
    url_cols = [c for c in df.columns if "url" in c.lower() or "link" in c.lower()]
    for col in url_cols:
        vals = df[col].dropna().unique()[:3]
        for v in vals:
            if str(v).strip() not in ("", "nan"):
                refs.append(f"Source URL: {v}")
    return refs


def _build_limitations(
    ward_match: dict,
    period_empty: bool,
    param_cols: list[str],
) -> list[str]:
    lims = [
        "This dataset contains groundwater monitoring samples, not "
        "municipal treated drinking-water test results.",
        "Ward-level verification is not supported by the current dataset. "
        "No station can be officially linked to a specific ward.",
        "These results do not constitute a ward drinking-water safety certificate.",
        "Do not use these results alone to assess tap-water safety.",
    ]
    if ward_match.get("status") == "Unverified":
        lims.append(
            "Ward match is unverified — the station is in the same district "
            "but has no official ward assignment in this dataset."
        )
    if period_empty:
        lims.append(
            "No records fall within the requested date period. "
            "Records shown may be outside the selected range."
        )
    if not param_cols:
        lims.append(
            "No usable numeric parameter columns were found for this selection."
        )
    return lims
