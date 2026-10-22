"""
app.py  –  Ward Water Quality Reporter  (Flask edition)
========================================================
Run locally:
    python app.py

Run via Docker:
    docker compose up --build
"""

from __future__ import annotations
import io
import json
import logging
import os
import sys

import pandas as pd
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, send_file, g
)

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
    auth,
    water_standards,
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
# Flask setup
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "wwqr-dev-secret-change-in-prod")

# Custom Jinja2 filters
app.jinja_env.filters["enumerate"] = enumerate


@app.context_processor
def inject_user():
    return {
        "current_user": session.get("user"),
        "demo_users": auth.DEFAULT_USERS,
        "available_roles": auth.AVAILABLE_ROLES,
    }


# ---------------------------------------------------------------------------
# Global cached data (loaded once at startup)
# ---------------------------------------------------------------------------
_CACHED_DF: pd.DataFrame | None = None
_CACHED_PROFILE: analysis.DatasetProfile | None = None
_CACHED_RAW_DF: pd.DataFrame | None = None
_CACHED_ULBS: list[dict] | None = None
_LOAD_ERROR: str | None = None


def _get_data() -> tuple[pd.DataFrame | None, analysis.DatasetProfile | None, str | None]:
    global _CACHED_DF, _CACHED_PROFILE, _LOAD_ERROR
    if _CACHED_DF is not None:
        return _CACHED_DF, _CACHED_PROFILE, None
    if _LOAD_ERROR is not None:
        return None, None, _LOAD_ERROR
    if not data_loader.file_exists():
        _LOAD_ERROR = (
            f"Dataset not found at: {data_loader.get_csv_path()}<br>"
            "Please place <code>tamil_nadu_groundwater_quality_cleaned.csv</code> "
            "inside the <code>data/</code> folder and restart the server."
        )
        return None, None, _LOAD_ERROR
    try:
        _CACHED_DF = data_loader.load_csv()
        _CACHED_PROFILE = analysis.DatasetProfile(_CACHED_DF)
        _CACHED_PROFILE.parse_dates()
        logger.info("Dataset loaded: %d rows", len(_CACHED_DF))
    except Exception as exc:
        _LOAD_ERROR = str(exc)
        return None, None, _LOAD_ERROR
    return _CACHED_DF, _CACHED_PROFILE, None


def _get_raw_data() -> pd.DataFrame | None:
    global _CACHED_RAW_DF
    if _CACHED_RAW_DF is not None:
        return _CACHED_RAW_DF
    if data_loader.raw_file_exists():
        try:
            _CACHED_RAW_DF = data_loader.load_raw_csv()
            logger.info("Raw CGWB dataset loaded: %d rows", len(_CACHED_RAW_DF))
        except Exception as exc:
            logger.warning("Could not load raw dataset: %s", exc)
    return _CACHED_RAW_DF


def _get_ulbs() -> list[dict]:
    global _CACHED_ULBS
    if _CACHED_ULBS is not None:
        return _CACHED_ULBS
    if data_loader.ulb_file_exists():
        try:
            _CACHED_ULBS = data_loader.get_ulb_list()
            logger.info("ULB wards dataset loaded: %d municipalities", len(_CACHED_ULBS))
        except Exception as exc:
            logger.warning("Could not load ULB dataset: %s", exc)
            _CACHED_ULBS = []
    else:
        _CACHED_ULBS = []
    return _CACHED_ULBS


# ---------------------------------------------------------------------------
# Role-based dashboard helpers & routes
# ---------------------------------------------------------------------------

def get_role_dashboard_url(role: str) -> str:
    """Return the designated dashboard endpoint URL based on user role."""
    if role == "Environmental Officer":
        return url_for("dashboard_officer")
    elif role == "Municipal Quality Inspector":
        return url_for("dashboard_inspector")
    elif role == "Senior Hydrologist":
        return url_for("dashboard_hydrologist")
    else:
        return url_for("dashboard_citizen")


