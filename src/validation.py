"""
validation.py
=============
Column-level validation, required-column checks, and input
sanitisation functions.

None of these functions invent values; they only check and flag problems.
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Column-presence validation
# ---------------------------------------------------------------------------

# These are the "nice to have" column groups — the real column names will be
# discovered from the actual CSV and mapped dynamically.  We list aliases so
# we can find the right column even if names differ slightly.
REQUIRED_COLUMN_ALIASES: dict[str, list[str]] = {
    "district":    ["district", "District", "DISTRICT", "dist"],
    "station":     ["station", "Station", "station_name", "Station_Name",
                    "STATION", "location", "Location"],
    "sample_date": ["date", "Date", "DATE", "sample_date", "Sample_Date",
                    "sampling_date", "Sampling_Date", "year", "Year", "YEAR"],
}


def find_column(df: pd.DataFrame, role: str) -> str | None:
    """
    Find the actual column name in *df* that plays the given *role*.

    Parameters
    ----------
    df   : the DataFrame to search
    role : one of 'district', 'station', 'sample_date'

    Returns
    -------
    str | None  – the column name if found, otherwise None
    """
    aliases = REQUIRED_COLUMN_ALIASES.get(role, [])
    lower_map = {c.lower(): c for c in df.columns}
    for alias in aliases:
        if alias in df.columns:
            return alias
        if alias.lower() in lower_map:
            return lower_map[alias.lower()]
    return None


def discover_column_roles(df: pd.DataFrame) -> dict[str, str | None]:
    """
    Return a mapping of role → actual column name for every known role.
    Roles with no matching column map to None.
    """
    return {role: find_column(df, role) for role in REQUIRED_COLUMN_ALIASES}


def validate_required_columns(df: pd.DataFrame) -> tuple[bool, list[str]]:
    """
    Check that the DataFrame has at least district and station columns.

    Returns
    -------
    (ok: bool, missing_roles: list[str])
        ok is True only when all critical columns are found.
    """
    critical = ["district", "station"]
    missing = [role for role in critical if find_column(df, role) is None]
    return (len(missing) == 0), missing


# ---------------------------------------------------------------------------
# Value-level validation
# ---------------------------------------------------------------------------

def validate_search_inputs(
    district: str | None,
    station: str | None,
) -> tuple[bool, str]:
    """
    Validate user-supplied search parameters.

    Returns
    -------
    (valid: bool, error_message: str)
    """
    if not district or district.strip() == "":
        return False, "Please select a district before searching."
    if not station or station.strip() == "":
        return False, "Please select or enter a sampling station."
    return True, ""


def validate_measurement_value(value) -> tuple[bool, str]:
    """
    Check whether a single measurement value is usable.

    Returns
    -------
    (valid: bool, display_value: str)
        If invalid, display_value is 'Not available'.
    """
    if value is None:
        return False, "Not available"
    try:
        val = float(value)
        if pd.isna(val):
            return False, "Not available"
        return True, str(val)
    except (TypeError, ValueError):
        if isinstance(value, str) and value.strip() == "":
            return False, "Not available"
        return False, "Not available"


def check_completely_empty_columns(df: pd.DataFrame) -> list[str]:
    """Return a list of column names where every row is NaN."""
    return [
        col for col in df.columns
        if df[col].isna().all()
    ]


def check_missing_summary(df: pd.DataFrame) -> pd.Series:
    """Return count of missing values per column, sorted descending."""
    return df.isnull().sum().sort_values(ascending=False)


# ---------------------------------------------------------------------------
# Source evidence validation
# ---------------------------------------------------------------------------

def has_source_evidence(row: pd.Series, url_cols: list[str]) -> bool:
    """Return True if *row* has at least one non-empty URL/source column."""
    for col in url_cols:
        if col in row.index:
            val = row[col]
            if pd.notna(val) and str(val).strip() not in ("", "nan"):
                return True
    return False


# ---------------------------------------------------------------------------
# Ward-match validation
# ---------------------------------------------------------------------------

def assess_ward_match(
    station: str,
    ward_input: str,
) -> dict[str, str]:
    """
    Determine whether a station can be matched to the requested ward.

    Because the current dataset does NOT contain verified ward-to-station
    mappings, this function always returns "Unverified" with an explanation.

    A future version could query a verified mapping table here.

    Returns
    -------
    dict with keys:
        status   – "Unverified" | "Verified" | "No match"
        message  – Human-readable explanation
    """
    if not ward_input or ward_input.strip() == "":
        return {
            "status": "Not requested",
            "message": "No ward was specified by the user.",
        }

    # No verified ward mapping exists in the current dataset.
    return {
        "status": "Unverified",
        "message": (
            f"The station '{station}' is in the same district as ward "
            f"'{ward_input}', but no verified official mapping links this "
            "station to that ward. Treat this as unverified proximity only."
        ),
    }
