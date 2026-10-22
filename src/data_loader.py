"""
data_loader.py
==============
Responsible for loading the CSV file, inspecting its structure,
and returning clean DataFrames to the rest of the application.

Key rules:
- Never invent records.
- Never silently substitute a missing file with fake data.
- Always preserve the original columns.
"""

import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)

# Expected location of the CSV files
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CSV_FILENAME = "tamil_nadu_groundwater_quality_cleaned.csv"
CSV_PATH = os.path.join(DATA_DIR, CSV_FILENAME)

CLEANED_CSV_PATH = CSV_PATH
RAW_CSV_PATH = os.path.join(DATA_DIR, "tamil_nadu_groundwater_quality_raw.csv")
ULB_CSV_PATH = os.path.join(DATA_DIR, "tamil_nadu_ulb_wards.csv")


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_csv_path() -> str:
    """Return the absolute path to the dataset file."""
    return CSV_PATH


def file_exists() -> bool:
    """Return True if the cleaned CSV file is present on disk."""
    return os.path.isfile(CSV_PATH)


def raw_file_exists() -> bool:
    """Return True if the raw CSV file is present on disk."""
    return os.path.isfile(RAW_CSV_PATH)


def ulb_file_exists() -> bool:
    """Return True if the ULB wards CSV file is present on disk."""
    return os.path.isfile(ULB_CSV_PATH)


def load_csv(path: str | None = None) -> pd.DataFrame:
    """
    Load the CSV and return a DataFrame.

    Parameters
    ----------
    path : str, optional
        Override the default CSV path (useful in tests).

    Returns
    -------
    pd.DataFrame
        Raw DataFrame with all original columns preserved.

    Raises
    ------
    FileNotFoundError
        When the CSV is missing from the expected location.
    ValueError
        When the CSV file is empty or completely unparseable.
    """
    target = path or CSV_PATH

    if not os.path.isfile(target):
        raise FileNotFoundError(
            f"Dataset not found at: {target}\n"
            "Please place 'tamil_nadu_groundwater_quality_cleaned.csv' "
            "inside the 'data/' folder and restart the application."
        )

    try:
        df = pd.read_csv(target, low_memory=False)
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"The CSV file is empty: {target}") from exc
    except Exception as exc:
        raise ValueError(f"Could not read CSV ({target}): {exc}") from exc

    if df.empty:
        raise ValueError(f"The CSV file contains no data rows: {target}")

    # Strip leading/trailing whitespace from all string columns
    df = _strip_whitespace(df)

    logger.info("Loaded %d rows × %d columns from %s", len(df), len(df.columns), target)
    return df


def _strip_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    """Strip leading/trailing spaces from string column names and values."""
    df.columns = [c.strip() for c in df.columns]
    for col in df.select_dtypes(include=["object", "string"]).columns:
        if df[col].dtype == "object" or str(df[col].dtype).startswith("str"):
            df[col] = df[col].astype(str).str.strip()
    return df


# ---------------------------------------------------------------------------
# Inspection helpers (called once at startup)
# ---------------------------------------------------------------------------

def inspect_dataset(df: pd.DataFrame) -> dict:
    """
    Summarise the dataset structure for display in the UI.

    Returns a dict with:
        total_rows, total_columns, columns, missing_counts,
        completely_empty_columns, non_empty_columns,
        sample_districts, sample_stations
    """
    missing = df.isnull().sum()
    completely_empty = missing[missing == len(df)].index.tolist()
    non_empty = [c for c in df.columns if c not in completely_empty]

    # Try to pull a handful of district / station values for display
    district_col = _find_column(df, ["district", "District", "DISTRICT"])
    station_col = _find_column(df, ["station", "Station", "STATION",
                                    "station_name", "Station_Name"])

    sample_districts: list[str] = []
    sample_stations: list[str] = []

    if district_col:
        sample_districts = (
            df[district_col].dropna().unique().tolist()[:20]
        )
    if station_col:
        sample_stations = (
            df[station_col].dropna().unique().tolist()[:20]
        )

    return {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": df.columns.tolist(),
        "missing_counts": missing.to_dict(),
        "completely_empty_columns": completely_empty,
        "non_empty_columns": non_empty,
        "sample_districts": sample_districts,
        "sample_stations": sample_stations,
        "district_column": district_col,
        "station_column": station_col,
    }