@app.route("/")
def home():
    """
    Entry point: If user is not logged in, display the login page first.
    If user is authenticated, navigate directly to their respective role dashboard.
    """
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    return redirect(get_role_dashboard_url(user.get("role", "")))


@app.route("/dashboard/officer")
def dashboard_officer():
    user = session.get("user")
    if not user:
        return redirect(url_for("login", next=request.path))

    stats = approval.get_approval_stats()
    pending = approval.get_reports_by_status("DRAFT", limit=20)
    recent = approval.get_all_reports(limit=10)
    return render_template(
        "dashboards/officer.html",
        stats=stats,
        pending_reports=pending,
        recent_decisions=recent,
    )


@app.route("/dashboard/inspector")
def dashboard_inspector():
    user = session.get("user")
    if not user:
        return redirect(url_for("login", next=request.path))

    stats = approval.get_approval_stats()
    return render_template(
        "dashboards/inspector.html",
        stats=stats,
    )


@app.route("/dashboard/hydrologist")
def dashboard_hydrologist():
    user = session.get("user")
    if not user:
        return redirect(url_for("login", next=request.path))

    stats = approval.get_approval_stats()
    return render_template(
        "dashboards/hydrologist.html",
        stats=stats,
    )


@app.route("/dashboard/citizen")
def dashboard_citizen():
    user = session.get("user")
    if not user:
        return redirect(url_for("login", next=request.path))

    approved = approval.get_reports_by_status("APPROVED", limit=10)
    return render_template(
        "dashboards/citizen.html",
        approved_reports=approved,
    )


@app.route("/search-explorer")
def search_explorer():
    """Universal groundwater search interface for all authenticated users."""
    user = session.get("user")
    if not user:
        return redirect(url_for("login", next=request.path))

    df, profile, error = _get_data()
    if error:
        return render_template("error.html", error=error), 503

    districts = (
        data_loader.get_districts(df, profile.district_col)
        if profile.district_col else []
    )
    ulbs = _get_ulbs()
    raw_df = _get_raw_data()

    return render_template(
        "home.html",
        districts=districts,
        ulbs=ulbs,
        total_rows=profile.total_rows,
        raw_rows=len(raw_df) if raw_df is not None else 0,
        ulb_count=len(ulbs),
        param_count=len(profile.param_cols),
        param_cols=profile.param_cols,
    )


@app.route("/stations")
def stations_ajax():
    """AJAX endpoint: return stations for a selected district as JSON."""
    df, profile, error = _get_data()
    if error:
        return jsonify({"stations": []})
    district = request.args.get("district", "")
    if not district or not profile.district_col or not profile.station_col:
        return jsonify({"stations": []})
    stations = data_loader.get_stations_for_district(
        df, profile.district_col, profile.station_col, district
    )
    return jsonify({"stations": stations})


@app.route("/api/ulbs")
def ulbs_api():
    """AJAX endpoint: return all 125 Tamil Nadu Urban Local Bodies (Municipalities)."""
    return jsonify({"ulbs": _get_ulbs()})


