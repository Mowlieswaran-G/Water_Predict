"""
app.py  –  Ward Water Quality Reporter
=======================================
Main Streamlit application entry point.

Run with:
    streamlit run app.py

Pages:
    🏠 Home & Search
    📋 Search Results
    🔍 Detailed Sample View
    📄 Report & Approval
    📜 Report History
"""

from __future__ import annotations
import io
import logging
import os
import sys

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Path fix (so src/ imports work from any CWD)
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(__file__))

from src import (
    data_loader,
    validation,
    filtering,
    date_utils,
    normalization,
    source_verification,
    analysis,
    report_generator,
    approval,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("app")

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Ward Water Quality Reporter",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS  (water-themed)
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Sidebar ───────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1628 0%, #0d2347 60%, #0a3d62 100%);
    color: #e0eeff;
}
section[data-testid="stSidebar"] * {
    color: #cce0ff !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-size: 0.95rem;
    padding: 6px 0;
}

/* ── Main background ───────────────────────────────── */
.main .block-container {
    background: #f0f4fa;
    padding-top: 1.5rem;
}

/* ── Title block ───────────────────────────────────── */
.title-block {
    background: linear-gradient(135deg, #0a1628 0%, #1a3a6b 50%, #0d5c99 100%);
    border-radius: 14px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 6px 24px rgba(10,22,40,0.35);
}
.title-block h1 {
    color: #ffffff;
    font-size: 2.2rem;
    font-weight: 700;
    margin: 0 0 0.3rem 0;
    letter-spacing: -0.5px;
}
.title-block p {
    color: #a8c8f0;
    font-size: 1rem;
    margin: 0;
}

/* ── Cards ──────────────────────────────────────────── */
.card {
    background: #ffffff;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    margin-bottom: 1rem;
}
.card-blue {
    border-left: 5px solid #1a6bbf;
}
.card-green {
    border-left: 5px solid #1e8a4a;
}
.card-amber {
    border-left: 5px solid #e8920a;
}
.card-red {
    border-left: 5px solid #c0392b;
}
.card h3 {
    color: #0a1628;
    font-size: 1rem;
    font-weight: 600;
    margin: 0 0 0.4rem 0;
}
.card p, .card div {
    color: #3a4a5c;
    font-size: 0.9rem;
    margin: 0;
}

/* ── Metric tiles ───────────────────────────────────── */
.metric-tile {
    background: linear-gradient(135deg, #1a3a6b, #1a6bbf);
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    color: white;
    text-align: center;
    box-shadow: 0 3px 12px rgba(26,107,191,0.3);
}
.metric-tile .value {
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
}
.metric-tile .label {
    font-size: 0.78rem;
    opacity: 0.85;
    margin-top: 0.35rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── Warning / info banners ─────────────────────────── */
.warn-banner {
    background: #fff8e1;
    border: 1px solid #f9a825;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    color: #7a5000;
    font-size: 0.88rem;
    margin: 0.5rem 0;
}
.danger-banner {
    background: #fdecea;
    border: 1px solid #e53935;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    color: #7b1515;
    font-size: 0.88rem;
    margin: 0.5rem 0;
}
.info-banner {
    background: #e3f2fd;
    border: 1px solid #1a6bbf;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    color: #0a2a55;
    font-size: 0.88rem;
    margin: 0.5rem 0;
}
.approved-banner {
    background: #e8f5e9;
    border: 1px solid #2e7d32;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    color: #1b4320;
    font-size: 0.88rem;
    margin: 0.5rem 0;
}

/* ── Section headings ───────────────────────────────── */
.section-heading {
    color: #0a1628;
    font-size: 1.1rem;
    font-weight: 600;
    border-bottom: 2px solid #1a6bbf;
    padding-bottom: 0.3rem;
    margin: 1.2rem 0 0.8rem 0;
}

/* ── Buttons ────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #1a6bbf, #0d5c99);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.55rem 1.6rem;
    font-weight: 600;
    font-size: 0.95rem;
    transition: all 0.2s ease;
    box-shadow: 0 3px 10px rgba(26,107,191,0.3);
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2176c7, #1a6bbf);
    box-shadow: 0 5px 16px rgba(26,107,191,0.45);
    transform: translateY(-1px);
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #1e8a4a, #145c30);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.45rem 1.2rem;
    font-weight: 600;
    font-size: 0.88rem;
}

/* ── Approve / Reject buttons ───────────────────────── */
div[data-testid="column"] .stButton > button.approve-btn {
    background: linear-gradient(135deg, #1e8a4a, #145c30) !important;
}
div[data-testid="column"] .stButton > button.reject-btn {
    background: linear-gradient(135deg, #c0392b, #922b21) !important;
}

/* ── Tables ─────────────────────────────────────────── */
.dataframe {
    font-size: 0.83rem !important;
}

/* ── Sidebar logo ───────────────────────────────────── */
.sidebar-logo {
    text-align: center;
    font-size: 2.8rem;
    margin-bottom: 0.5rem;
}
.sidebar-app-title {
    text-align: center;
    font-weight: 700;
    font-size: 1.05rem;
    color: #a8d8ff !important;
    margin-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)


# ===========================================================================
# Session state helpers
# ===========================================================================

def _init_state():
    defaults = {
        "search_done":     False,
        "search_result":   None,
        "profile":         None,
        "df_raw":          None,
        "selected_row_idx": None,
        "draft_report":    None,
        "page":            "🏠 Home & Search",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ===========================================================================
# Data loading  (cached once per session)
# ===========================================================================

@st.cache_resource(show_spinner="Loading dataset …")
def _load_data():
    """Load CSV and build DatasetProfile once per process."""
    df = data_loader.load_csv()
    profile = analysis.DatasetProfile(df)
    profile.parse_dates()
    return df, profile


# ===========================================================================
# Sidebar navigation
# ===========================================================================

def _sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">💧</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sidebar-app-title">Ward Water Quality Reporter</div>',
            unsafe_allow_html=True,
        )
        st.markdown("---")
        page = st.radio(
            "Navigate",
            [
                "🏠 Home & Search",
                "📋 Search Results",
                "🔍 Detailed Sample View",
                "📄 Report & Approval",
                "📜 Report History",
            ],
            index=[
                "🏠 Home & Search",
                "📋 Search Results",
                "🔍 Detailed Sample View",
                "📄 Report & Approval",
                "📜 Report History",
            ].index(st.session_state.page),
            label_visibility="collapsed",
        )
        st.session_state.page = page
        st.markdown("---")
        st.markdown(
            '<p style="font-size:0.75rem; color:#6a90c0; text-align:center;">'
            "Data: Central Ground Water Board<br>"
            "Tamil Nadu Groundwater Quality<br>"
            "⚠️ Not a drinking-water certificate"
            "</p>",
            unsafe_allow_html=True,
        )
    return page


# ===========================================================================
# Page 1 — Home & Search
# ===========================================================================

def page_home(df: pd.DataFrame, profile: analysis.DatasetProfile):
    # ── Title ─────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="title-block">
      <h1>💧 Ward Water Quality Reporter</h1>
      <p>Explore available groundwater records with transparent sources and sample dates.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Dataset info banner ───────────────────────────────────────────────
    st.markdown(
        '<div class="info-banner">📂 <b>Dataset loaded:</b> '
        f"{profile.total_rows:,} rows · {len(profile.param_cols)} measurable parameter(s) found.</div>",
        unsafe_allow_html=True,
    )

    # ── Search form ───────────────────────────────────────────────────────
    st.markdown('<div class="section-heading">🔎 Search Water-Quality Records</div>',
                unsafe_allow_html=True)

    with st.form("search_form"):
        col1, col2 = st.columns(2)

        with col1:
            # A — State (fixed)
            st.text_input("State", value="Tamil Nadu", disabled=True)

            # B — District
            districts = (
                data_loader.get_districts(df, profile.district_col)
                if profile.district_col else []
            )
            if not districts:
                st.warning("No district column found in dataset.")
                district = st.text_input("District (enter manually)", "")
            else:
                district = st.selectbox(
                    "District *",
                    ["— select —"] + districts,
                    help="Choose a district from the dataset.",
                )

            # C — Station
            if profile.station_col and profile.district_col and district != "— select —":
                stations = data_loader.get_stations_for_district(
                    df, profile.district_col, profile.station_col, district
                ) if district != "— select —" else []
            else:
                stations = []

            if stations:
                station = st.selectbox(
                    "Sampling Station *",
                    ["— select —"] + stations,
                    help="Stations available in the selected district.",
                )
            else:
                station = st.text_input(
                    "Sampling Station *",
                    "",
                    help="Enter the station name (no stations loaded for this district yet).",
                )

        with col2:
            # D — Ward
            st.markdown(
                '<p style="font-size:0.82rem; color:#c05a0a; font-weight:600;">'
                "ℹ️  Ward information: The current groundwater dataset does not contain "
                "verified ward-level assignments. Entering a ward will mark the result "
                "as <b>Unverified</b>. No station will be silently claimed as a ward's sample."
                "</p>",
                unsafe_allow_html=True,
            )
            ward_input = st.text_input(
                "Ward Name or Number (optional)",
                "",
                help="Enter a ward for reference — result will be flagged Unverified.",
            )

            # E — Date period
            period = st.selectbox(
                "Date Period *",
                [
                    "All available",
                    "Last 30 days",
                    "Last 6 months",
                    "Last 1 year",
                    "Custom",
                ],
            )
            custom_start = custom_end = None
            if period == "Custom":
                c1, c2 = st.columns(2)
                with c1:
                    custom_start = st.date_input("From")
                with c2:
                    custom_end = st.date_input("To")

            # F — Parameter
            param_options = ["All parameters"] + profile.param_cols
            selected_params_raw = st.multiselect(
                "Water-Quality Parameter(s)",
                param_options,
                default=["All parameters"],
                help="Select one or more parameters, or leave as 'All parameters'.",
            )
            if "All parameters" in selected_params_raw:
                selected_params = profile.param_cols
            else:
                selected_params = selected_params_raw

        # G — Submit
        submitted = st.form_submit_button(
            "🔍  Find Water-Quality Records",
            use_container_width=True,
        )

    if submitted:
        # Validate inputs
        d = district if district != "— select —" else ""
        s = station if station != "— select —" else ""
        valid, err = validation.validate_search_inputs(d, s)
        if not valid:
            st.error(err)
            return

        with st.spinner("Searching …"):
            result = analysis.run_search(
                profile=profile,
                district=d,
                station=s,
                ward_input=ward_input,
                period=period,
                selected_params=selected_params,
                custom_start=custom_start,
                custom_end=custom_end,
            )

        st.session_state.search_result = result
        st.session_state.search_done = True
        st.session_state.page = "📋 Search Results"
        st.rerun()


# ===========================================================================
# Page 2 — Search Results
# ===========================================================================

def page_results(profile: analysis.DatasetProfile):
    st.markdown("""
    <div class="title-block">
      <h1>📋 Search Results</h1>
      <p>Actual measurements from the groundwater dataset — with full source transparency.</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.search_done or st.session_state.search_result is None:
        st.info("No search has been run yet. Go to **🏠 Home & Search** to start.")
        return

    result = st.session_state.search_result
    records: pd.DataFrame = result["records"]
    warnings: list[str] = result["warnings"]
    ward_match: dict = result["ward_match"]
    param_cols: list[str] = result["param_cols_used"]

    # ── Summary cards ──────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f'<div class="metric-tile"><div class="value">{result["total_found"]}</div>'
            '<div class="label">Records Found</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="metric-tile"><div class="value">{result["period_found"]}</div>'
            '<div class="label">In Period</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        latest = result.get("latest_date") or "Unknown"
        st.markdown(
            f'<div class="metric-tile"><div class="value" style="font-size:1.1rem;">'
            f'{latest}</div><div class="label">Latest Sample Date</div></div>',
            unsafe_allow_html=True,
        )
    with c4:
        wstatus = ward_match.get("status", "N/A")
        color = "#e8920a" if wstatus == "Unverified" else (
            "#1e8a4a" if wstatus == "Verified" else "#6a7f99")
        st.markdown(
            f'<div class="metric-tile" style="background: linear-gradient(135deg, {color}, {color}cc);">'
            f'<div class="value" style="font-size:1rem;">{wstatus}</div>'
            '<div class="label">Ward Match</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Warnings ───────────────────────────────────────────────────────────
    if warnings:
        for w in warnings:
            st.markdown(f'<div class="warn-banner">{w}</div>', unsafe_allow_html=True)

    # ── Ward match explanation ──────────────────────────────────────────────
    if ward_match.get("status") == "Unverified":
        st.markdown(
            f'<div class="danger-banner">⚠️ <b>Ward match is UNVERIFIED.</b> '
            f'{ward_match.get("message", "")}</div>',
            unsafe_allow_html=True,
        )

    # ── No data case ────────────────────────────────────────────────────────
    if records.empty:
        st.markdown(
            '<div class="danger-banner">🔴 <b>No data found for this selection.</b><br>'
            "No data found for this ward in the available dataset. "
            "This does not mean the water is safe or unsafe.</div>",
            unsafe_allow_html=True,
        )
        return

    # ── Period-empty notice ─────────────────────────────────────────────────
    if result.get("period_empty"):
        st.markdown(
            '<div class="warn-banner">⏱️ <b>No samples found within the selected period.</b> '
            "Showing all available records. Broaden the date range to see more.</div>",
            unsafe_allow_html=True,
        )

    # ── Historical notice ───────────────────────────────────────────────────
    if "Is_Historical" in records.columns:
        hist_count = records["Is_Historical"].sum()
        if hist_count:
            st.markdown(
                f'<div class="warn-banner">🕰️ <b>{int(hist_count)} record(s) are Historical</b> '
                "(collected more than 1 year ago). "
                "They are labelled in the table below.</div>",
                unsafe_allow_html=True,
            )

    # ── Table ───────────────────────────────────────────────────────────────
    st.markdown('<div class="section-heading">📊 Measurement Records</div>',
                unsafe_allow_html=True)

    # Build display table
    display_cols = []
    for role_col in [profile.district_col, profile.station_col]:
        if role_col and role_col in records.columns:
            display_cols.append(role_col)

    if profile.date_col_raw and profile.date_col_raw in records.columns:
        display_cols.append(profile.date_col_raw)

    if "Age_Label" in records.columns:
        display_cols.append("Age_Label")

    display_cols += [p for p in param_cols if p in records.columns]

    if "Ward_Match_Status" not in records.columns:
        records = records.copy()
        records["Ward_Match_Status"] = ward_match.get("status", "N/A")
        display_cols.append("Ward_Match_Status")

    display_df = records[display_cols] if display_cols else records
    st.dataframe(display_df, use_container_width=True, height=400)

    # ── Row detail link ─────────────────────────────────────────────────────
    st.markdown(
        '<p style="font-size:0.82rem; color:#3a5a8a;">💡 Enter a row index below '
        "to inspect the full detail of that record.</p>",
        unsafe_allow_html=True,
    )
    row_idx = st.number_input(
        "Row index to inspect",
        min_value=0,
        max_value=max(len(records) - 1, 0),
        value=0,
        step=1,
    )
    if st.button("🔍 Open Detailed View"):
        st.session_state.selected_row_idx = int(row_idx)
        st.session_state.page = "🔍 Detailed Sample View"
        st.rerun()

    # ── Measurement summary ─────────────────────────────────────────────────
    st.markdown('<div class="section-heading">📈 Parameter Summary</div>',
                unsafe_allow_html=True)
    summary = analysis.summarise_measurements(records, param_cols)
    if summary.empty:
        st.info("No numeric measurements available for this selection.")
    else:
        st.dataframe(summary, use_container_width=True)

    # ── Source evidence ─────────────────────────────────────────────────────
    st.markdown('<div class="section-heading">🔗 Source Evidence</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="info-banner">'
        "<b>Dataset:</b> Tamil Nadu Groundwater Quality (Cleaned CSV)<br>"
        "<b>Official Source:</b> Central Ground Water Board (CGWB) — India<br>"
        "<b>Data Type:</b> Groundwater chemistry from monitoring wells. "
        "<b>NOT</b> verified treated drinking-water tap results.<br>"
        "<b>Ward Mapping:</b> No verified ward-to-station mapping is present. "
        "Ward associations are unverified proximity only."
        "</div>",
        unsafe_allow_html=True,
    )

    # ── Downloads ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-heading">⬇️ Download</div>',
                unsafe_allow_html=True)
    csv_bytes = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️  Download Results as CSV",
        data=csv_bytes,
        file_name="water_quality_results.csv",
        mime="text/csv",
    )

    # ── Generate report button ──────────────────────────────────────────────
    st.markdown('<div class="section-heading">📄 Generate Report</div>',
                unsafe_allow_html=True)
    if st.button("📄 Generate Draft Report for Approval →"):
        report_id = report_generator.create_report_id(
            result.get("district", ""), result.get("station", "")
        )
        # Pull search params from the first record (best effort)
        district_val = (records[profile.district_col].iloc[0]
                        if profile.district_col and not records.empty else "Unknown")
        station_val = (records[profile.station_col].iloc[0]
                       if profile.station_col and not records.empty else "Unknown")

        draft = report_generator.build_draft_report(
            report_id=report_id,
            district=district_val,
            station=station_val,
            ward_input=result.get("ward_input", ""),
            period=result.get("period", "All available"),
            records=records,
            param_cols=param_cols,
            ward_match=ward_match,
            warnings=warnings,
            latest_date=result.get("latest_date"),
            period_empty=result.get("period_empty", False),
            total_found=result["total_found"],
            period_found=result["period_found"],
            parsed_date_col=result.get("parsed_date_col"),
        )
        approval.save_draft(draft)
        st.session_state.draft_report = draft
        st.session_state.page = "📄 Report & Approval"
        st.rerun()


# ===========================================================================
# Page 3 — Detailed Sample View
# ===========================================================================

def page_detail(profile: analysis.DatasetProfile):
    st.markdown("""
    <div class="title-block">
      <h1>🔍 Detailed Sample View</h1>
      <p>Full record details with provenance and data-quality notes.</p>
    </div>
    """, unsafe_allow_html=True)

    if (
        not st.session_state.search_done
        or st.session_state.search_result is None
        or st.session_state.search_result["records"].empty
    ):
        st.info("No search results yet. Run a search first.")
        return

    records: pd.DataFrame = st.session_state.search_result["records"]
    idx = st.session_state.get("selected_row_idx", 0)
    idx = min(idx, len(records) - 1)

    row = records.iloc[idx]
    ward_match = st.session_state.search_result.get("ward_match", {})
    param_cols = st.session_state.search_result.get("param_cols_used", [])

    # ── Navigation ──────────────────────────────────────────────────────────
    c1, _, c2 = st.columns([1, 4, 1])
    with c1:
        if idx > 0 and st.button("← Previous"):
            st.session_state.selected_row_idx = idx - 1
            st.rerun()
    with c2:
        if idx < len(records) - 1 and st.button("Next →"):
            st.session_state.selected_row_idx = idx + 1
            st.rerun()

    st.markdown(f"**Showing record {idx + 1} of {len(records)}**")

    # ── Station / Location ──────────────────────────────────────────────────
    st.markdown('<div class="section-heading">📍 Location</div>',
                unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**District:** {row.get(profile.district_col, 'N/A')}")
        st.markdown(f"**Station:** {row.get(profile.station_col, 'N/A')}")
    with col2:
        lat_col = _find_coord_col(records, "lat")
        lon_col = _find_coord_col(records, "lon")
        lat_val = row.get(lat_col, "N/A") if lat_col else "N/A"
        lon_val = row.get(lon_col, "N/A") if lon_col else "N/A"
        st.markdown(f"**Latitude:** {lat_val}")
        st.markdown(f"**Longitude:** {lon_val}")

    # ── Date info ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-heading">📅 Sample Date</div>',
                unsafe_allow_html=True)
    raw_date = row.get(profile.date_col_raw, "N/A") if profile.date_col_raw else "N/A"
    age_label = row.get("Age_Label", "Date unknown")
    is_hist = row.get("Is_Historical")

    st.markdown(f"**Collection Date (original):** {raw_date}")
    if is_hist is True:
        st.markdown(
            f'<div class="warn-banner">🕰️ <b>Historical sample</b> — {age_label}. '
            "This is NOT a current measurement.</div>",
            unsafe_allow_html=True,
        )
    elif is_hist is False:
        st.markdown(
            f'<div class="approved-banner">📅 {age_label}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="info-banner">📅 Date unknown — cannot determine age.</div>',
            unsafe_allow_html=True,
        )

    # ── Measurements ───────────────────────────────────────────────────────
    st.markdown('<div class="section-heading">🧪 Measurements</div>',
                unsafe_allow_html=True)
    meas_rows = []
    for col in param_cols:
        raw_val = row.get(col)
        valid, disp = validation.validate_measurement_value(raw_val)
        meas_rows.append({
            "Parameter": col,
            "Measured Value": disp if valid else "Not available",
            "Unit": "(see column name — no separate unit column in dataset)",
            "Data Status": "OK" if valid else "Missing",
        })
    if meas_rows:
        st.dataframe(pd.DataFrame(meas_rows), use_container_width=True)
    else:
        st.info("No numeric parameters available for this record.")

    # ── Ward match ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-heading">🗺️ Ward Match Status</div>',
                unsafe_allow_html=True)
    wstatus = ward_match.get("status", "Not requested")
    if wstatus == "Unverified":
        st.markdown(
            f'<div class="danger-banner">⚠️ <b>Unverified:</b> '
            f'{ward_match.get("message", "")}</div>',
            unsafe_allow_html=True,
        )
    elif wstatus == "Not requested":
        st.info("No ward was specified for this search.")
    else:
        st.success(f"Ward match: {wstatus}")

    # ── Source evidence ──────────────────────────────────────────────────────
    st.markdown('<div class="section-heading">🔗 Source Evidence</div>',
                unsafe_allow_html=True)
    prov_cols = profile.provenance_cols
    evidence = source_verification.build_evidence_record(row, prov_cols)
    for k, v in evidence.items():
        st.markdown(f"- **{k.replace('_', ' ')}:** {v}")

    source_warnings = source_verification.validate_source_fields(evidence)
    for sw in source_warnings:
        st.markdown(f'<div class="warn-banner">{sw}</div>', unsafe_allow_html=True)

    # ── Original row data ────────────────────────────────────────────────────
    with st.expander("📂 Original raw row from dataset"):
        st.dataframe(row.to_frame().T, use_container_width=True)


def _find_coord_col(df: pd.DataFrame, kind: str) -> str | None:
    targets = ["lat", "latitude"] if kind == "lat" else ["lon", "lng", "longitude"]
    for col in df.columns:
        if col.lower() in targets:
            return col
    return None


# ===========================================================================
# Page 4 — Report & Approval
# ===========================================================================

def page_report_approval():
    st.markdown("""
    <div class="title-block">
      <h1>📄 Report & Human Approval</h1>
      <p>Review the draft report carefully before approving for publication.</p>
    </div>
    """, unsafe_allow_html=True)

    draft = st.session_state.get("draft_report")

    if draft is None:
        st.info(
            "No draft report exists yet. Run a search, view results, "
            "and click **Generate Draft Report**."
        )
        return

    # ── Report banner ────────────────────────────────────────────────────────
    current_status = approval.get_report_status(draft["Report_ID"]) or "DRAFT"
    status_color = {
        "DRAFT":    "#e8920a",
        "APPROVED": "#1e8a4a",
        "REJECTED": "#c0392b",
    }.get(current_status, "#6a7f99")

    st.markdown(
        f'<div style="background:{status_color}22; border-left:5px solid {status_color}; '
        f'border-radius:8px; padding:0.8rem 1.2rem; margin-bottom:1rem;">'
        f'<b>Report ID:</b> {draft["Report_ID"]} &nbsp;|&nbsp; '
        f'<b>Status:</b> {current_status} &nbsp;|&nbsp; '
        f'<b>Generated:</b> {draft.get("Generated_At", "")}'
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="danger-banner">⚠️ <b>Important:</b> This is a DRAFT groundwater report. '
        "It is NOT a ward drinking-water safety certificate. "
        "You must review all warnings before approving.</div>",
        unsafe_allow_html=True,
    )

    # ── Report fields ────────────────────────────────────────────────────────
    st.markdown('<div class="section-heading">📋 Report Details</div>',
                unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    fields_l = [
        ("Report Type",         draft.get("Report_Type")),
        ("State",               draft.get("State")),
        ("District",            draft.get("District")),
        ("Station",             draft.get("Station")),
        ("Ward Input",          draft.get("Ward_Input")),
        ("Period Requested",    draft.get("Period_Requested")),
    ]
    fields_r = [
        ("Total Records Found",  draft.get("Total_Records_Found")),
        ("Period Records Found", draft.get("Period_Records_Found")),
        ("Latest Sample Date",   draft.get("Latest_Sample_Date")),
        ("Sample Date Range",    draft.get("Sample_Date_Range")),
        ("Ward Match Status",    draft.get("Ward_Match_Status")),
    ]
    with col1:
        for label, val in fields_l:
            st.markdown(f"**{label}:** {val}")
    with col2:
        for label, val in fields_r:
            st.markdown(f"**{label}:** {val}")

    # ── Measurement summary ───────────────────────────────────────────────────
    st.markdown('<div class="section-heading">📊 Measurement Summary</div>',
                unsafe_allow_html=True)
    meas = draft.get("Measurement_Summary", [])
    if meas:
        st.dataframe(pd.DataFrame(meas), use_container_width=True)
    else:
        st.info("No numeric measurements in this report.")

    # ── Warnings ──────────────────────────────────────────────────────────────
    st.markdown('<div class="section-heading">⚠️ Warnings</div>',
                unsafe_allow_html=True)
    for w in draft.get("Warnings", []):
        st.markdown(f'<div class="warn-banner">{w}</div>', unsafe_allow_html=True)
    if not draft.get("Warnings"):
        st.success("No warnings.")

    # ── Limitations ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-heading">🚧 Limitations</div>',
                unsafe_allow_html=True)
    for lim in draft.get("Limitations", []):
        st.markdown(f"- {lim}")

    # ── Source references ─────────────────────────────────────────────────────
    st.markdown('<div class="section-heading">🔗 Source References</div>',
                unsafe_allow_html=True)
    for ref in draft.get("Source_References", []):
        st.markdown(f"- {ref}")

    # ── Approval buttons ──────────────────────────────────────────────────────
    st.markdown('<div class="section-heading">✅ Human Approval</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="info-banner">👁️ You must review all sections above before approving. '
        "Approval marks this report as reviewed — it does NOT certify water safety.</div>",
        unsafe_allow_html=True,
    )

    if current_status == "APPROVED":
        st.markdown(
            '<div class="approved-banner">✅ This report has already been APPROVED.</div>',
            unsafe_allow_html=True,
        )
    elif current_status == "REJECTED":
        st.markdown(
            '<div class="danger-banner">🔴 This report was REJECTED.</div>',
            unsafe_allow_html=True,
        )
    else:
        reviewer_name = st.text_input(
            "Your name (reviewer)",
            value="Anonymous Reviewer",
        )
        col_a, col_r = st.columns(2)
        with col_a:
            if st.button("✅ Approve Report", use_container_width=True):
                approval.approve_report(draft["Report_ID"], reviewer_name)
                draft["Approval_Status"] = "APPROVED"
                draft["Approved_By"] = reviewer_name
                st.session_state.draft_report = draft
                st.success(f"✅ Report {draft['Report_ID']} approved by {reviewer_name}.")
                st.rerun()
        with col_r:
            rejection_reason = st.text_input("Rejection reason (optional)")
            if st.button("❌ Reject Report", use_container_width=True):
                approval.reject_report(draft["Report_ID"], rejection_reason)
                draft["Approval_Status"] = "REJECTED"
                st.session_state.draft_report = draft
                st.warning(f"Report {draft['Report_ID']} has been rejected.")
                st.rerun()

    # ── Downloads ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-heading">⬇️ Download Report</div>',
                unsafe_allow_html=True)
    records = (
        st.session_state.search_result["records"]
        if st.session_state.search_result
        else pd.DataFrame()
    )
    param_cols = (
        st.session_state.search_result.get("param_cols_used", [])
        if st.session_state.search_result
        else []
    )
    report_df = report_generator.report_to_dataframe(draft, records)
    csv_bytes = report_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️  Download Report as CSV",
        data=csv_bytes,
        file_name=f"report_{draft['Report_ID']}.csv",
        mime="text/csv",
    )


# ===========================================================================
# Page 5 — Report History
# ===========================================================================

def page_history():
    st.markdown("""
    <div class="title-block">
      <h1>📜 Report History</h1>
      <p>All generated draft and approved reports stored locally.</p>
    </div>
    """, unsafe_allow_html=True)

    reports = approval.get_all_reports(limit=100)

    if not reports:
        st.info("No reports have been generated yet.")
        return

    df_hist = pd.DataFrame(reports)

    # Colour-code status
    def style_status(val):
        colors = {
            "APPROVED": "background-color:#d4edda; color:#1b5e20",
            "REJECTED": "background-color:#fde8e8; color:#7b1515",
            "DRAFT":    "background-color:#fff8e1; color:#7a5000",
        }
        return colors.get(val, "")

    styled = df_hist.style.applymap(style_status, subset=["approval_status"])
    st.dataframe(styled, use_container_width=True)

    # Allow reloading a past report
    st.markdown('<div class="section-heading">🔄 Reload a Report</div>',
                unsafe_allow_html=True)
    report_ids = df_hist["report_id"].tolist()
    chosen_id = st.selectbox("Select a Report ID", report_ids)
    if st.button("Load Report"):
        loaded = approval.load_report_json(chosen_id)
        if loaded:
            st.session_state.draft_report = loaded
            st.session_state.page = "📄 Report & Approval"
            st.success(f"Loaded report {chosen_id}.")
            st.rerun()
        else:
            st.error("Could not load report JSON.")


# ===========================================================================
# Sidebar: Dataset info expander
# ===========================================================================

def _dataset_info_expander(profile: analysis.DatasetProfile):
    with st.sidebar.expander("📊 Dataset Info"):
        st.markdown(f"**Rows:** {profile.total_rows:,}")
        st.markdown(f"**Parameters:** {len(profile.param_cols)}")
        st.markdown(f"**District col:** `{profile.district_col}`")
        st.markdown(f"**Station col:** `{profile.station_col}`")
        st.markdown(f"**Date col:** `{profile.date_col_raw}`")
        if profile.completely_empty_cols:
            st.markdown(
                f"**Empty cols ({len(profile.completely_empty_cols)}):** "
                + ", ".join(profile.completely_empty_cols[:5])
            )


# ===========================================================================
# Main entry point
# ===========================================================================

def main():
    _init_state()
    page = _sidebar()

    # ── Check if dataset exists ─────────────────────────────────────────────
    if not data_loader.file_exists():
        st.markdown("""
        <div class="title-block">
          <h1>💧 Ward Water Quality Reporter</h1>
          <p>Dataset not found.</p>
        </div>
        """, unsafe_allow_html=True)
        st.error(
            "🚫 **Dataset not found!**\n\n"
            f"Please place your CSV file at:\n\n"
            f"`{data_loader.get_csv_path()}`\n\n"
            "The expected filename is: `tamil_nadu_groundwater_quality_cleaned.csv`\n\n"
            "Once the file is in the `data/` folder, refresh this page."
        )
        return

    # ── Load data ────────────────────────────────────────────────────────────
    try:
        df, profile = _load_data()
    except (FileNotFoundError, ValueError) as exc:
        st.error(f"🚫 Error loading dataset: {exc}")
        return

    _dataset_info_expander(profile)

    # ── Route to page ────────────────────────────────────────────────────────
    if page == "🏠 Home & Search":
        page_home(df, profile)
    elif page == "📋 Search Results":
        page_results(profile)
    elif page == "🔍 Detailed Sample View":
        page_detail(profile)
    elif page == "📄 Report & Approval":
        page_report_approval()
    elif page == "📜 Report History":
        page_history()


if __name__ == "__main__":
    main()