def get_districts(df: pd.DataFrame, district_col: str) -> list[str]:
    """Return a sorted list of unique district names from the DataFrame."""
    if district_col not in df.columns:
        return []
    return sorted(df[district_col].dropna().unique().tolist())


def get_stations_for_district(
    df: pd.DataFrame,
    district_col: str,
    station_col: str,
    district: str,
) -> list[str]:
    """Return sorted station names that belong to the given district."""
    if district_col not in df.columns or station_col not in df.columns:
        return []
    mask = df[district_col].str.lower() == district.lower()
    return sorted(df.loc[mask, station_col].dropna().unique().tolist())


# ---------------------------------------------------------------------------
# Internal utility
# ---------------------------------------------------------------------------

def _find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Return the first candidate column name that exists in the DataFrame."""
    for name in candidates:
        if name in df.columns:
            return name
    # Case-insensitive fallback
    lower_map = {c.lower(): c for c in df.columns}
    for name in candidates:
        if name.lower() in lower_map:
            return lower_map[name.lower()]
    return None


# ---------------------------------------------------------------------------
# Raw groundwater dataset and ULB wards loaders
# ---------------------------------------------------------------------------

def load_raw_csv(path: str | None = None) -> pd.DataFrame:
    """
    Load the raw CGWB groundwater quality CSV and return a DataFrame.
    """
    target = path or RAW_CSV_PATH
    if not os.path.isfile(target):
        raise FileNotFoundError(f"Raw dataset not found at: {target}")

    try:
        df = pd.read_csv(target, low_memory=False)
    except Exception as exc:
        raise ValueError(f"Could not read raw CSV ({target}): {exc}") from exc

    if df.empty:
        raise ValueError(f"The raw CSV file contains no data rows: {target}")

    return _strip_whitespace(df)


def load_ulb_wards(path: str | None = None) -> pd.DataFrame:
    """
    Load the Tamil Nadu ULB Wards dataset (125 municipalities).
    """
    target = path or ULB_CSV_PATH
    if not os.path.isfile(target):
        raise FileNotFoundError(f"ULB wards dataset not found at: {target}")

    try:
        df = pd.read_csv(target, low_memory=False)
    except Exception as exc:
        raise ValueError(f"Could not read ULB CSV ({target}): {exc}") from exc

    if df.empty:
        raise ValueError(f"The ULB CSV file contains no data rows: {target}")

    return _strip_whitespace(df)


def get_ulb_list(path: str | None = None) -> list[dict]:
    """
    Return a clean list of ULB dictionaries sorted alphabetically by name.
    Each item contains name, grade, total_wards, council_general, council_sc,
    council_st, council_women.
    """
    df = load_ulb_wards(path)
    ulbs = []
    for _, row in df.iterrows():
        ulb_name = str(row.get("Name of the ULB", "")).strip()
        if not ulb_name:
            continue
        grade = str(row.get("Grade", "")).strip()

        try:
            total_wards = int(row.get("Total No. of Wards", 0))
        except (ValueError, TypeError):
            total_wards = 0

        def _safe_int(val):
            if pd.isna(val) or str(val).strip().upper() in ("NA", "NAN", ""):
                return None
            try:
                return int(float(val))
            except (ValueError, TypeError):
                return None

        ulbs.append({
            "name": ulb_name,
            "grade": grade,
            "total_wards": total_wards,
            "council_general": _safe_int(row.get("Strength of the Council-General")),
            "council_sc": _safe_int(row.get("Strength of the Council-Reserved for-SC")),
            "council_st": _safe_int(row.get("Strength of the Council-Reserved for-ST")),
            "council_women": _safe_int(row.get("Strength of the Council-Reserved for-Women")),
        })

    ulbs.sort(key=lambda x: x["name"].lower())
    return ulbs


def get_ulb_details(ulb_name: str, path: str | None = None) -> dict | None:
    """
    Find detailed ULB metadata by municipality name (case-insensitive).
    """
    if not ulb_name:
        return None
    target = ulb_name.strip().lower()
    for item in get_ulb_list(path):
        if item["name"].lower() == target:
            return item
    return None