@app.route("/search", methods=["POST"])
def search():
    df, profile, error = _get_data()
    if error:
        return render_template("error.html", error=error), 503

    district     = request.form.get("district", "").strip()
    station      = request.form.get("station", "").strip()
    ulb_name     = request.form.get("ulb_name", "").strip()
    ward_input   = request.form.get("ward_input", "").strip()
    dataset_mode = request.form.get("dataset_mode", "cleaned").strip().lower()
    period       = request.form.get("period", "All available")
    custom_start_str = request.form.get("custom_start", "")
    custom_end_str   = request.form.get("custom_end", "")
    selected_params_raw = request.form.getlist("params")

    # Fetch municipality details from dataset 3
    ulb_details = data_loader.get_ulb_details(ulb_name) if ulb_name else None

    # Parse custom dates
    from datetime import date
    custom_start = custom_end = None
    if period == "Custom":
        try:
            custom_start = date.fromisoformat(custom_start_str)
            custom_end   = date.fromisoformat(custom_end_str)
        except ValueError:
            pass

    # Validate inputs
    valid, err = validation.validate_search_inputs(district, station)
    if not valid:
        flash(err, "error")
        return redirect(url_for("home"))

    if "All parameters" in selected_params_raw or not selected_params_raw:
        selected_params = profile.param_cols
    else:
        selected_params = selected_params_raw

    result = analysis.run_search(
        profile=profile,
        district=district,
        station=station,
        ward_input=ward_input,
        period=period,
        selected_params=selected_params,
        custom_start=custom_start,
        custom_end=custom_end,
    )

    # If ULB was provided, note transparent caveat
    if ulb_details:
        result["warnings"].append(
            f"ℹ️ Selected Municipality: {ulb_details['name']} ({ulb_details['grade']} Grade, {ulb_details['total_wards']} Wards). "
            "CGWB stations are groundwater exploratory wells; municipal ward boundaries are not officially mapped in CGWB data."
        )

    # Store result in session (serialise records to JSON)
    records_json = result["records"].to_json(orient="split", date_format="iso")
    session["search_result_meta"] = {
        "total_found":     result["total_found"],
        "period_found":    result["period_found"],
        "period_empty":    result["period_empty"],
        "warnings":        result["warnings"],
        "ward_match":      result["ward_match"],
        "param_cols_used": result["param_cols_used"],
        "latest_date":     result["latest_date"],
        "parsed_date_col": result["parsed_date_col"],
        "district":        district,
        "station":         station,
        "ulb_name":        ulb_name,
        "ulb_details":     ulb_details,
        "dataset_mode":    dataset_mode,
        "ward_input":      ward_input,
        "period":          period,
    }
    session["records_json"] = records_json

    return redirect(url_for("results"))


@app.route("/results")
def results():
    df, profile, error = _get_data()
    if error:
        return render_template("error.html", error=error), 503

    meta = session.get("search_result_meta")
    records_json = session.get("records_json")

    if not meta:
        flash("No search has been run yet.", "info")
        return redirect(url_for("home"))

    records = pd.read_json(io.StringIO(records_json), orient="split") if records_json else pd.DataFrame()

    # Build display columns list
    display_cols = []
    for c in [profile.district_col, profile.station_col, profile.date_col_raw]:
        if c and c in records.columns:
            display_cols.append(c)
    if "Age_Label" in records.columns:
        display_cols.append("Age_Label")
    if "Ward_Match_Status" not in records.columns and not records.empty:
        records["Ward_Match_Status"] = meta["ward_match"].get("status", "N/A")
    if "Ward_Match_Status" in records.columns:
        display_cols.append("Ward_Match_Status")
    for p in meta["param_cols_used"]:
        if p in records.columns:
            display_cols.append(p)

    display_df = records[display_cols] if display_cols and not records.empty else records

    # Evaluate chemical parameters for sample using BIS IS 10500:2012 standards
    evaluated_params_list = []
    stat_counts = {"total": 0, "acceptable": 0, "permissible": 0, "exceeded": 0, "advisory": 0, "missing": 0}
    if not records.empty:
        first_row_dict = records.iloc[0].to_dict()
        evaluated_params_list = water_standards.evaluate_sample_parameters(
            first_row_dict, meta["param_cols_used"]
        )
        stat_counts = {
            "total": len(evaluated_params_list),
            "acceptable": sum(1 for p in evaluated_params_list if p["status"] == "acceptable"),
            "permissible": sum(1 for p in evaluated_params_list if p["status"] == "permissible"),
            "exceeded": sum(1 for p in evaluated_params_list if p["status"] == "exceeded"),
            "advisory": sum(1 for p in evaluated_params_list if p["status"] == "advisory"),
            "missing": sum(1 for p in evaluated_params_list if p["status"] == "missing"),
        }

    # Fetch corresponding raw records from Dataset 2 for side-by-side comparison
    raw_df = _get_raw_data()
    raw_records_map = {}
    if raw_df is not None and not records.empty and "_id" in records.columns:
        subset_raw = raw_df[raw_df["_id"].isin(records["_id"])].set_index("_id")
        raw_records_map = subset_raw.to_dict(orient="index")

    # Measurement summary
    summary = analysis.summarise_measurements(records, meta["param_cols_used"])

    # Missing values report
    missing_rpt = (
        filtering.missing_value_report(records, meta["param_cols_used"])
        if not records.empty else pd.DataFrame()
    )

    return render_template(
        "results.html",
        meta=meta,
        records=display_df.to_dict(orient="records"),
        columns=display_df.columns.tolist(),
        summary=summary.to_dict(orient="records"),
        missing=missing_rpt.to_dict(orient="records"),
        evaluated_params=evaluated_params_list,
        stat_counts=stat_counts,
        raw_records_map=raw_records_map,
        ulb_name=meta.get("ulb_name"),
        ulb_details=meta.get("ulb_details"),
        dataset_mode=meta.get("dataset_mode", "cleaned"),
        row_count=len(records),
    )


