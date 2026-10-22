"""
test_datasets_integration.py
=============================
Tests verifying the seamless integration of all 3 official datasets:
1. tamil_nadu_groundwater_quality_cleaned.csv
2. tamil_nadu_groundwater_quality_raw.csv
3. tamil_nadu_ulb_wards.csv
"""

import pytest
import pandas as pd
from src import data_loader, water_standards
from app import app


def test_ulb_dataset_loaded():
    ulbs = data_loader.get_ulb_list()
    assert len(ulbs) == 125
    avadi = data_loader.get_ulb_details("Avadi")
    assert avadi is not None
    assert avadi["name"] == "Avadi"
    assert avadi["grade"] == "SPECIAL"
    assert avadi["total_wards"] == 48
    assert avadi["council_general"] == 31
    assert avadi["council_sc"] == 4
    assert avadi["council_women"] == 13


def test_groundwater_datasets_alignment():
    clean_df = data_loader.load_csv()
    raw_df = data_loader.load_raw_csv()
    assert len(clean_df) == 433
    assert len(raw_df) == 433
    # Check 1:1 ID match
    assert (clean_df["_id"] == raw_df["_id"]).all()
    # Check that clean has ISO date columns added
    assert "Sample Date (ISO)" in clean_df.columns
    assert "Recency Label (as of 2026-10-20)" in clean_df.columns
    assert "Data Type / Caveat" in clean_df.columns


def test_water_standards_evaluation():
    # pH within limits
    eval_ph_ok = water_standards.evaluate_parameter("Potential of Hydrogen (pH)", 7.4)
    assert eval_ph_ok["status"] == "acceptable"
    assert eval_ph_ok["badge_class"] == "badge-success"

    # pH acidic (exceeded)
    eval_ph_acid = water_standards.evaluate_parameter("Potential of Hydrogen (pH)", 5.2)
    assert eval_ph_acid["status"] == "exceeded"
    assert eval_ph_acid["badge_class"] == "badge-danger"

    # Fluoride desirable (<=1.0)
    eval_f_ok = water_standards.evaluate_parameter("Fluoride (mg/L)", 0.8)
    assert eval_f_ok["status"] == "acceptable"

    # Fluoride permissible (1.0 - 1.5)
    eval_f_perm = water_standards.evaluate_parameter("Fluoride (mg/L)", 1.2)
    assert eval_f_perm["status"] == "permissible"
    assert eval_f_perm["badge_class"] == "badge-warning"

    # Fluoride excessive (>1.5)
    eval_f_high = water_standards.evaluate_parameter("Fluoride (mg/L)", 2.4)
    assert eval_f_high["status"] == "exceeded"

    # Missing value
    eval_missing = water_standards.evaluate_parameter("Total Dissolved Solids (mg/L)", None)
    assert eval_missing["status"] == "missing"
    assert eval_missing["badge_class"] == "badge-muted"


def test_api_ulbs_endpoint():
    client = app.test_client()
    resp = client.get("/api/ulbs")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "ulbs" in data
    assert len(data["ulbs"]) == 125
