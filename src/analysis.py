"""
analysis.py
===========
High-level analysis helpers that combine filtering, date parsing,
and parameter selection into one pipeline call.

These functions coordinate the other modules but never invent data.
"""

from __future__ import annotations
import logging
import pandas as pd

from . import data_loader, validation, filtering, date_utils, source_verification

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Column-role catalogue (discovered dynamically)
# ---------------------------------------------------------------------------

class DatasetProfile:
    """
    Holds discovered column roles for a loaded DataFrame.

    Created once and passed around instead of re-discovering columns
    on every call.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df
        roles = validation.discover_column_roles(df)
        self.district_col:    str | None = roles.get("district")
        self.station_col:     str | None = roles.get("station")
        self.date_col_raw:    str | None = roles.get("sample_date")

        # Parsed date column name (added later)
        self.date_col_parsed: str | None = None

        # Parameter columns (numeric, non-empty)
        meta_cols = [c for c in [
            self.district_col, self.station_col, self.date_col_raw
        ] if c]
        self.param_cols: list[str] = filtering.get_measurement_columns(
            df, exclude_cols=meta_cols
        )

        # Provenance
        self.provenance_cols = source_verification.discover_provenance_columns(df)

        # Inspection summary
        insp = data_loader.inspect_dataset(df)
        self.completely_empty_cols: list[str] = insp["completely_empty_columns"]
        self.total_rows: int = insp["total_rows"]

    def parse_dates(self) -> None:
        """Parse the raw date column in-place and add a '_parsed' column."""
        if self.date_col_raw and self.date_col_raw in self.df.columns:
            parsed_name = self.date_col_raw + "_parsed"
            self.df[parsed_name] = date_utils.parse_date_column(
                self.df[self.date_col_raw]
            )
            self.date_col_parsed = parsed_name
            logger.info(
                "Parsed dates: %d valid, %d NaT",
                self.df[parsed_name].notna().sum(),
                self.df[parsed_name].isna().sum(),
            )


# ---------------------------------------------------------------------------
# Main search pipeline
# ---------------------------------------------------------------------------

def run_search(
    profile: DatasetProfile,
    district: str,
    station: str,
    ward_input: str,
    period: str,
    selected_params: list[str],
    custom_start=None,
    custom_end=None,
) -> dict:
    """
    Execute the full search pipeline and return a result bundle.

    Returns a dict with keys:
        records         – filtered DataFrame (may be empty)
        total_found     – int
        period_found    – int (records matching the period)
        period_empty    – bool
        warnings        – list[str]
        ward_match      – dict (status + message)
        param_cols_used – list[str]
        latest_date     – str | None
    """
    warnings: list[str] = []

    # Step 1: Filter by district
    df = filtering.filter_by_district(
        profile.df, profile.district_col or "district", district
    )
    if df.empty:
        warnings.append(f"No records found for district '{district}'.")
        return _empty_result(warnings, ward_input, station)

    # Step 2: Filter by station
    df = filtering.filter_by_station(
        df, profile.station_col or "station", station
    )
    if df.empty:
        warnings.append(
            f"No records found for station '{station}' in district '{district}'."
        )
        return _empty_result(warnings, ward_input, station)

    total_found = len(df)

    # Step 3: Parse dates
    if profile.date_col_raw and profile.date_col_raw in df.columns:
        parsed_col = profile.date_col_raw + "_parsed"
        df[parsed_col] = date_utils.parse_date_column(df[profile.date_col_raw])
        unparseable = df[parsed_col].isna().sum()
        if unparseable:
            warnings.append(
                f"⚠️ {unparseable} row(s) have unparseable dates and are "
                "shown with 'Date unknown'."
            )
    else:
        parsed_col = None
        warnings.append(
            "⚠️ No date column was found. Date filtering and historical "
            "labelling are unavailable."
        )

    # Step 4: Historical labels
    if parsed_col and parsed_col in df.columns:
        df = date_utils.add_historical_column(df, parsed_col)
    else:
        df["Is_Historical"] = None
        df["Age_Label"] = "Date unknown"

    # Step 5: Date-period filter
    period_df = df
    period_found = total_found
    period_empty = False

    if parsed_col and parsed_col in df.columns and period != "All available":
        period_df = date_utils.filter_by_period(
            df, parsed_col, period, custom_start, custom_end
        )
        period_found = len(period_df)
        if period_found == 0:
            period_empty = True
            warnings.append(
                f"⚠️ No samples were found within the selected period "
                f"('{period}'). "
                f"{total_found} older record(s) exist outside this range — "
                "broaden the date range to see them."
            )
            period_df = df  # show ALL records with a warning rather than nothing

    # Step 6: Parameter column selection
    if selected_params and selected_params != ["All parameters"]:
        param_cols_used = [p for p in selected_params if p in profile.param_cols]
    else:
        param_cols_used = profile.param_cols

    # Step 7: Ward match assessment
    ward_match = validation.assess_ward_match(station, ward_input)
    if ward_match["status"] == "Unverified" and ward_input.strip():
        warnings.append(
            f"⚠️ Ward match UNVERIFIED: {ward_match['message']}"
        )

    # Step 8: Latest date
    latest_date = None
    if parsed_col and parsed_col in period_df.columns:
        valid_dates = period_df[parsed_col].dropna()
        if not valid_dates.empty:
            latest_date = str(valid_dates.max().date())

    return {
        "records":          period_df,
        "total_found":      total_found,
        "period_found":     period_found,
        "period_empty":     period_empty,
        "warnings":         warnings,
        "ward_match":       ward_match,
        "param_cols_used":  param_cols_used,
        "latest_date":      latest_date,
        "parsed_date_col":  parsed_col,
    }


def _empty_result(warnings: list[str], ward_input: str, station: str) -> dict:
    """Return a standard empty result bundle."""
    ward_match = validation.assess_ward_match(station, ward_input)
    return {
        "records":         pd.DataFrame(),
        "total_found":     0,
        "period_found":    0,
        "period_empty":    True,
        "warnings":        warnings,
        "ward_match":      ward_match,
        "param_cols_used": [],
        "latest_date":     None,
        "parsed_date_col": None,
    }


# ---------------------------------------------------------------------------
# Measurement summary
# ---------------------------------------------------------------------------

def summarise_measurements(
    df: pd.DataFrame,
    param_cols: list[str],
) -> pd.DataFrame:
    """
    Return a summary table (mean, min, max, count) for each parameter.

    Completely empty columns are excluded.
    """
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
            "Missing":   int(numeric.isna().sum()),
        })
    return pd.DataFrame(rows)