@app.route("/detail/<int:row_idx>")
def detail(row_idx: int):
    df, profile, error = _get_data()
    if error:
        return render_template("error.html", error=error), 503

    records_json = session.get("records_json")
    meta = session.get("search_result_meta")

    if not records_json or not meta:
        flash("No search results. Run a search first.", "info")
        return redirect(url_for("home"))

    records = pd.read_json(io.StringIO(records_json), orient="split")
    if records.empty or row_idx >= len(records):
        flash("Row not found.", "error")
        return redirect(url_for("results"))

    row = records.iloc[row_idx]
    row_dict = row.to_dict()

    # Build measurement rows evaluated against BIS standards
    evaluated_params = water_standards.evaluate_sample_parameters(
        row_dict, meta["param_cols_used"]
    )

    # Fetch raw row for direct comparison
    raw_df = _get_raw_data()
    raw_row = None
    if raw_df is not None and "_id" in row and not pd.isna(row["_id"]):
        matching = raw_df[raw_df["_id"] == row["_id"]]
        if not matching.empty:
            raw_row = matching.iloc[0].to_dict()

    # Source evidence
    prov_cols = profile.provenance_cols
    evidence = source_verification.build_evidence_record(row, prov_cols)
    source_warnings = source_verification.validate_source_fields(evidence)

    # Date info
    raw_date = row.get(profile.date_col_raw, "N/A") if profile.date_col_raw else "N/A"
    age_label = row.get("Age_Label", "Date unknown")
    is_hist = row.get("Is_Historical")

    # Coordinates
    lat_col = _find_coord_col(records, "lat")
    lon_col = _find_coord_col(records, "lon")

    return render_template(
        "detail.html",
        row=row_dict,
        row_idx=row_idx,
        total_rows=len(records),
        district=row.get(profile.district_col, "N/A") if profile.district_col else "N/A",
        station=row.get(profile.station_col, "N/A") if profile.station_col else "N/A",
        raw_date=raw_date,
        age_label=age_label,
        is_historical=is_hist,
        evaluated_params=evaluated_params,
        raw_row=raw_row,
        ulb_name=meta.get("ulb_name"),
        ulb_details=meta.get("ulb_details"),
        dataset_mode=meta.get("dataset_mode", "cleaned"),
        evidence=evidence,
        source_warnings=source_warnings,
        ward_match=meta["ward_match"],
        lat=row.get(lat_col, "N/A") if lat_col else "N/A",
        lon=row.get(lon_col, "N/A") if lon_col else "N/A",
    )


