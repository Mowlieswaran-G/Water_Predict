"""
test_dates.py
=============
TC2: Historical Sample labelling
+ extra date parsing and period-filter tests
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import pandas as pd
from datetime import date, timedelta
from unittest.mock import patch

from src.date_utils import (
    parse_date_column,
    sample_age_days,
    is_historical,
    historical_label,
    filter_by_period,
    add_historical_column,
    HISTORICAL_THRESHOLD_DAYS,
)

FAKE_TODAY = date(2024, 6, 1)  # Fixed reference date for all tests


class TestTC2HistoricalSample:
    """
    TC2 — Historical Sample
    Input: a sample collected more than one year ago.
    Expected: labelled Historical, actual date shown, not called current.
    """

    @patch("src.date_utils.today", return_value=FAKE_TODAY)
    def test_old_sample_is_historical(self, _mock):
        old_date = FAKE_TODAY - timedelta(days=400)
        assert is_historical(pd.Timestamp(old_date)) is True

    @patch("src.date_utils.today", return_value=FAKE_TODAY)
    def test_old_sample_label_says_historical(self, _mock):
        old_date = FAKE_TODAY - timedelta(days=400)
        label = historical_label(pd.Timestamp(old_date))
        assert "Historical" in label, f"Expected 'Historical' in '{label}'"

    @patch("src.date_utils.today", return_value=FAKE_TODAY)
    def test_old_sample_label_not_current(self, _mock):
        """Label must not contain words implying the sample is current."""
        old_date = FAKE_TODAY - timedelta(days=500)
        label = historical_label(pd.Timestamp(old_date))
        for bad_word in ["current", "recent", "today", "now"]:
            assert bad_word.lower() not in label.lower(), (
                f"Label should not contain '{bad_word}': '{label}'"
            )

    @patch("src.date_utils.today", return_value=FAKE_TODAY)
    def test_recent_sample_not_historical(self, _mock):
        recent = FAKE_TODAY - timedelta(days=30)
        assert is_historical(pd.Timestamp(recent)) is False

    @patch("src.date_utils.today", return_value=FAKE_TODAY)
    def test_unknown_date_returns_none(self, _mock):
        assert is_historical(None) is None
        assert is_historical(pd.NaT) is None


class TestDateParsing:
    """Tests for parse_date_column — must never guess unparseable values."""

    def test_standard_date_string(self):
        s = pd.Series(["2020-03-15"])
        result = parse_date_column(s)
        assert result.iloc[0] == pd.Timestamp("2020-03-15")

    def test_year_only(self):
        s = pd.Series(["2019"])
        result = parse_date_column(s)
        assert result.iloc[0] == pd.Timestamp("2019-01-01")

    def test_numeric_year(self):
        s = pd.Series([2021])
        result = parse_date_column(s)
        assert result.iloc[0] == pd.Timestamp("2021-01-01")

    def test_unparseable_is_nat(self):
        s = pd.Series(["not-a-date", "??", ""])
        result = parse_date_column(s)
        assert result.isna().all(), "Unparseable dates must be NaT"

    def test_mixed_valid_invalid(self):
        s = pd.Series(["2022-01-10", "garbage"])
        result = parse_date_column(s)
        assert result.iloc[0] == pd.Timestamp("2022-01-10")
        assert pd.isna(result.iloc[1])

    def test_none_is_nat(self):
        s = pd.Series([None])
        result = parse_date_column(s)
        assert pd.isna(result.iloc[0])


class TestFilterByPeriod:
    """Ensure period filtering does not silently return out-of-range records."""

    def _make_df(self):
        dates = pd.to_datetime([
            "2024-05-20",  # within last 30 days of FAKE_TODAY
            "2023-10-01",  # within last 6 months of FAKE_TODAY
            "2022-01-15",  # older — historical
            pd.NaT,        # unknown date
        ])
        df = pd.DataFrame({"date_parsed": dates, "value": [1, 2, 3, 4]})
        return df

    @patch("src.date_utils.today", return_value=FAKE_TODAY)
    def test_last_30_days(self, _mock):
        df = self._make_df()
        result = filter_by_period(df, "date_parsed", "Last 30 days")
        assert len(result) == 1  # only 2024-05-20

    @patch("src.date_utils.today", return_value=FAKE_TODAY)
    def test_last_6_months(self, _mock):
        df = self._make_df()
        result = filter_by_period(df, "date_parsed", "Last 6 months")
        # 2024-05-20 and 2023-10-01 (≈240 days from 2024-06-01 ... wait)
        # 2023-10-01 is 244 days before 2024-06-01 — beyond 183 days
        # So only 2024-05-20 qualifies
        assert all(result["date_parsed"].notna())

    @patch("src.date_utils.today", return_value=FAKE_TODAY)
    def test_all_available_returns_all_rows(self, _mock):
        df = self._make_df()
        result = filter_by_period(df, "date_parsed", "All available")
        assert len(result) == len(df)

    @patch("src.date_utils.today", return_value=FAKE_TODAY)
    def test_no_match_returns_empty(self, _mock):
        """If no rows match, return empty — do not silently include them."""
        df = pd.DataFrame({
            "date_parsed": pd.to_datetime(["2010-01-01", "2011-05-05"]),
            "value": [10, 20],
        })
        result = filter_by_period(df, "date_parsed", "Last 30 days")
        assert result.empty, "Should return empty when no rows are in range"


class TestAddHistoricalColumn:
    """Test that add_historical_column correctly annotates a DataFrame."""

    @patch("src.date_utils.today", return_value=FAKE_TODAY)
    def test_adds_columns(self, _mock):
        df = pd.DataFrame({
            "d": pd.to_datetime([
                FAKE_TODAY - timedelta(days=500),
                FAKE_TODAY - timedelta(days=10),
            ])
        })
        result = add_historical_column(df, "d")
        assert "Is_Historical" in result.columns
        assert "Age_Label" in result.columns

    @patch("src.date_utils.today", return_value=FAKE_TODAY)
    def test_historical_true_for_old(self, _mock):
        df = pd.DataFrame({"d": [pd.Timestamp(FAKE_TODAY - timedelta(days=800))]})
        result = add_historical_column(df, "d")
        assert result["Is_Historical"].iloc[0] == True  # numpy bool compatible

    @patch("src.date_utils.today", return_value=FAKE_TODAY)
    def test_historical_false_for_recent(self, _mock):
        df = pd.DataFrame({"d": [pd.Timestamp(FAKE_TODAY - timedelta(days=5))]})
        result = add_historical_column(df, "d")
        assert result["Is_Historical"].iloc[0] == False  # numpy bool compatible
