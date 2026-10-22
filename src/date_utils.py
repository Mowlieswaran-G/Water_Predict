"""
date_utils.py
=============
Parse sample dates, calculate sample age, and label historical samples.

Rules:
- Use the real system date — never a hardcoded date.
- If a date cannot be parsed, flag it rather than guess.
- A sample is "Historical" when it is older than HISTORICAL_THRESHOLD_DAYS.
"""

import logging
from datetime import date, datetime, timedelta
import pandas as pd

logger = logging.getLogger(__name__)

# A sample older than this many days is labelled "Historical"
HISTORICAL_THRESHOLD_DAYS = 365  # 1 year


# ---------------------------------------------------------------------------
# Core date parsing
# ---------------------------------------------------------------------------

def parse_date_column(series: pd.Series) -> pd.Series:
    """
    Convert a raw date column to pandas datetime (UTC-naive).

    Handles:
    - Standard date strings (YYYY-MM-DD, DD/MM/YYYY, etc.)
    - 4-digit year-only values (e.g. 2019 → 2019-01-01)
    - Already-numeric years stored as int/float

    Values that cannot be parsed are returned as NaT (Not a Time).
    We never guess or invent a date.
    """
    def _parse_one(val):
        if pd.isna(val):
            return pd.NaT
        s = str(val).strip()
        # Year-only: 4-digit integer string
        if s.isdigit() and len(s) == 4:
            try:
                return pd.Timestamp(f"{s}-01-01")
            except Exception:
                return pd.NaT
        # Try multiple explicit formats (ISO first to avoid day/month ambiguity)
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y",
                    "%m/%d/%Y", "%d-%b-%Y", "%Y"):
            try:
                return pd.to_datetime(s, format=fmt)
            except Exception:
                continue
        # Last-resort generic parser (no dayfirst to avoid ambiguity)
        try:
            return pd.to_datetime(s)
        except Exception:
            pass
        logger.debug("Could not parse date value: %r", val)
        return pd.NaT

    return series.apply(_parse_one)


def today() -> date:
    """Return today's date (real system date, not hardcoded)."""
    return datetime.now().date()


def sample_age_days(sample_date: date | datetime | pd.Timestamp) -> int | None:
    """
    Return how many days old a sample is relative to today.

    Returns None if sample_date is None / NaT.
    """
    if sample_date is None or pd.isna(sample_date):
        return None
    t = today()
    if isinstance(sample_date, pd.Timestamp):
        sample_date = sample_date.date()
    elif isinstance(sample_date, datetime):
        sample_date = sample_date.date()
    return (t - sample_date).days


def is_historical(sample_date, threshold_days: int = HISTORICAL_THRESHOLD_DAYS) -> bool | None:
    """
    Return True when the sample is older than threshold_days.

    Returns None when the date is unknown.
    """
    age = sample_age_days(sample_date)
    if age is None:
        return None
    return age > threshold_days


def historical_label(sample_date, threshold_days: int = HISTORICAL_THRESHOLD_DAYS) -> str:
    """
    Return a human-readable age label for a sample.

    Possible returns:
        "Date unknown"
        "Recent  (within last year)"
        "Historical  (collected X days ago)"
    """
    age = sample_age_days(sample_date)
    if age is None:
        return "Date unknown"
    if age <= threshold_days:
        return f"Recent  (within last {threshold_days} days)"
    return f"Historical  (collected {age} days ago)"


# ---------------------------------------------------------------------------
# Filtering helpers
# ---------------------------------------------------------------------------

def filter_by_period(
    df: pd.DataFrame,
    date_col: str,
    period: str,
    custom_start: date | None = None,
    custom_end: date | None = None,
) -> pd.DataFrame:
    """
    Filter DataFrame rows whose *date_col* falls within the chosen period.

    Parameters
    ----------
    df          : DataFrame with a parsed datetime column
    date_col    : name of the datetime column
    period      : "Last 30 days" | "Last 6 months" | "Last 1 year" | "Custom"
    custom_start: used when period == "Custom"
    custom_end  : used when period == "Custom"

    Returns
    -------
    Filtered DataFrame — may be empty if no rows match.
    """
    t = today()

    if period == "Last 30 days":
        cutoff = t - timedelta(days=30)
        start, end = cutoff, t
    elif period == "Last 6 months":
        cutoff = t - timedelta(days=183)
        start, end = cutoff, t
    elif period == "Last 1 year":
        cutoff = t - timedelta(days=365)
        start, end = cutoff, t
    elif period == "Custom":
        start = custom_start or (t - timedelta(days=365))
        end = custom_end or t
    else:
        # All available records
        return df.copy()

    mask = (
        df[date_col].notna()
        & (df[date_col].dt.date >= start)
        & (df[date_col].dt.date <= end)
    )
    return df[mask].copy()


def add_historical_column(
    df: pd.DataFrame,
    date_col: str,
    threshold_days: int = HISTORICAL_THRESHOLD_DAYS,
) -> pd.DataFrame:
    """
    Add a 'Historical' boolean column and a 'Age_Label' string column
    to the DataFrame based on the parsed date column.
    """
    df = df.copy()
    df["Is_Historical"] = df[date_col].apply(
        lambda d: is_historical(d, threshold_days)
    )
    df["Age_Label"] = df[date_col].apply(
        lambda d: historical_label(d, threshold_days)
    )
    return df
