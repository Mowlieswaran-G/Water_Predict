"""
test_auth.py
============
Unit and integration tests for authentication and reviewer authorization.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import uuid
from src import auth


class TestAuthentication:
    """Test login and user management."""

    def test_default_officer_login_success(self):
        user = auth.authenticate_user("officer", "water2026")
        assert user is not None
        assert user["username"] == "officer"
        assert user["role"] == "Environmental Officer"
        assert user["is_reviewer"] is True

    def test_default_inspector_login_success(self):
        user = auth.authenticate_user("inspector", "inspect2026")
        assert user is not None
        assert user["role"] == "Municipal Quality Inspector"
        assert user["is_reviewer"] is True

    def test_citizen_login_not_official_reviewer(self):
        user = auth.authenticate_user("citizen", "citizen2026")
        assert user is not None
        assert user["role"] == "Public Citizen / Researcher"
        assert user["is_reviewer"] is False

    def test_invalid_password_fails(self):
        user = auth.authenticate_user("officer", "wrongpassword")
        assert user is None

    def test_unknown_user_fails(self):
        user = auth.authenticate_user("nonexistent_user", "password")
        assert user is None

    def test_register_and_authenticate_new_user(self):
        import uuid
        uname = f"chemist_{uuid.uuid4().hex[:6]}"
        success, msg = auth.register_user(
            username=uname,
            password="testpassword123",
            full_name="Dr. Test Chemist",
            role="Environmental Officer",
            department="Water Lab",
            email="chemist@test.gov.in"
        )
        assert success is True

        # Test logging in as newly registered user
        user = auth.authenticate_user(uname, "testpassword123")
        assert user is not None
        assert user["full_name"] == "Dr. Test Chemist"
        assert user["is_reviewer"] is True


    def test_duplicate_registration_prevented(self):
        success, msg = auth.register_user(
            username="officer",
            password="water2026",
            full_name="Duplicate Officer",
            role="Environmental Officer"
        )
        assert success is False
        assert "already registered" in msg

    def test_shorthand_role_registration(self):
        uname = f"inspector_user_{uuid.uuid4().hex[:6]}"
        success, msg = auth.register_user(
            username=uname,
            password="inspectorpass123",
            full_name="Mr. S. Inspector",
            role="Inspector"
        )
        assert success is True
        user = auth.get_user(uname)
        assert user["role"] == "Municipal Quality Inspector"

    def test_login_page_renders_segmented_options_and_no_dummy_user_in_login(self):
        from app import app
        client = app.test_client()
        resp = client.get("/login")
        assert resp.status_code == 200
        html = resp.data.decode("utf-8")
        assert "tabBtnLogin" in html
        assert "tabBtnRegister" in html
        assert "Create User" in html
        assert "roleCardOfficer" in html
        assert "roleCardInspector" in html
        assert "roleCardHydrologist" in html
        assert "roleCardCitizen" in html
        # Dummy user auto-fill section should not be present
        assert "Or quick sign in as" not in html
        assert "demo-role-avatars" not in html
