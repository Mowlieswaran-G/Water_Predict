"""
test_validation.py
==================
Tests for src/validation.py

Covers:
- Column discovery
- Search input validation
- Measurement value validation
- Empty-column detection
- Ward match assessment
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import pandas as pd

from src.validation import (
    find_column,
    discover_column_roles,
    validate_required_columns,
    validate_search_inputs,
    validate_measurement_value,
    check_completely_empty_columns,
    assess_ward_match,
)


class TestFindColumn:
    def test_finds_exact_match(self):
        df = pd.DataFrame(columns=["District", "Station", "Year"])
        assert find_column(df, "district") == "District"

    def test_finds_case_insensitive(self):
        df = pd.DataFrame(columns=["DISTRICT", "station_name"])
        assert find_column(df, "district") == "DISTRICT"
        assert find_column(df, "station") == "station_name"

    def test_returns_none_when_missing(self):
        df = pd.DataFrame(columns=["foo", "bar"])
        assert find_column(df, "district") is None

    def test_finds_date_aliases(self):
        df = pd.DataFrame(columns=["Year", "Location"])
        assert find_column(df, "sample_date") == "Year"


class TestValidateRequiredColumns:
    def test_all_present(self):
        df = pd.DataFrame(columns=["District", "Station", "Year", "pH"])
        ok, missing = validate_required_columns(df)
        assert ok is True
        assert missing == []

    def test_district_missing(self):
        df = pd.DataFrame(columns=["Station", "Year"])
        ok, missing = validate_required_columns(df)
        assert ok is False
        assert "district" in missing

    def test_station_missing(self):
        df = pd.DataFrame(columns=["District", "Year"])
        ok, missing = validate_required_columns(df)
        assert ok is False
        assert "station" in missing

    def test_both_missing(self):
        df = pd.DataFrame(columns=["Year", "pH", "EC"])
        ok, missing = validate_required_columns(df)
        assert ok is False
        assert len(missing) == 2


class TestValidateSearchInputs:
    def test_valid_inputs(self):
        ok, err = validate_search_inputs("Chennai", "Well_001")
        assert ok is True
        assert err == ""

    def test_empty_district(self):
        ok, err = validate_search_inputs("", "Well_001")
        assert ok is False
        assert "district" in err.lower()

    def test_none_district(self):
        ok, err = validate_search_inputs(None, "Well_001")
        assert ok is False

    def test_empty_station(self):
        ok, err = validate_search_inputs("Chennai", "")
        assert ok is False
        assert "station" in err.lower()

    def test_whitespace_only(self):
        ok, err = validate_search_inputs("   ", "Well")
        assert ok is False

    def test_both_empty(self):
        ok, err = validate_search_inputs("", "")
        assert ok is False


class TestValidateMeasurementValue:
    def test_valid_float(self):
        valid, disp = validate_measurement_value(7.5)
        assert valid is True
        assert "7.5" in disp

    def test_valid_string_float(self):
        valid, disp = validate_measurement_value("3.14")
        assert valid is True

    def test_none_is_not_available(self):
        valid, disp = validate_measurement_value(None)
        assert valid is False
        assert disp == "Not available"

    def test_nan_is_not_available(self):
        valid, disp = validate_measurement_value(float("nan"))
        assert valid is False
        assert disp == "Not available"

    def test_empty_string_is_not_available(self):
        valid, disp = validate_measurement_value("")
        assert valid is False
        assert disp == "Not available"

    def test_nonnumeric_string_is_not_available(self):
        valid, disp = validate_measurement_value("N/D")
        assert valid is False
        assert disp == "Not available"

    def test_zero_is_valid(self):
        """Zero is a real measurement — not the same as missing."""
        valid, disp = validate_measurement_value(0.0)
        assert valid is True


class TestCheckCompletelyEmptyColumns:
    def test_empty_column_detected(self):
        df = pd.DataFrame({
            "A": [1, 2, 3],
            "B": [None, None, None],
            "C": ["x", "y", "z"],
        })
        empties = check_completely_empty_columns(df)
        assert "B" in empties
        assert "A" not in empties
        assert "C" not in empties

    def test_no_empty_columns(self):
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        assert check_completely_empty_columns(df) == []


class TestAssessWardMatch:
    def test_no_ward_input_is_not_requested(self):
        result = assess_ward_match("Well_001", "")
        assert result["status"] == "Not requested"

    def test_ward_input_is_unverified(self):
        """
        TC1 & TC4: Ward match must never be silently claimed as verified
        when no official mapping exists.
        """
        result = assess_ward_match("Some_Station", "Ward 5")
        assert result["status"] == "Unverified"
        assert "unverified" in result["message"].lower() or "no verified" in result["message"].lower()

    def test_ward_message_explains_reason(self):
        result = assess_ward_match("Station_A", "Ward 12")
        assert len(result["message"]) > 10  # meaningful explanation
