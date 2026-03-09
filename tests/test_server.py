"""Tests for the remote API server."""

import pytest
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from src.i18n import set_language
from src.remote.server import app, set_engine, set_server_lang, _verify_token
import src.remote.server as server_module


@pytest.fixture(autouse=True)
def setup_server():
    """Setup server state for each test."""
    set_language("en")
    set_server_lang("en")
    # Disable auth for most tests
    server_module._auth_required = False
    server_module._auth = None
    yield
    # Cleanup
    server_module._engine = None
    server_module._connections = {}


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_engine():
    engine = MagicMock()
    engine.process_text.return_value = "Done."
    set_engine(engine)
    return engine


class TestPublicEndpoints:
    def test_index_returns_html(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "VoxControl" in response.text

    def test_auth_status(self, client):
        response = client.get("/api/auth/status")
        assert response.status_code == 200
        data = response.json()
        assert "auth_required" in data
        assert "version" in data


class TestCommandAPI:
    def test_command_success(self, client, mock_engine):
        response = client.post("/api/command", json={"text": "open chrome"})
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Done."
        mock_engine.process_text.assert_called_once_with("open chrome")

    def test_command_no_engine(self, client):
        # Engine not set
        server_module._engine = None
        response = client.post("/api/command", json={"text": "open chrome"})
        assert response.status_code == 503

    def test_command_empty_text(self, client, mock_engine):
        response = client.post("/api/command", json={"text": ""})
        assert response.status_code == 422  # pydantic validation


class TestStatusAPI:
    def test_status_online(self, client, mock_engine):
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert data["engine_ready"] is True
        assert "strings" in data

    def test_status_language(self, client, mock_engine):
        set_server_lang("es")
        response = client.get("/api/status")
        data = response.json()
        assert data["language"] == "es"


class TestActionsAPI:
    def test_actions_list(self, client, mock_engine):
        response = client.get("/api/actions")
        assert response.status_code == 200
        data = response.json()
        assert "actions" in data
        assert "system.open_app" in data["actions"]
        assert "browser.search" in data["actions"]
        assert len(data["actions"]) > 50


class TestAuthFlow:
    @pytest.fixture(autouse=True)
    def setup_auth(self, tmp_path):
        """Enable auth for these tests."""
        from src.auth.auth import AuthManager
        config = {
            "credentials_file": str(tmp_path / "credentials.json"),
            "jwt_secret": "test-secret",
            "token_expiry": 3600,
        }
        server_module._auth = AuthManager(config)
        server_module._auth_required = True
        yield
        server_module._auth_required = False

    def test_register_first_user(self, client):
        response = client.post("/api/auth/register", json={
            "username": "admin",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["username"] == "admin"

    def test_register_blocked_after_first(self, client):
        client.post("/api/auth/register", json={"username": "admin", "password": "password123"})
        response = client.post("/api/auth/register", json={"username": "hacker", "password": "password123"})
        assert response.status_code == 403

    def test_login_valid(self, client):
        client.post("/api/auth/register", json={"username": "admin", "password": "password123"})
        response = client.post("/api/auth/login", json={"username": "admin", "password": "password123"})
        assert response.status_code == 200
        assert "token" in response.json()

    def test_login_invalid(self, client):
        client.post("/api/auth/register", json={"username": "admin", "password": "password123"})
        response = client.post("/api/auth/login", json={"username": "admin", "password": "wrongpassword"})
        assert response.status_code == 401

    def test_command_requires_auth(self, client):
        mock_engine = MagicMock()
        mock_engine.process_text.return_value = "Done."
        set_engine(mock_engine)

        # Without token
        response = client.post("/api/command", json={"text": "open chrome"})
        assert response.status_code == 401

    def test_command_with_token(self, client):
        mock_engine = MagicMock()
        mock_engine.process_text.return_value = "Done."
        set_engine(mock_engine)

        # Register and login
        reg = client.post("/api/auth/register", json={"username": "admin", "password": "password123"})
        token = reg.json()["token"]

        response = client.post(
            "/api/command",
            json={"text": "open chrome"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["response"] == "Done."


class TestWebSocket:
    def test_ws_text_command(self, client, mock_engine):
        with client.websocket_connect("/ws") as ws:
            # Receive config
            data = json.loads(ws.receive_text())
            assert data["type"] == "config"
            # Receive status
            data = json.loads(ws.receive_text())
            assert data["type"] == "status"
            # Send command
            ws.send_text(json.dumps({"type": "text", "data": "open chrome"}))
            data = json.loads(ws.receive_text())
            assert data["type"] == "response"
            assert data["data"] == "Done."

    def test_ws_ping_pong(self, client, mock_engine):
        with client.websocket_connect("/ws") as ws:
            ws.receive_text()  # config
            ws.receive_text()  # status
            ws.send_text(json.dumps({"type": "ping"}))
            data = json.loads(ws.receive_text())
            assert data["type"] == "pong"


class TestRateLimiting:
    def test_rate_limiter_allows(self):
        from src.auth.middleware import RateLimiter
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        for _ in range(5):
            assert limiter.is_allowed("192.168.1.1") is True
        assert limiter.is_allowed("192.168.1.1") is False

    def test_rate_limiter_different_ips(self):
        from src.auth.middleware import RateLimiter
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        assert limiter.is_allowed("192.168.1.1") is True
        assert limiter.is_allowed("192.168.1.1") is True
        assert limiter.is_allowed("192.168.1.1") is False
        assert limiter.is_allowed("192.168.1.2") is True  # different IP

    def test_rate_limiter_remaining(self):
        from src.auth.middleware import RateLimiter
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        assert limiter.get_remaining("192.168.1.1") == 10
        limiter.is_allowed("192.168.1.1")
        assert limiter.get_remaining("192.168.1.1") == 9
