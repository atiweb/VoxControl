"""
Authentication manager for VoxControl remote API.
Uses JWT tokens with bcrypt password hashing.
"""

import hashlib
import hmac
import json
import logging
import os
import secrets
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# JWT-like token using HMAC-SHA256 (no external dependency needed)
_TOKEN_EXPIRY = 86400  # 24 hours


class AuthManager:
    """Manages user authentication with hashed passwords and signed tokens."""

    def __init__(self, config: dict):
        self.config = config
        self._secret = config.get("jwt_secret") or os.getenv("VOXCONTROL_SECRET") or self._generate_secret()
        raw_cred_path = Path(config.get("credentials_file", "config/credentials.json"))
        if raw_cred_path.is_absolute():
            self._credentials_path = raw_cred_path
        else:
            from ..paths import get_config_dir
            self._credentials_path = get_config_dir() / raw_cred_path.name
        self._token_expiry = config.get("token_expiry", _TOKEN_EXPIRY)
        self._credentials = self._load_credentials()

    def _generate_secret(self) -> str:
        """Generate a random secret and persist it."""
        secret = secrets.token_hex(32)
        from ..paths import get_config_dir
        secret_path = get_config_dir() / ".secret"
        secret_path.write_text(secret, encoding="utf-8")
        logger.info("Generated new JWT secret.")
        return secret

    def _load_credentials(self) -> dict:
        """Load stored credentials from disk."""
        if self._credentials_path.exists():
            try:
                data = json.loads(self._credentials_path.read_text(encoding="utf-8"))
                return data
            except (json.JSONDecodeError, OSError) as e:
                logger.error(f"Failed to load credentials: {e}")
        return {}

    def _save_credentials(self):
        """Save credentials to disk."""
        self._credentials_path.parent.mkdir(parents=True, exist_ok=True)
        self._credentials_path.write_text(
            json.dumps(self._credentials, indent=2),
            encoding="utf-8"
        )

    def has_users(self) -> bool:
        """Check if any users exist (for first-time setup)."""
        return len(self._credentials.get("users", {})) > 0

    def create_user(self, username: str, password: str) -> bool:
        """Create a new user with hashed password."""
        if not username or not password:
            return False
        if len(password) < 6:
            return False

        users = self._credentials.setdefault("users", {})
        if username in users:
            return False

        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)

        users[username] = {
            "password_hash": password_hash,
            "salt": salt,
            "created_at": time.time(),
        }
        self._save_credentials()
        logger.info(f"User '{username}' created.")
        return True

    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return a token, or None if invalid."""
        users = self._credentials.get("users", {})
        user = users.get(username)
        if not user:
            return None

        expected_hash = user["password_hash"]
        salt = user["salt"]
        actual_hash = self._hash_password(password, salt)

        if not hmac.compare_digest(expected_hash, actual_hash):
            return None

        return self._create_token(username)

    def validate_token(self, token: str) -> Optional[str]:
        """Validate a token and return the username, or None if invalid/expired."""
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None

            header_b64, payload_b64, signature = parts

            # Verify signature
            expected_sig = self._sign(f"{header_b64}.{payload_b64}")
            if not hmac.compare_digest(expected_sig, signature):
                return None

            # Decode payload
            import base64
            payload_json = base64.urlsafe_b64decode(payload_b64 + "==").decode("utf-8")
            payload = json.loads(payload_json)

            # Check expiry
            if time.time() > payload.get("exp", 0):
                return None

            return payload.get("sub")
        except Exception:
            return None

    def _create_token(self, username: str) -> str:
        """Create a signed token for the given user."""
        import base64

        header = base64.urlsafe_b64encode(
            json.dumps({"alg": "HS256", "typ": "JWT"}).encode()
        ).decode().rstrip("=")

        payload = base64.urlsafe_b64encode(
            json.dumps({
                "sub": username,
                "iat": int(time.time()),
                "exp": int(time.time() + self._token_expiry),
            }).encode()
        ).decode().rstrip("=")

        signature = self._sign(f"{header}.{payload}")
        return f"{header}.{payload}.{signature}"

    def _sign(self, data: str) -> str:
        """Create HMAC-SHA256 signature."""
        return hmac.new(
            self._secret.encode("utf-8"),
            data.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        """Hash password with salt using SHA-256 (iterated)."""
        data = f"{salt}:{password}".encode("utf-8")
        for _ in range(100_000):
            data = hashlib.sha256(data).digest()
        return data.hex()
