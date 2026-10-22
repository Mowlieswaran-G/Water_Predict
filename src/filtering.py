"""
filtering.py
============
Filter records by district, station, date, and parameter.

All functions work only on real data — they never invent rows.
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# District / Station filters
# ---------------------------------------------------------------------------

def filter_by_district(
    df: pd.DataFrame,
    district_col: str,
    district: str,
) -> pd.DataFrame:
    """Return rows whose district column matches *district* (case-insensitive)."""
    if district_col not in df.columns:
        logger.warning("District column '%s' not found.", district_col)
        return df.iloc[0:0].copy()  # empty frame with same columns

    mask = df[district_col].str.lower() == district.lower()
    result = df[mask].copy()
    logger.info(
        "filter_by_district('%s'): %d → %d rows", district, len(df), len(result)
    )
    return result


def filter_by_station(
    df: pd.DataFrame,
    station_col: str,
    station: str,
) -> pd.DataFrame:
    """Return rows whose station column matches *station* (case-insensitive)."""
    if station_col not in df.columns:
        logger.warning("Station column '%s' not found.", station_col)
        return df.iloc[0:0].copy()

    mask = df[station_col].str.lower() == station.lower()
    result = df[mask].copy()
    logger.info(
        "filter_by_station('%s'): %d → %d rows", station, len(df), len(result)
    )
    return result


# ---------------------------------------------------------------------------
# Parameter selection
# ---------------------------------------------------------------------------

def get_measurement_columns(
    df: pd.DataFrame,
    exclude_cols: list[str],
) -> list[str]:
    """
    Return columns that could be water-quality parameters.

    Excludes:
    - Columns listed in *exclude_cols* (e.g. district, station, date)
    - Completely empty columns
    - Non-numeric columns (unless they look like coded values)

    Only includes columns that have at least ONE non-null numeric value.
    """
    candidates = []
    for col in df.columns:
        if col in exclude_cols:
            continue
        if df[col].isna().all():
            continue
        # Try numeric conversion
        numeric = pd.to_numeric(df[col], errors="coerce")
        if numeric.notna().any():
            candidates.append(col)
    return candidates


def filter_by_parameter(
    df: pd.DataFrame,
    parameter_col: str,
    parameter: str,
) -> pd.DataFrame:
    """
    Return rows for a single parameter when the data is in long/tidy format.

    For wide-format CSVs (one column per parameter) this is not needed;
    use column selection instead.
    """
    if parameter_col not in df.columns:
        return df.iloc[0:0].copy()
    mask = df[parameter_col].str.lower() == parameter.lower()
    return df[mask].copy()


def select_parameter_columns(
    df: pd.DataFrame,
    selected_params: list[str],
) -> pd.DataFrame:
    """
    For wide-format data: return a view with only the selected parameter columns
    plus any index/metadata columns that are already in df.
    """
    present = [p for p in selected_params if p in df.columns]
    return df[present].copy() if present else df.iloc[0:0].copy()


# ---------------------------------------------------------------------------
# Duplicate detection
# ---------------------------------------------------------------------------

def flag_duplicates(
    df: pd.DataFrame,
    key_cols: list[str],
) -> pd.DataFrame:
    """Add a boolean 'Is_Duplicate' column based on *key_cols*."""
    df = df.copy()
    subset = [c for c in key_cols if c in df.columns]
    if subset:
        df["Is_Duplicate"] = df.duplicated(subset=subset, keep="first")
    else:
        df["Is_Duplicate"] = False
    return df


# ---------------------------------------------------------------------------
# Missing-value summary
# ---------------------------------------------------------------------------

def missing_value_report(df: pd.DataFrame, param_cols: list[str]) -> pd.DataFrame:
    """
    Return a small summary DataFrame showing how many values are missing
    per parameter column.

    Columns: Parameter, Total_Rows, Non_Null, Missing, Pct_Missing
    """
    rows = []
    for col in param_cols:
        if col not in df.columns:
            continue
        total = len(df)
        non_null = int(df[col].notna().sum())
        missing = total - non_null
        pct = round(missing / total * 100, 1) if total > 0 else 0.0
        rows.append({
            "Parameter": col,
            "Total_Rows": total,
            "Non_Null": non_null,
            "Missing": missing,
            "Pct_Missing": pct,
        })
    return pd.DataFrame(rows)