@app.route("/generate_report", methods=["POST"])
def generate_report():
    df, profile, error = _get_data()
    if error:
        return render_template("error.html", error=error), 503

    records_json = session.get("records_json")
    meta = session.get("search_result_meta")

    if not records_json or not meta:
        flash("No search results to report on.", "error")
        return redirect(url_for("home"))

    records = pd.read_json(io.StringIO(records_json), orient="split")

    report_id = report_generator.create_report_id(
        meta.get("district", ""), meta.get("station", "")
    )
    draft = report_generator.build_draft_report(
        report_id=report_id,
        district=meta.get("district", ""),
        station=meta.get("station", ""),
        ward_input=meta.get("ward_input", ""),
        period=meta.get("period", "All available"),
        records=records,
        param_cols=meta.get("param_cols_used", []),
        ward_match=meta.get("ward_match", {}),
        warnings=meta.get("warnings", []),
        latest_date=meta.get("latest_date"),
        period_empty=meta.get("period_empty", False),
        total_found=meta.get("total_found", 0),
        period_found=meta.get("period_found", 0),
        parsed_date_col=meta.get("parsed_date_col"),
        ulb_name=meta.get("ulb_name"),
        ulb_details=meta.get("ulb_details"),
        dataset_mode=meta.get("dataset_mode", "cleaned"),
    )
    approval.save_draft(draft)
    session["draft_report_id"] = report_id
    session["draft_report_json"] = json.dumps(draft, default=str)

    return redirect(url_for("report_page"))


@app.route("/report")
def report_page():
    draft_json = session.get("draft_report_json")
    if not draft_json:
        flash("No draft report. Run a search and generate a report first.", "info")
        return redirect(url_for("home"))

    draft = json.loads(draft_json)
    current_status = approval.get_report_status(draft["Report_ID"]) or "DRAFT"
    draft["Approval_Status"] = current_status

    return render_template("report.html", report=draft, status=current_status)


@app.route("/approve/<report_id>", methods=["POST"])
def approve(report_id: str):
    user = session.get("user")
    default_name = f"{user['full_name']} ({user['role']})" if user else "Anonymous Reviewer"
    reviewer = request.form.get("reviewer", "").strip() or default_name
    approval.approve_report(report_id, reviewer)
    flash(f"✅ Report {report_id} approved by {reviewer}.", "success")

    # Refresh session draft
    loaded = approval.load_report_json(report_id)
    if loaded:
        loaded["Approval_Status"] = "APPROVED"
        loaded["Approved_By"] = reviewer
        session["draft_report_json"] = json.dumps(loaded, default=str)

    return redirect(url_for("report_page"))


# ---------------------------------------------------------------------------
# Authentication routes
# ---------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.args.get("next") or request.form.get("next") or url_for("home")

    if request.method == "POST":
        action = request.form.get("action", "login")

        if action == "register":
            username = request.form.get("reg_username", "").strip()
            password = request.form.get("reg_password", "")
            full_name = request.form.get("reg_full_name", "").strip()
            role = request.form.get("reg_role", "Public Citizen / Researcher")
            department = request.form.get("reg_department", "").strip()
            email = request.form.get("reg_email", "").strip()

            success, msg = auth.register_user(
                username=username,
                password=password,
                full_name=full_name,
                role=role,
                department=department,
                email=email,
            )
            if success:
                flash(f"✅ {msg}", "success")
                user = auth.authenticate_user(username, password)
                if user:
                    session["user"] = user
                    role_url = get_role_dashboard_url(user.get("role", ""))
                    target = request.args.get("next") or request.form.get("next")
                    if not target or target in ("/", url_for("home"), url_for("login")):
                        target = role_url
                    return redirect(target)
                return redirect(url_for("login"))
            else:
                flash(f"⛔ {msg}", "error")
                return render_template("login.html", active_tab="register", next_url=next_url)

        # Standard login
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = auth.authenticate_user(username, password)
        if user:
            session["user"] = user
            flash(f"👋 Welcome back, {user['full_name']} ({user['role']})!", "success")
            role_url = get_role_dashboard_url(user.get("role", ""))
            target = request.args.get("next") or request.form.get("next")
            if not target or target in ("/", url_for("home"), url_for("login")):
                target = role_url
            return redirect(target)
        else:
            flash("⛔ Invalid username or password. Please verify your credentials or create a new user account.", "error")
            return render_template("login.html", active_tab="login", next_url=next_url)


    # GET request
    active_tab = request.args.get("tab", "login")
    return render_template("login.html", active_tab=active_tab, next_url=next_url)


