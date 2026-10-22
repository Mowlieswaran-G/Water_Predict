"""
water_standards.py
==================
Official Bureau of Indian Standards (BIS IS 10500:2012)
Drinking Water Specification benchmarks and parameter evaluators.

Used to provide transparent chemical context for groundwater samples
collected across Tamil Nadu by the Central Ground Water Board (CGWB).
"""

from __future__ import annotations
import math
from typing import Any

# BIS IS 10500:2012 standards dictionary
# Keys correspond to exact column names found in the CGWB groundwater datasets.
BIS_STANDARDS: dict[str, dict[str, Any]] = {
    "Potential of Hydrogen (pH)": {
        "display_name": "pH (Potential of Hydrogen)",
        "unit": "pH units",
        "acceptable_min": 6.5,
        "acceptable_max": 8.5,
        "permissible_min": 6.5,
        "permissible_max": 8.5,
        "standard_ref": "BIS IS 10500:2012 (6.5 – 8.5)",
        "health_impact": "Values <6.5 cause corrosion of plumbing; >8.5 cause incrustation and bitter taste.",
    },
    "Electric Conductivity (I 1/4 S/cm)": {
        "display_name": "Electrical Conductivity (EC)",
        "unit": "µS/cm",
        "acceptable_max": 1500.0,
        "permissible_max": 2500.0,
        "standard_ref": "CPHEEO / WHO (Advisory <1500 µS/cm)",
        "health_impact": "Indicates total ionic concentration and dissolved mineral salts.",
    },
    "Total Dissolved Solids (mg/L)": {
        "display_name": "Total Dissolved Solids (TDS)",
        "unit": "mg/L",
        "acceptable_max": 500.0,
        "permissible_max": 2000.0,
        "standard_ref": "BIS IS 10500:2012 (Acceptable: 500, Max: 2000 mg/L)",
        "health_impact": "High TDS affects palatability and gastrointestinal irritation.",
    },
    "Total Hardness (mgCaCO3/L)": {
        "display_name": "Total Hardness (as CaCO₃)",
        "unit": "mg/L",
        "acceptable_max": 200.0,
        "permissible_max": 600.0,
        "standard_ref": "BIS IS 10500:2012 (Acceptable: 200, Max: 600 mg/L)",
        "health_impact": "Causes scale formation in boilers and consumes excessive soap.",
    },
    "Calcium (mg/L)": {
        "display_name": "Calcium (Ca)",
        "unit": "mg/L",
        "acceptable_max": 75.0,
        "permissible_max": 200.0,
        "standard_ref": "BIS IS 10500:2012 (Acceptable: 75, Max: 200 mg/L)",
        "health_impact": "Essential mineral; high levels contribute to scale encrustation.",
    },
    "Magnesium (mg/L)": {
        "display_name": "Magnesium (Mg)",
        "unit": "mg/L",
        "acceptable_max": 30.0,
        "permissible_max": 100.0,
        "standard_ref": "BIS IS 10500:2012 (Acceptable: 30, Max: 100 mg/L)",
        "health_impact": "High concentration in presence of sulphate exerts laxative action.",
    },
    "Chloride (mg/L)": {
        "display_name": "Chloride (Cl)",
        "unit": "mg/L",
        "acceptable_max": 250.0,
        "permissible_max": 1000.0,
        "standard_ref": "BIS IS 10500:2012 (Acceptable: 250, Max: 1000 mg/L)",
        "health_impact": "Imparts salty taste and accelerates metal corrosion in supply lines.",
    },
    "Fluoride (mg/L)": {
        "display_name": "Fluoride (F)",
        "unit": "mg/L",
        "acceptable_max": 1.0,
        "permissible_max": 1.5,
        "standard_ref": "BIS IS 10500:2012 (Acceptable: 1.0, Max: 1.5 mg/L)",
        "health_impact": "Excess (>1.5 mg/L) causes dental and skeletal fluorosis.",
    },
    "Nitrate N (mgN/L)": {
        "display_name": "Nitrate (as N / NO₃)",
        "unit": "mg/L",
        "acceptable_max": 45.0,
        "permissible_max": 45.0,
        "standard_ref": "BIS IS 10500:2012 (Max: 45 mg/L; No relaxation)",
        "health_impact": "Can cause methemoglobinemia (blue baby syndrome) in infants.",
    },
    "Sulphate (mg/L)": {
        "display_name": "Sulphate (SO₄)",
        "unit": "mg/L",
        "acceptable_max": 200.0,
        "permissible_max": 400.0,
        "standard_ref": "BIS IS 10500:2012 (Acceptable: 200, Max: 400 mg/L)",
        "health_impact": "May produce gastrointestinal irritation, particularly with high Mg.",
    },
    "Total Alkalinity (mg/L as CaCO3)": {
        "display_name": "Total Alkalinity (as CaCO₃)",
        "unit": "mg/L",
        "acceptable_max": 200.0,
        "permissible_max": 600.0,
        "standard_ref": "BIS IS 10500:2012 (Acceptable: 200, Max: 600 mg/L)",
        "health_impact": "Imparts unpleasant taste and reacts with cations.",
    },
    "Carbonate (mg/L)": {
        "display_name": "Carbonate (CO₃)",
        "unit": "mg/L",
        "standard_ref": "Advisory / Natural Mineral Component",
        "health_impact": "Buffering agent contributing to alkalinity.",
    },
    "Bicarbonate (mg/L)": {
        "display_name": "Bicarbonate (HCO₃)",
        "unit": "mg/L",
        "standard_ref": "Advisory / Natural Mineral Component",
        "health_impact": "Natural buffering component of groundwater.",
    },
    "Phosphate(mg/L)": {
        "display_name": "Phosphate (PO₄)",
        "unit": "mg/L",
        "standard_ref": "Advisory / Nutrient indicator (<0.1 mg/L recommended)",
        "health_impact": "Indicator of agricultural runoff or domestic detergent presence.",
    },
    "Silica(mg/L)": {
        "display_name": "Silica (SiO₂)",
        "unit": "mg/L",
        "standard_ref": "Advisory / Natural Rock Dissolution",
        "health_impact": "Harmless dissolved rock component.",
    },
    "Sodium (mg/L)": {
        "display_name": "Sodium (Na)",
        "unit": "mg/L",
        "acceptable_max": 200.0,
        "standard_ref": "WHO Guideline (Advisory: 200 mg/L for taste)",
        "health_impact": "Relevant for individuals on strict low-sodium dietary regimens.",
    },
    "Potassium (mg/L)": {
        "display_name": "Potassium (K)",
        "unit": "mg/L",
        "acceptable_max": 12.0,
        "standard_ref": "WHO Guideline (Advisory: 12 mg/L)",
        "health_impact": "Essential nutrient in small quantities; rarely harmful in water.",
    },
    "Iron(mg/L)": {
        "display_name": "Iron (Fe)",
        "unit": "mg/L",
        "acceptable_max": 1.0,
        "permissible_max": 1.0,
        "standard_ref": "BIS IS 10500:2012 Second Revision (Max: 1.0 mg/L)",
        "health_impact": "Stains laundry, promotes iron bacteria, alters taste and odor.",
    },
    "Arsenic (mg/L)": {
        "display_name": "Arsenic (As)",
        "unit": "mg/L",
        "acceptable_max": 0.01,
        "permissible_max": 0.05,
        "standard_ref": "BIS IS 10500:2012 (Acceptable: 0.01, Max: 0.05 mg/L)",
        "health_impact": "Carcinogenic and toxic; causes arsenicosis and skin lesions.",
    },
    "Uranium(mg/L)": {
        "display_name": "Uranium (U)",
        "unit": "mg/L",
        "acceptable_max": 0.03,
        "permissible_max": 0.03,
        "standard_ref": "AERB / WHO Guideline (Max: 0.03 mg/L)",
        "health_impact": "Chemical kidney toxicity and radiotoxicity over long exposure.",
    },
    "Manganese (mg/L)": {
        "display_name": "Manganese (Mn)",
        "unit": "mg/L",
        "acceptable_max": 0.1,
        "permissible_max": 0.3,
        "standard_ref": "BIS IS 10500:2012 (Acceptable: 0.1, Max: 0.3 mg/L)",
        "health_impact": "Produces black stains on plumbing and bitter metallic taste.",
    },
    "Copper (mg/L)": {
        "display_name": "Copper (Cu)",
        "unit": "mg/L",
        "acceptable_max": 0.05,
        "permissible_max": 1.5,
        "standard_ref": "BIS IS 10500:2012 (Acceptable: 0.05, Max: 1.5 mg/L)",
        "health_impact": "Astringent taste and gastrointestinal distress at high doses.",
    },
    "Lead (mg/L)": {
        "display_name": "Lead (Pb)",
        "unit": "mg/L",
        "acceptable_max": 0.01,
        "permissible_max": 0.01,
        "standard_ref": "BIS IS 10500:2012 (Max: 0.01 mg/L; No relaxation)",
        "health_impact": "Cumulative neurotoxin, particularly harmful to children.",
    },
    "Zinc (mg/L)": {
        "display_name": "Zinc (Zn)",
        "unit": "mg/L",
        "acceptable_max": 5.0,
        "permissible_max": 15.0,
        "standard_ref": "BIS IS 10500:2012 (Acceptable: 5.0, Max: 15.0 mg/L)",
        "health_impact": "Gives milkiness and metallic taste at concentrations >5 mg/L.",
    },
    "Nickel (mg/L)": {
        "display_name": "Nickel (Ni)",
        "unit": "mg/L",
        "acceptable_max": 0.02,
        "permissible_max": 0.02,
        "standard_ref": "BIS IS 10500:2012 (Max: 0.02 mg/L; No relaxation)",
        "health_impact": "Potential allergen and toxic heavy metal.",
    },
    "Cadmium (mg/L)": {
        "display_name": "Cadmium (Cd)",
        "unit": "mg/L",
        "acceptable_max": 0.003,
        "permissible_max": 0.003,
        "standard_ref": "BIS IS 10500:2012 (Max: 0.003 mg/L; No relaxation)",
        "health_impact": "Toxic heavy metal; damages renal function.",
    },
    "Chromium (mg/L)": {
        "display_name": "Chromium (Cr)",
        "unit": "mg/L",
        "acceptable_max": 0.05,
        "permissible_max": 0.05,
        "standard_ref": "BIS IS 10500:2012 (Max: 0.05 mg/L; No relaxation)",
        "health_impact": "Hexavalent chromium is carcinogenic upon chronic ingestion.",
    },
}


