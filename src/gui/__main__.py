"""
VoxControl GUI -- Entry point.

Usage:
  python -m src.gui                # Launch the GUI
  pythonw -m src.gui               # Launch without console window
"""

import sys
import os
from pathlib import Path

# Ensure project root is on path
project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def main():
    import logging
    import yaml

    # Load config
    from src.paths import resolve_config_path, ensure_user_data
    ensure_user_data()  # Copy defaults on first run (frozen exe)
    config_path = resolve_config_path("config/settings.yaml")
    config = {}
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

    # Load .env overrides
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    # Environment overrides (same logic as main.py)
    env_overrides = {
        "APP_LANGUAGE": ("app", "language"),
        "AI_BACKEND": ("ai", "backend"),
    }
    for env_key, path in env_overrides.items():
        val = os.getenv(env_key)
        if val:
            section, key = path
            config.setdefault(section, {})[key] = val

    # Setup logging
    from src.paths import get_logs_dir
    log_name = config.get("logging", {}).get("file", "logs/voxcontrol.log")
    log_file = str(get_logs_dir() / Path(log_name).name)
    level_str = config.get("logging", {}).get("level", "INFO")
    level = getattr(logging, level_str.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )

    # Import and launch GUI
    from src.gui.app import VoxControlApp

    app = VoxControlApp(config)
    app.mainloop()


if __name__ == "__main__":
    main()
