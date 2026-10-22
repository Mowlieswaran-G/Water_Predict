"""
test_scenarios.py
=================
The four required test cases (TC1–TC4) plus extra edge-case tests.

TC1 — Ward selected           → unverified match or no data
TC2 — Historical sample       → labelled, actual date shown (see test_dates.py too)
TC3 — Unit normalization      → equal values after normalization (see test_normalization.py)
TC4 — No sample for ward      → correct no-data message, no invented data
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import pandas as pd
from datetime import date, timedelta
from unittest.mock import patch

from src import validation, filtering, date_utils, analysis
from src.normalization import values_are_equivalent

FAKE_TODAY = date(2024, 6, 1)

# ---------------------------------------------------------------------------
# Helpers: build small synthetic DataFrames (for testing only)
# ---------------------------------------------------------------------------

def _make_sample_df():
    """
    A minimal DataFrame that mimics a real CSV structure.
    Clearly labelled as a test fixture — NOT an official dataset.
    """
    return pd.DataFrame({
        "District":     ["Chennai", "Chennai", "Madurai"],
        "Station":      ["Station_A", "Station_A", "Station_B"],
        "Year":         ["2022", "2024", "2019"],
        "pH":           [7.2, 8.0, 6.9],
        "EC":           [450.0, None, 820.0],
        "TDS":          [300.0, 520.0, None],
    })


# ===========================================================================
# TC1 — Ward Selected
# ===========================================================================

class TestTC1WardSelected:
    """
    TC1: User selects a district and a ward identifier.
    Expected: if no verified ward mapping exists, show Unverified.
    """

    def test_ward_match_is_unverified_when_no_mapping(self):
        """
        No official ward-to-station mapping is in the dataset.
        The application must return Unverified, not silently claim a match.
        """
        result = validation.assess_ward_match("Station_A", "Ward 7")
        assert result["status"] == "Unverified", (
            f"Expected 'Unverified', got '{result['status']}'"
        )

    def test_unverified_message_is_informative(self):
        result = validation.assess_ward_match("Station_A", "Ward 7")
        assert len(result.get("message", "")) > 20

    def test_station_in_district_does_not_imply_ward(self):
        """
        Fact: a station being in the same district as a ward does NOT mean
        the station is the ward's official sampling point.
        This test ensures the function never returns 'Verified' without a mapping.
        """
        result = validation.assess_ward_match("Some_Monitoring_Well", "Ward 3")
        assert result["status"] != "Verified", (
            "Should never be Verified without an official mapping table"
        )

    def test_no_ward_input_is_not_requested(self):
        result = validation.assess_ward_match("Station_A", "")
        assert result["status"] == "Not requested"


# ===========================================================================
# TC2 — Historical Sample  (core logic also in test_dates.py)
# ===========================================================================

class TestTC2HistoricalInPipeline:
    """
    TC2: Integration-level test — add_historical_column labels old samples
    and those labels survive the analysis pipeline.
    """

    @patch("src.date_utils.today", return_value=FAKE_TODAY)
    def test_old_record_labelled_historical(self, _mock):
        df = pd.DataFrame({
            "date_parsed": [pd.Timestamp(FAKE_TODAY - timedelta(days=800))]
        })
        result = date_utils.add_historical_column(df, "date_parsed")
        assert result["Is_Historical"].iloc[0] == True  # numpy bool compatible
        assert "Historical" in result["Age_Label"].iloc[0]

    @patch("src.date_utils.today", return_value=FAKE_TODAY)
    def test_historical_label_contains_real_age(self, _mock):
        """The label must show actual age in days, not a generic word."""
        old_date = FAKE_TODAY - timedelta(days=500)
        label = date_utils.historical_label(pd.Timestamp(old_date))
        assert "500" in label

    @patch("src.date_utils.today", return_value=FAKE_TODAY)
    def test_historical_samples_do_not_appear_as_recent(self, _mock):
        """An old sample must never be described as 'recent'."""
        old_date = FAKE_TODAY - timedelta(days=700)
        label = date_utils.historical_label(pd.Timestamp(old_date))
        assert "recent" not in label.lower()


# ===========================================================================
# TC3 — Unit Normalization  (detailed in test_normalization.py)
# ===========================================================================

class TestTC3InScenarios:
    """
    TC3 integration check: 1 mg/L and 1000 µg/L are equivalent.
    Both values are synthetic test fixtures, NOT official measurements.
    """

    def test_1_mg_equals_1000_ug(self):
        equal, msg = values_are_equivalent(1.0, "mg/L", 1000.0, "µg/L")
        assert equal, f"Expected equality: {msg}"

    def test_synthetic_values_never_claimed_as_official(self):
        """
        This test explicitly asserts the design constraint:
        convert_unit(is_synthetic=True) results must never appear as real data.
        """
        from src.normalization import convert_unit
        result = convert_unit(1.0, "mg/L", "µg/L", is_synthetic=True)
        assert result.is_synthetic is True, (
            "Synthetic fixtures must always be flagged"
        )


# ===========================================================================
# TC4 — No Sample for Ward
# ===========================================================================

class TestTC4NoSampleForWard:
    """
    TC4: A ward with no verified matching record.
    Expected: correct no-data message, no invented sample, no substitute station.
    """

    def test_empty_filter_result_returns_no_invented_rows(self):
        """
        Filtering for a district/station that doesn't exist must return
        an empty DataFrame — never a padded or invented row.
        """
        df = _make_sample_df()
        result = filtering.filter_by_district(df, "District", "NonExistentDistrict")
        assert result.empty, "Filter must return empty, not invent records"

    def test_empty_station_filter_returns_empty(self):
        df = _make_sample_df()
        df2 = filtering.filter_by_district(df, "District", "Chennai")
        result = filtering.filter_by_station(df2, "Station", "GhostStation")
        assert result.empty

    def test_no_data_message_triggered_for_missing_ward(self):
        """
        The analysis pipeline must flag an empty result with a warning
        containing the expected no-data message content.
        """
        # Build a mock DatasetProfile with the small test frame
        df = _make_sample_df()
        profile = _make_profile(df)

        result = analysis.run_search(
            profile=profile,
            district="Chennai",
            station="Station_A",
            ward_input="Ward 99",         # Ward that has no mapping
            period="All available",
            selected_params=[],
        )
        # Must be flagged Unverified
        assert result["ward_match"]["status"] == "Unverified"
        # Must not return zero rows silently as OK
        # (records may exist for the station — but the ward is unverified)
        warn_text = " ".join(result["warnings"]).lower()
        assert "unverified" in warn_text

    def test_no_data_for_nonexistent_station(self):
        """
        When the station truly doesn't exist, records must be empty
        and a warning must appear — no nearby station substituted.
        """
        df = _make_sample_df()
        profile = _make_profile(df)

        result = analysis.run_search(
            profile=profile,
            district="Chennai",
            station="Ward_Only_Station_XYZ",  # does not exist in data
            ward_input="Ward 1",
            period="All available",
            selected_params=[],
        )
        assert result["records"].empty
        assert len(result["warnings"]) > 0

    def test_ward_assessment_never_verified_without_mapping(self):
        """Core TC4 assertion: Ward match must not be 'Verified' by default."""
        match = validation.assess_ward_match("Any_Station", "Ward 42")
        assert match["status"] != "Verified"


# ---------------------------------------------------------------------------
# Extra: Missing values
# ---------------------------------------------------------------------------

class TestMissingValues:
    def test_missing_measurement_not_converted_to_zero(self):
        """None/NaN must not become 0.0."""
        valid, disp = validation.validate_measurement_value(None)
        assert not valid
        assert "Not available" in disp
        assert disp != "0" and disp != "0.0"

    def test_empty_parameter_column_not_presented(self):
        df = _make_sample_df()
        df["EmptyCol"] = None
        empty = validation.check_completely_empty_columns(df)
        assert "EmptyCol" in empty

    def test_partial_missing_column_not_all_empty(self):
        df = _make_sample_df()
        empty = validation.check_completely_empty_columns(df)
        # EC has one None but is not completely empty
        assert "EC" not in empty


# ---------------------------------------------------------------------------
# Extra: Duplicate rows
# ---------------------------------------------------------------------------

class TestDuplicates:
    def test_duplicates_flagged(self):
        df = pd.DataFrame({
            "District": ["Chennai", "Chennai"],
            "Station":  ["Station_A", "Station_A"],
            "Year":     ["2022", "2022"],
            "pH":       [7.2, 7.2],
        })
        result = filtering.flag_duplicates(df, key_cols=["District", "Station", "Year"])
        assert "Is_Duplicate" in result.columns
        assert result["Is_Duplicate"].sum() == 1  # second row is dup

    def test_no_duplicates_not_flagged(self):
        df = _make_sample_df()
        result = filtering.flag_duplicates(df, key_cols=["District", "Station", "Year"])
        assert result["Is_Duplicate"].sum() == 0


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _make_profile(df: pd.DataFrame) -> analysis.DatasetProfile:
    """Build a DatasetProfile from a test DataFrame and parse its dates."""
    profile = analysis.DatasetProfile(df)
    profile.parse_dates()
    return profile
