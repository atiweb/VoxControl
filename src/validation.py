"""
Input validation and action whitelist for VoxControl.
Prevents execution of unrecognized actions and sanitizes inputs.
"""

import logging
import os
import re
from typing import Optional

logger = logging.getLogger(__name__)

# ---- ACTION WHITELIST ----
# All valid action prefixes and their valid sub-actions
VALID_ACTIONS = {
    "system": {
        "open_app", "close_app", "switch_window", "minimize", "maximize",
        "restore", "show_desktop", "lock_screen", "shutdown", "restart",
        "sleep", "screenshot", "volume_up", "volume_down", "volume_mute",
        "volume_set", "brightness_up", "brightness_down", "do_not_disturb",
        "task_manager", "settings", "clipboard_history",
        "virtual_desktop_new", "virtual_desktop_switch",
    },
    "browser": {
        "open", "open_url", "search", "new_tab", "close_tab", "reopen_tab",
        "next_tab", "prev_tab", "go_back", "go_forward", "refresh",
        "scroll_up", "scroll_down", "scroll_top", "scroll_bottom",
        "zoom_in", "zoom_out", "zoom_reset", "bookmark", "find",
        "download", "fullscreen", "history", "incognito",
    },
    "whatsapp": {
        "open", "open_chat", "send_message", "search", "attach_file",
        "voice_note", "mark_read", "archive_chat", "mute_chat",
    },
    "office": {
        "word.open", "word.new", "word.save", "word.bold", "word.italic",
        "word.underline", "excel.open", "excel.new", "excel.save",
        "excel.auto_sum", "excel.create_chart", "ppt.open", "ppt.new",
        "ppt.save", "ppt.new_slide", "ppt.start_slideshow",
    },
    "files": {
        "open_explorer", "open_folder", "open_file", "new_folder",
        "rename", "delete", "copy", "cut", "paste", "search",
    },
    "media": {
        "play_pause", "next", "previous", "stop", "shuffle", "repeat",
        "open_spotify", "open_youtube",
    },
    "keyboard": {
        "type", "press", "hotkey", "copy", "paste", "undo", "redo",
        "cut", "save", "select_all",
    },
    "mouse": {
        "click", "double_click", "scroll",
    },
}

# Actions that are considered destructive/risky
RISKY_ACTIONS = {
    "system.shutdown", "system.restart", "system.sleep",
    "files.delete",
}


def validate_action(action: str) -> bool:
    """Check if an action is in the whitelist."""
    if not action or action == "unknown":
        return True  # unknown is handled by dispatcher

    parts = action.split(".", 1)
    if len(parts) < 2:
        return False

    prefix = parts[0]
    sub_action = parts[1]

    valid_subs = VALID_ACTIONS.get(prefix)
    if valid_subs is None:
        logger.warning(f"Unknown action prefix: '{prefix}'")
        return False

    if sub_action not in valid_subs:
        logger.warning(f"Unknown sub-action: '{sub_action}' for prefix '{prefix}'")
        return False

    return True


def is_risky_action(action: str) -> bool:
    """Check if action is considered risky/destructive."""
    return action in RISKY_ACTIONS


def sanitize_text_input(text: str, max_length: int = 500) -> str:
    """Sanitize text input: trim, limit length, remove control characters."""
    if not text:
        return ""
    # Remove control characters except newline/tab
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text.strip()[:max_length]


def validate_url(url: str) -> bool:
    """Basic URL validation — only allow http/https schemes."""
    if not url:
        return False
    return bool(re.match(r'^https?://', url, re.IGNORECASE))


def validate_path(path: str) -> bool:
    """Validate file path — prevent directory traversal."""
    if not path:
        return False
    # Expand environment variables for validation
    expanded = os.path.expandvars(path)
    normalized = os.path.normpath(expanded)
    # Block paths that try to escape common base directories
    if '..' in path:
        logger.warning(f"Path traversal attempt blocked: {path}")
        return False
    return True


def validate_config(config: dict) -> list[str]:
    """Validate configuration and return list of warnings/errors."""
    errors = []

    # App language
    app_lang = config.get("app", {}).get("language", "")
    if app_lang:
        lang_base = app_lang.split("-")[0].lower()
        if lang_base not in ("pt", "es", "en"):
            errors.append(f"Unsupported language: {app_lang}")

    # AI backend
    ai_config = config.get("ai", {})
    backend = ai_config.get("backend", "")
    if backend and backend not in ("claude", "openai", "offline"):
        errors.append(f"Invalid AI backend: {backend}")

    fallback = ai_config.get("fallback", "")
    if fallback and fallback not in ("claude", "openai", "offline", ""):
        errors.append(f"Invalid AI fallback: {fallback}")

    # Confidence threshold
    min_conf = ai_config.get("min_confidence", 0.6)
    if not 0.0 <= min_conf <= 1.0:
        errors.append(f"min_confidence must be 0.0–1.0, got {min_conf}")

    # STT engine
    stt_engine = config.get("stt", {}).get("engine", "")
    if stt_engine and stt_engine not in ("faster-whisper", "vosk"):
        errors.append(f"Invalid STT engine: {stt_engine}")

    # Remote port
    port = config.get("remote", {}).get("port", 8765)
    if not isinstance(port, int) or port < 1 or port > 65535:
        errors.append(f"Invalid port: {port}")

    # Voice volume
    volume = config.get("voice_response", {}).get("volume", 0.9)
    if not 0.0 <= volume <= 1.0:
        errors.append(f"Voice volume must be 0.0–1.0, got {volume}")

    return errors
