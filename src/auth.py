"""
auth.py
=======
Authentication and User Management for Ward Water Quality Reporter.

Provides secure role-based access for:
- Environmental Officers (authorized to review and approve reports)
- Municipal Quality Inspectors
- CGWB Hydrologists
- Public Citizens and Researchers

Stores users with salted password hashes in SQLite (outputs/reports.db).
"""

from __future__ import annotations
import logging
import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)

_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(_BASE_DIR, "outputs", "reports.db")

AVAILABLE_ROLES = [
    "Environmental Officer",
    "Municipal Quality Inspector",
    "Senior Hydrologist",
    "Public Citizen / Researcher",
]

DEFAULT_USERS = [
    {
        "username": "officer",
        "password": "water2026",
        "full_name": "Dr. K. Ananthi",
        "role": "Environmental Officer",
        "department": "State Groundwater Authority, Tamil Nadu",
        "email": "ananthi.k@tn.gov.in",
    },
    {
        "username": "inspector",
        "password": "inspect2026",
        "full_name": "M. Senthil Kumar",
        "role": "Municipal Quality Inspector",
        "department": "Greater Chennai Corporation",
        "email": "senthil.k@chennaicorp.gov.in",
    },
    {
        "username": "hydrologist",
        "password": "cgwb2026",
        "full_name": "R. Meenakshi",
        "role": "Senior Hydrologist",
        "department": "Central Ground Water Board (CGWB)",
        "email": "meenakshi.r@cgwb.nic.in",
    },
    {
        "username": "citizen",
        "password": "citizen2026",
        "full_name": "Kavitha Sundaram",
        "role": "Public Citizen / Researcher",
        "department": "Community Water Watch",
        "email": "kavitha.waterwatch@gmail.com",
    },
]


def _get_connection() -> sqlite3.Connection:
    """Return an open SQLite connection with users table initialized."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _create_tables(conn)
    return conn


def _create_tables(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username        TEXT PRIMARY KEY,
            password_hash   TEXT NOT NULL,
            full_name       TEXT NOT NULL,
            role            TEXT NOT NULL,
            department      TEXT,
            email           TEXT,
            created_at      TEXT
        )
    """)
    conn.commit()
    _seed_default_users(conn)


def _seed_default_users(conn: sqlite3.Connection) -> None:
    """Seed initial demo accounts if table is empty."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count == 0:
        logger.info("Seeding default authentication accounts into SQLite...")
        for u in DEFAULT_USERS:
            pwd_hash = generate_password_hash(u["password"], method="pbkdf2:sha256")
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT OR IGNORE INTO users
                    (username, password_hash, full_name, role, department, email, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                u["username"],
                pwd_hash,
                u["full_name"],
                u["role"],
                u["department"],
                u["email"],
                now_str,
            ))
        conn.commit()


def authenticate_user(username: str, password: str) -> dict | None:
    """
    Validate username and password. Returns user dict on success, None on failure.
    """
    if not username or not password:
        return None

    username = username.strip().lower()
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE LOWER(username) = ?",
            (username,)
        ).fetchone()

        if not row:
            return None

        if check_password_hash(row["password_hash"], password):
            return {
                "username": row["username"],
                "full_name": row["full_name"],
                "role": row["role"],
                "department": row["department"],
                "email": row["email"],
                "is_reviewer": row["role"] in (
                    "Environmental Officer",
                    "Municipal Quality Inspector",
                    "Senior Hydrologist",
                ),
            }
        return None


def register_user(
    username: str,
    password: str,
    full_name: str,
    role: str,
    department: str = "",
    email: str = "",
) -> tuple[bool, str]:
    """
    Register a new user account.
    Returns (success, message).
    """
    username = username.strip().lower()
    full_name = full_name.strip()
    department = department.strip()
    email = email.strip()

    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters."
    if not password or len(password) < 4:
        return False, "Password must be at least 4 characters."
    # Normalize role name
    role_clean = role.strip()
    if role_clean in ("Officer", "Environmental Officer"):
        role = "Environmental Officer"
    elif role_clean in ("Inspector", "Municipal Quality Inspector"):
        role = "Municipal Quality Inspector"
    elif role_clean in ("Hydrologist", "Senior Hydrologist"):
        role = "Senior Hydrologist"
    elif role_clean in ("Citizen", "Public Citizen", "Public Citizen / Researcher"):
        role = "Public Citizen / Researcher"
    elif role_clean not in AVAILABLE_ROLES:
        role = "Public Citizen / Researcher"
    else:
        role = role_clean

    with _get_connection() as conn:
        existing = conn.execute(
            "SELECT 1 FROM users WHERE LOWER(username) = ?",
            (username,)
        ).fetchone()
        if existing:
            return False, f"Username '{username}' is already registered. Please choose another."

        pwd_hash = generate_password_hash(password, method="pbkdf2:sha256")
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn.execute("""
            INSERT INTO users
                (username, password_hash, full_name, role, department, email, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, pwd_hash, full_name, role, department, email, now_str))
        conn.commit()

    return True, "Account registered successfully! You can now log in."


def get_user(username: str) -> dict | None:
    """Retrieve user profile by username."""
    if not username:
        return None
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT username, full_name, role, department, email, created_at FROM users WHERE LOWER(username) = ?",
            (username.strip().lower(),)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        d["is_reviewer"] = d["role"] in (
            "Environmental Officer",
            "Municipal Quality Inspector",
            "Senior Hydrologist",
        )
        return d
