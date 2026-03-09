"""Tests for the AuthManager."""

import pytest
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.auth.auth import AuthManager


@pytest.fixture
def auth_dir(tmp_path):
    """Provide a temp directory for auth files."""
    return tmp_path


@pytest.fixture
def auth(auth_dir):
    """Create an AuthManager with temp storage."""
    config = {
        "credentials_file": str(auth_dir / "credentials.json"),
        "jwt_secret": "test-secret-key-12345",
        "token_expiry": 3600,
    }
    return AuthManager(config)


class TestUserCreation:
    def test_create_user(self, auth):
        assert auth.create_user("admin", "password123") is True

    def test_create_duplicate_user_fails(self, auth):
        auth.create_user("admin", "password123")
        assert auth.create_user("admin", "otherpass") is False

    def test_create_user_short_password_fails(self, auth):
        assert auth.create_user("admin", "123") is False

    def test_create_user_empty_username_fails(self, auth):
        assert auth.create_user("", "password123") is False

    def test_create_user_empty_password_fails(self, auth):
        assert auth.create_user("admin", "") is False

    def test_has_users_initially_false(self, auth):
        assert auth.has_users() is False

    def test_has_users_after_creation(self, auth):
        auth.create_user("admin", "password123")
        assert auth.has_users() is True


class TestAuthentication:
    def test_authenticate_valid(self, auth):
        auth.create_user("admin", "password123")
        token = auth.authenticate("admin", "password123")
        assert token is not None
        assert len(token) > 20

    def test_authenticate_invalid_password(self, auth):
        auth.create_user("admin", "password123")
        token = auth.authenticate("admin", "wrongpassword")
        assert token is None

    def test_authenticate_nonexistent_user(self, auth):
        token = auth.authenticate("nobody", "password123")
        assert token is None


class TestTokenValidation:
    def test_valid_token(self, auth):
        auth.create_user("admin", "password123")
        token = auth.authenticate("admin", "password123")
        username = auth.validate_token(token)
        assert username == "admin"

    def test_invalid_token(self, auth):
        assert auth.validate_token("invalid.token.here") is None

    def test_empty_token(self, auth):
        assert auth.validate_token("") is None

    def test_tampered_token(self, auth):
        auth.create_user("admin", "password123")
        token = auth.authenticate("admin", "password123")
        # Tamper with the token
        parts = token.split(".")
        parts[2] = "tampered_signature"
        tampered = ".".join(parts)
        assert auth.validate_token(tampered) is None

    def test_expired_token(self, auth_dir):
        config = {
            "credentials_file": str(auth_dir / "credentials.json"),
            "jwt_secret": "test-secret-key-12345",
            "token_expiry": -1,  # already expired
        }
        auth = AuthManager(config)
        auth.create_user("admin", "password123")
        token = auth.authenticate("admin", "password123")
        assert auth.validate_token(token) is None


class TestPersistence:
    def test_credentials_survive_reload(self, auth_dir):
        config = {
            "credentials_file": str(auth_dir / "credentials.json"),
            "jwt_secret": "test-secret-key-12345",
            "token_expiry": 3600,
        }
        auth1 = AuthManager(config)
        auth1.create_user("admin", "password123")

        # Reload
        auth2 = AuthManager(config)
        assert auth2.has_users() is True
        token = auth2.authenticate("admin", "password123")
        assert token is not None
