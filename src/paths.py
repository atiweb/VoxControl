"""
VoxControl -- Centralized path resolver.

When running from source:  paths resolve relative to the project root.
When running as a PyInstaller .exe:
  - Bundled resources (defaults) → sys._MEIPASS (temp dir)
  - User data (config, logs, models) → %APPDATA%/VoxControl
"""

import os
import sys
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

APP_NAME = "VoxControl"


def is_frozen() -> bool:
    """True when running inside a PyInstaller bundle."""
    return getattr(sys, "frozen", False)


def _project_root() -> Path:
    """Source-mode project root (directory containing src/)."""
    return Path(__file__).resolve().parent.parent


def _bundle_dir() -> Path:
    """PyInstaller temp directory where bundled data files live."""
    return Path(getattr(sys, "_MEIPASS", _project_root()))


def get_data_dir() -> Path:
    """User-writable data directory. Created if it doesn't exist.

    Frozen  → %APPDATA%/VoxControl
    Source  → project root
    """
    if is_frozen():
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        data = base / APP_NAME
    else:
        data = _project_root()

    data.mkdir(parents=True, exist_ok=True)
    return data


def get_config_dir() -> Path:
    d = get_data_dir() / "config"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_logs_dir() -> Path:
    d = get_data_dir() / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_models_dir() -> Path:
    d = get_data_dir() / "models"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_bundled_resource(relative: str) -> Path:
    """Resolve a path inside the PyInstaller bundle (or project root in source mode)."""
    return _bundle_dir() / relative


def get_static_dir() -> Path:
    """Static files for the remote web UI (bundled with the exe)."""
    return get_bundled_resource("src") / "remote" / "static"


# ── First-run initialization ───────────────────────────────────────

_DEFAULT_CONFIGS = [
    "config/settings.yaml",
    "config/custom_commands.yaml",
]


def ensure_user_data():
    """Copy default config files to user data dir on first run.

    Only copies files that don't already exist so user edits are preserved.
    """
    if not is_frozen():
        return  # nothing to do in source mode

    data = get_data_dir()
    bundle = _bundle_dir()

    for rel in _DEFAULT_CONFIGS:
        src = bundle / rel
        dst = data / rel
        if src.exists() and not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            logger.info("Created default %s", rel)


def resolve_config_path(relative: str) -> Path:
    """Resolve a config-relative path, checking user data first then bundle."""
    user_path = get_data_dir() / relative
    if user_path.exists():
        return user_path
    # Fallback to bundled default
    return get_bundled_resource(relative)
