"""
normalization.py
================
Unit conversion for water-quality concentration measurements.

Verified conversion rules (source: standard SI/chemistry conventions):
    1 mg/L  =  1 000 µg/L   (milligrams per litre to micrograms per litre)
    1 µg/L  =  0.001 mg/L   (micrograms per litre to milligrams per litre)

Rules that are NOT applied:
- pH is dimensionless — do NOT convert it as a concentration.
- Parameters with unknown or ambiguous units are flagged, not guessed.
- Different parameters are never compared as though they are the same.

Synthetic test fixtures (see tests/) are clearly marked and never
presented as real official measurements.
"""

from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Supported unit conversions
# ---------------------------------------------------------------------------

# Map (from_unit_normalised, to_unit_normalised) → scale_factor
_CONVERSION_TABLE: dict[tuple[str, str], float] = {
    ("mg/l",  "µg/l"):  1_000.0,
    ("mg/l",  "ug/l"):  1_000.0,
    ("mg/l",  "μg/l"):  1_000.0,
    ("µg/l",  "mg/l"):  0.001,
    ("ug/l",  "mg/l"):  0.001,
    ("μg/l",  "mg/l"):  0.001,
    # same-unit → identity
    ("mg/l",  "mg/l"):  1.0,
    ("µg/l",  "µg/l"): 1.0,
    ("ug/l",  "ug/l"):  1.0,
    ("μg/l",  "μg/l"): 1.0,
}

# Units that must NOT be converted as concentrations
_NON_CONCENTRATION_UNITS: set[str] = {"ph", "°c", "c", "ntu", "ecf", "ms/cm",
                                       "μs/cm", "us/cm", "s.u.", "su"}

# Canonical display names for units
_CANONICAL_UNIT: dict[str, str] = {
    "mg/l":  "mg/L",
    "µg/l":  "µg/L",
    "ug/l":  "µg/L",
    "μg/l":  "µg/L",
}


class ConversionResult:
    """Holds both the original and normalized measurement."""

    __slots__ = (
        "original_value", "original_unit",
        "normalized_value", "normalized_unit",
        "is_synthetic", "warning", "ok",
    )

    def __init__(
        self,
        original_value: float | None,
        original_unit: str,
        normalized_value: float | None,
        normalized_unit: str,
        is_synthetic: bool = False,
        warning: str = "",
        ok: bool = True,
    ):
        self.original_value  = original_value
        self.original_unit   = original_unit
        self.normalized_value = normalized_value
        self.normalized_unit  = normalized_unit
        self.is_synthetic    = is_synthetic
        self.warning         = warning
        self.ok              = ok

    def display(self) -> dict:
        return {
            "original_value":   self.original_value,
            "original_unit":    self.original_unit,
            "normalized_value": self.normalized_value,
            "normalized_unit":  self.normalized_unit,
            "is_synthetic":     self.is_synthetic,
            "warning":          self.warning,
            "conversion_ok":    self.ok,
        }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def convert_unit(
    value: float | None,
    from_unit: str,
    to_unit: str,
    is_synthetic: bool = False,
) -> ConversionResult:
    """
    Convert *value* from *from_unit* to *to_unit*.

    Parameters
    ----------
    value       : Numeric measurement (or None if missing)
    from_unit   : Source unit string (e.g. "mg/L", "µg/L")
    to_unit     : Target unit string
    is_synthetic: Set True for test fixtures — prevents display as real data

    Returns
    -------
    ConversionResult
    """
    # Handle missing value
    if value is None:
        return ConversionResult(
            None, from_unit, None, to_unit,
            is_synthetic=is_synthetic,
            warning="Value is missing — cannot convert.",
            ok=False,
        )

    from_key = from_unit.strip().lower()
    to_key   = to_unit.strip().lower()

    # Block non-concentration units
    if from_key in _NON_CONCENTRATION_UNITS or to_key in _NON_CONCENTRATION_UNITS:
        return ConversionResult(
            value, from_unit, None, to_unit,
            is_synthetic=is_synthetic,
            warning=(
                f"Unit '{from_unit}' is not a concentration unit. "
                "Unit conversion not applicable."
            ),
            ok=False,
        )

    # Unknown unit
    if (from_key, to_key) not in _CONVERSION_TABLE:
        return ConversionResult(
            value, from_unit, None, to_unit,
            is_synthetic=is_synthetic,
            warning=f"Unit unknown — comparison unavailable. ({from_unit} → {to_unit})",
            ok=False,
        )

    factor = _CONVERSION_TABLE[(from_key, to_key)]
    normalized = round(value * factor, 6)
    display_unit = _CANONICAL_UNIT.get(to_key, to_unit)

    return ConversionResult(
        original_value=value,
        original_unit=from_unit,
        normalized_value=normalized,
        normalized_unit=display_unit,
        is_synthetic=is_synthetic,
        ok=True,
    )


def normalize_to_mg_per_L(
    value: float | None,
    unit: str,
    is_synthetic: bool = False,
) -> ConversionResult:
    """Convenience: always convert to mg/L."""
    return convert_unit(value, unit, "mg/L", is_synthetic=is_synthetic)


def normalize_to_ug_per_L(
    value: float | None,
    unit: str,
    is_synthetic: bool = False,
) -> ConversionResult:
    """Convenience: always convert to µg/L."""
    return convert_unit(value, unit, "µg/L", is_synthetic=is_synthetic)


def values_are_equivalent(
    val_a: float | None, unit_a: str,
    val_b: float | None, unit_b: str,
    tolerance: float = 1e-6,
) -> tuple[bool, str]:
    """
    Return (True, explanation) when val_a in unit_a equals val_b in unit_b.

    Both values are normalized to mg/L before comparison.
    Returns (False, reason) when comparison is not possible.
    """
    r_a = normalize_to_mg_per_L(val_a, unit_a)
    r_b = normalize_to_mg_per_L(val_b, unit_b)

    if not r_a.ok:
        return False, f"Could not normalize first value: {r_a.warning}"
    if not r_b.ok:
        return False, f"Could not normalize second value: {r_b.warning}"

    equal = abs(r_a.normalized_value - r_b.normalized_value) <= tolerance
    msg = (
        f"{val_a} {unit_a} → {r_a.normalized_value} mg/L  |  "
        f"{val_b} {unit_b} → {r_b.normalized_value} mg/L  →  "
        f"{'EQUAL' if equal else 'NOT EQUAL'}"
    )
    return equal, msg


# ---------------------------------------------------------------------------
# Column-level helper (for DataFrames)
# ---------------------------------------------------------------------------

def add_normalized_column(
    df,
    value_col: str,
    unit_col: str | None,
    default_unit: str = "mg/L",
    target_unit: str = "mg/L",
) -> "pd.DataFrame":  # type: ignore[name-defined]
    """
    Add 'Normalized_Value' and 'Normalized_Unit' columns to *df*.

    If *unit_col* is None, uses *default_unit* for all rows.
    """
    import pandas as pd

    df = df.copy()
    results = []
    for _, row in df.iterrows():
        val = row.get(value_col)
        unit = row.get(unit_col, default_unit) if unit_col else default_unit
        if unit is None or (isinstance(unit, float) and pd.isna(unit)):
            unit = default_unit
        r = convert_unit(val, str(unit), target_unit)
        results.append((r.normalized_value, r.normalized_unit, r.warning))

    df["Normalized_Value"] = [r[0] for r in results]
    df["Normalized_Unit"]  = [r[1] for r in results]
    df["Conversion_Warning"] = [r[2] for r in results]
    return df