@app.route("/logout")
def logout():
    user = session.pop("user", None)
    if user:
        flash(f"👋 You have been logged out. Have a great day, {user['full_name']}!", "info")
    else:
        flash("You are already logged out.", "info")
    return redirect(url_for("home"))


@app.route("/reject/<report_id>", methods=["POST"])
def reject(report_id: str):
    reason = request.form.get("reason", "").strip()
    approval.reject_report(report_id, reason)
    flash(f"❌ Report {report_id} rejected.", "warning")

    loaded = approval.load_report_json(report_id)
    if loaded:
        loaded["Approval_Status"] = "REJECTED"
        session["draft_report_json"] = json.dumps(loaded, default=str)

    return redirect(url_for("report_page"))


@app.route("/history")
def history():
    reports = approval.get_all_reports(limit=100)
    return render_template("history.html", reports=reports)


@app.route("/history/load/<report_id>")
def load_report(report_id: str):
    loaded = approval.load_report_json(report_id)
    if not loaded:
        flash("Report not found.", "error")
        return redirect(url_for("history"))
    session["draft_report_json"] = json.dumps(loaded, default=str)
    session["draft_report_id"] = report_id
    return redirect(url_for("report_page"))


@app.route("/download/results")
def download_results():
    records_json = session.get("records_json")
    meta = session.get("search_result_meta")
    if not records_json:
        flash("No results to download.", "error")
        return redirect(url_for("results"))

    records = pd.read_json(io.StringIO(records_json), orient="split")
    # Only show param cols + metadata cols
    param_cols = meta.get("param_cols_used", []) if meta else []
    csv_bytes = records.to_csv(index=False).encode("utf-8")

    buf = io.BytesIO(csv_bytes)
    buf.seek(0)
    return send_file(
        buf,
        mimetype="text/csv",
        as_attachment=True,
        download_name="water_quality_results.csv",
    )


@app.route("/download/report")
def download_report():
    draft_json = session.get("draft_report_json")
    records_json = session.get("records_json")
    if not draft_json:
        flash("No report to download.", "error")
        return redirect(url_for("report_page"))

    draft = json.loads(draft_json)
    records = pd.read_json(io.StringIO(records_json), orient="split") if records_json else pd.DataFrame()

    report_df = report_generator.report_to_dataframe(draft, records)
    csv_bytes = report_df.to_csv(index=False).encode("utf-8")

    buf = io.BytesIO(csv_bytes)
    buf.seek(0)
    return send_file(
        buf,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"report_{draft['Report_ID']}.csv",
    )


@app.route("/api/dataset-info")
def api_dataset_info():
    """JSON endpoint for dataset stats."""
    df, profile, error = _get_data()
    if error:
        return jsonify({"error": error}), 503
    return jsonify({
        "total_rows": profile.total_rows,
        "param_cols": profile.param_cols,
        "district_col": profile.district_col,
        "station_col": profile.station_col,
        "date_col": profile.date_col_raw,
        "empty_cols": profile.completely_empty_cols,
    })


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_coord_col(df: pd.DataFrame, kind: str) -> str | None:
    targets = ["lat", "latitude"] if kind == "lat" else ["lon", "lng", "longitude"]
    for col in df.columns:
        if col.lower() in targets:
            return col
    return None


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