def evaluate_parameter(col_name: str, raw_value: Any) -> dict[str, Any]:
    """
    Evaluate a measurement value against BIS IS 10500:2012 standards.

    Returns a dict with:
        display_name, unit, raw_value, numeric_value,
        status ('acceptable' | 'permissible' | 'exceeded' | 'advisory' | 'missing'),
        status_label, badge_class, standard_ref, health_impact
    """
    spec = BIS_STANDARDS.get(col_name, {
        "display_name": col_name,
        "unit": "",
        "standard_ref": "Advisory Parameter",
        "health_impact": "General groundwater chemical parameter.",
    })

    display_name = spec.get("display_name", col_name)
    unit = spec.get("unit", "")
    standard_ref = spec.get("standard_ref", "Advisory")
    health_impact = spec.get("health_impact", "")

    # Check for missing / empty
    if raw_value is None or raw_value == "":
        return {
            "parameter": col_name,
            "display_name": display_name,
            "unit": unit,
            "raw_value": "—",
            "numeric_value": None,
            "status": "missing",
            "status_label": "Not Tested / Missing",
            "badge_class": "badge-muted",
            "standard_ref": standard_ref,
            "health_impact": health_impact,
        }

    try:
        val = float(raw_value)
        if math.isnan(val):
            return {
                "parameter": col_name,
                "display_name": display_name,
                "unit": unit,
                "raw_value": "—",
                "numeric_value": None,
                "status": "missing",
                "status_label": "Not Tested / Missing",
                "badge_class": "badge-muted",
                "standard_ref": standard_ref,
                "health_impact": health_impact,
            }
    except (ValueError, TypeError):
        return {
            "parameter": col_name,
            "display_name": display_name,
            "unit": unit,
            "raw_value": str(raw_value),
            "numeric_value": None,
            "status": "advisory",
            "status_label": str(raw_value),
            "badge_class": "badge-neutral",
            "standard_ref": standard_ref,
            "health_impact": health_impact,
        }

    # Special handling for pH
    if "ph" in col_name.lower():
        acc_min = spec.get("acceptable_min", 6.5)
        acc_max = spec.get("acceptable_max", 8.5)
        if acc_min <= val <= acc_max:
            return {
                "parameter": col_name,
                "display_name": display_name,
                "unit": unit,
                "raw_value": f"{val:.2f}",
                "numeric_value": val,
                "status": "acceptable",
                "status_label": "Within Desirable Limit",
                "badge_class": "badge-success",
                "standard_ref": standard_ref,
                "health_impact": health_impact,
            }
        else:
            return {
                "parameter": col_name,
                "display_name": display_name,
                "unit": unit,
                "raw_value": f"{val:.2f}",
                "numeric_value": val,
                "status": "exceeded",
                "status_label": "Exceeds BIS Range",
                "badge_class": "badge-danger",
                "standard_ref": standard_ref,
                "health_impact": health_impact,
            }

    # Standard numeric upper limits
    acc_max = spec.get("acceptable_max")
    perm_max = spec.get("permissible_max", acc_max)

    if acc_max is not None:
        if val <= acc_max:
            status = "acceptable"
            status_label = "Within Desirable Limit"
            badge_class = "badge-success"
        elif perm_max is not None and val <= perm_max:
            status = "permissible"
            status_label = "Within Permissible Limit"
            badge_class = "badge-warning"
        else:
            status = "exceeded"
            status_label = "Exceeds Permissible Limit"
            badge_class = "badge-danger"
    else:
        status = "advisory"
        status_label = "Natural Component / Advisory"
        badge_class = "badge-neutral"

    # Format numeric value display cleanly
    if val >= 10:
        val_str = f"{val:.1f}" if val != int(val) else f"{int(val)}"
    elif val >= 0.1:
        val_str = f"{val:.2f}"
    else:
        val_str = f"{val:.4f}"

    return {
        "parameter": col_name,
        "display_name": display_name,
        "unit": unit,
        "raw_value": val_str,
        "numeric_value": val,
        "status": status,
        "status_label": status_label,
        "badge_class": badge_class,
        "standard_ref": standard_ref,
        "health_impact": health_impact,
    }


def evaluate_sample_parameters(row_dict: dict, param_cols: list[str]) -> list[dict[str, Any]]:
    """
    Evaluate all requested parameters for a single sample row.
    """
    results = []
    for col in param_cols:
        val = row_dict.get(col)
        evaluated = evaluate_parameter(col, val)
        results.append(evaluated)
    return results
