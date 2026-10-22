"""
test_normalization.py
=====================
TC3: Unit Normalization

Tests the unit conversion logic in src/normalization.py.

These tests use clearly labelled SYNTHETIC fixtures.
They are NOT official measurements — they exist only to verify math.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.normalization import (
    convert_unit,
    normalize_to_mg_per_L,
    normalize_to_ug_per_L,
    values_are_equivalent,
    ConversionResult,
)

# ── TC3 Core ──────────────────────────────────────────────────────────────────

class TestTC3UnitNormalization:
    """
    TC3 — Unit Normalization
    Synthetic test fixtures; NOT official measurements.
    """

    def test_1_mg_per_L_to_ug_per_L(self):
        """1 mg/L should equal 1000 µg/L — both are synthetic fixtures."""
        result = convert_unit(1.0, "mg/L", "µg/L", is_synthetic=True)
        assert result.ok, f"Conversion failed: {result.warning}"
        assert result.normalized_value == pytest.approx(1000.0, rel=1e-6)
        assert result.is_synthetic, "Must be flagged as synthetic"

    def test_1000_ug_per_L_to_mg_per_L(self):
        """1000 µg/L should equal 1 mg/L — both are synthetic fixtures."""
        result = convert_unit(1000.0, "µg/L", "mg/L", is_synthetic=True)
        assert result.ok, f"Conversion failed: {result.warning}"
        assert result.normalized_value == pytest.approx(1.0, rel=1e-6)
        assert result.is_synthetic, "Must be flagged as synthetic"

    def test_equivalent_values_normalize_equal(self):
        """
        TC3 requirement: 1 mg/L and 1000 µg/L represent the same amount.
        After normalization to a common unit they should be equal.
        """
        equal, msg = values_are_equivalent(
            val_a=1.0,    unit_a="mg/L",
            val_b=1000.0, unit_b="µg/L",
        )
        assert equal, f"Values should be equal but got: {msg}"

    def test_inequal_values_not_equal(self):
        """2 mg/L ≠ 1000 µg/L."""
        equal, msg = values_are_equivalent(2.0, "mg/L", 1000.0, "µg/L")
        assert not equal, f"Should be unequal but got: {msg}"

    def test_ug_spelling_variants(self):
        """Accept μg/L, µg/L, and ug/L as the same unit."""
        for unit in ["µg/L", "μg/L", "ug/L"]:
            result = convert_unit(1000.0, unit, "mg/L", is_synthetic=True)
            assert result.ok, f"Failed for unit spelling '{unit}': {result.warning}"
            assert result.normalized_value == pytest.approx(1.0)

    def test_same_unit_identity(self):
        """mg/L → mg/L should return same value."""
        result = convert_unit(5.5, "mg/L", "mg/L", is_synthetic=True)
        assert result.ok
        assert result.normalized_value == pytest.approx(5.5)

    def test_missing_value_returns_not_ok(self):
        """Missing value should fail gracefully, not crash."""
        result = convert_unit(None, "mg/L", "µg/L", is_synthetic=True)
        assert not result.ok
        assert result.normalized_value is None

    def test_ph_not_converted(self):
        """pH must NOT be treated as a concentration — conversion must fail."""
        result = convert_unit(7.0, "pH", "mg/L", is_synthetic=True)
        assert not result.ok
        assert "not a concentration" in result.warning.lower()

    def test_unknown_unit_flagged(self):
        """Unknown units must be flagged, not guessed."""
        result = convert_unit(5.0, "ppm_unknown", "mg/L", is_synthetic=True)
        assert not result.ok
        assert "unknown" in result.warning.lower()

    def test_normalize_to_mg_L_convenience(self):
        result = normalize_to_mg_per_L(500.0, "µg/L", is_synthetic=True)
        assert result.ok
        assert result.normalized_value == pytest.approx(0.5)

    def test_normalize_to_ug_L_convenience(self):
        result = normalize_to_ug_per_L(2.0, "mg/L", is_synthetic=True)
        assert result.ok
        assert result.normalized_value == pytest.approx(2000.0)

    def test_synthetic_flag_is_propagated(self):
        """The is_synthetic flag must always be returned as set."""
        r1 = convert_unit(1.0, "mg/L", "µg/L", is_synthetic=True)
        r2 = convert_unit(1.0, "mg/L", "µg/L", is_synthetic=False)
        assert r1.is_synthetic is True
        assert r2.is_synthetic is False
