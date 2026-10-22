"""
approval.py
===========
Manage the human approval workflow for generated reports.

Stores report status in a local SQLite database so approvals
persist across application restarts.

Approval states:
    DRAFT              – newly created, awaiting human review
    APPROVED           – human explicitly approved
    REJECTED           – human explicitly rejected
    REVISION_PENDING   – human requested changes
"""

from __future__ import annotations
import json
import logging
import os
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)

# Database file location (in the outputs/ directory)
_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(_BASE_DIR, "outputs", "reports.db")


# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

def _get_connection() -> sqlite3.Connection:
    """Return an open SQLite connection, creating the DB if needed."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _create_tables(conn)
    return conn


def _create_tables(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            report_id       TEXT PRIMARY KEY,
            district        TEXT,
            station         TEXT,
            ward_input      TEXT,
            period          TEXT,
            generated_at    TEXT,
            approval_status TEXT DEFAULT 'DRAFT',
            approved_by     TEXT,
            approved_at     TEXT,
            rejection_reason TEXT,
            report_json     TEXT
        )
    """)
    conn.commit()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def save_draft(report: dict) -> None:
    """
    Persist a draft report to the SQLite database.

    If a report with the same ID already exists, it is updated.
    """
    conn = _get_connection()
    try:
        conn.execute("""
            INSERT INTO reports
                (report_id, district, station, ward_input, period,
                 generated_at, approval_status, report_json)
            VALUES (?, ?, ?, ?, ?, ?, 'DRAFT', ?)
            ON CONFLICT(report_id) DO UPDATE SET
                report_json     = excluded.report_json,
                approval_status = 'DRAFT'
        """, (
            report["Report_ID"],
            report.get("District", ""),
            report.get("Station", ""),
            report.get("Ward_Input", ""),
            report.get("Period_Requested", ""),
            report.get("Generated_At", ""),
            json.dumps(report, default=str),
        ))
        conn.commit()
        logger.info("Saved draft report: %s", report["Report_ID"])
    finally:
        conn.close()


def approve_report(report_id: str, approved_by: str = "Anonymous Reviewer") -> bool:
    """
    Mark a report as APPROVED.

    Returns True if the report was found and updated.
    """
    conn = _get_connection()
    try:
        approved_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        cur = conn.execute("""
            UPDATE reports
            SET approval_status = 'APPROVED',
                approved_by     = ?,
                approved_at     = ?,
                rejection_reason = NULL
            WHERE report_id = ?
        """, (approved_by, approved_at, report_id))
        conn.commit()
        updated = cur.rowcount > 0
        if updated:
            logger.info("Report %s APPROVED by %s at %s",
                        report_id, approved_by, approved_at)
        return updated
    finally:
        conn.close()


def reject_report(report_id: str, reason: str = "") -> bool:
    """
    Mark a report as REJECTED with an optional reason.

    Returns True if the report was found and updated.
    """
    conn = _get_connection()
    try:
        rejected_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        cur = conn.execute("""
            UPDATE reports
            SET approval_status  = 'REJECTED',
                rejection_reason = ?,
                approved_at      = ?,
                approved_by      = NULL
            WHERE report_id = ?
        """, (reason, rejected_at, report_id))
        conn.commit()
        updated = cur.rowcount > 0
        if updated:
            logger.info("Report %s REJECTED. Reason: %s", report_id, reason)
        return updated
    finally:
        conn.close()


def get_report_status(report_id: str) -> str | None:
    """Return the current approval status of a report, or None if not found."""
    conn = _get_connection()
    try:
        cur = conn.execute(
            "SELECT approval_status FROM reports WHERE report_id = ?",
            (report_id,)
        )
        row = cur.fetchone()
        return row["approval_status"] if row else None
    finally:
        conn.close()


def get_all_reports(limit: int = 50) -> list[dict]:
    """Return the most recent *limit* reports as a list of dicts."""
    conn = _get_connection()
    try:
        cur = conn.execute("""
            SELECT report_id, district, station, ward_input, period,
                   generated_at, approval_status, approved_by, approved_at,
                   rejection_reason
            FROM reports
            ORDER BY generated_at DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def get_reports_by_status(status: str, limit: int = 50) -> list[dict]:
    """Return reports filtered by approval status ('DRAFT', 'APPROVED', 'REJECTED')."""
    conn = _get_connection()
    try:
        cur = conn.execute("""
            SELECT report_id, district, station, ward_input, period,
                   generated_at, approval_status, approved_by, approved_at,
                   rejection_reason
            FROM reports
            WHERE approval_status = ?
            ORDER BY generated_at DESC
            LIMIT ?
        """, (status, limit))
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def get_approval_stats() -> dict:
    """Return counts for DRAFT, APPROVED, REJECTED, and TOTAL reports."""
    conn = _get_connection()
    try:
        cur = conn.execute("""
            SELECT
                SUM(CASE WHEN approval_status = 'DRAFT' THEN 1 ELSE 0 END) as drafts,
                SUM(CASE WHEN approval_status = 'APPROVED' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN approval_status = 'REJECTED' THEN 1 ELSE 0 END) as rejected,
                COUNT(*) as total
            FROM reports
        """)
        row = cur.fetchone()
        return {
            "drafts": row["drafts"] or 0,
            "approved": row["approved"] or 0,
            "rejected": row["rejected"] or 0,
            "total": row["total"] or 0,
        }
    finally:
        conn.close()



def load_report_json(report_id: str) -> dict | None:
    """Load the full report JSON for a given report ID."""
    conn = _get_connection()
    try:
        cur = conn.execute(
            "SELECT report_json FROM reports WHERE report_id = ?",
            (report_id,)
        )
        row = cur.fetchone()
        if row and row["report_json"]:
            return json.loads(row["report_json"])
        return None
    finally:
        conn.close()
