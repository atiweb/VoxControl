"""Tests for the validation module."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.validation import (
    validate_action, is_risky_action, sanitize_text_input,
    validate_url, validate_path, validate_config, VALID_ACTIONS,
)


class TestValidateAction:
    def test_valid_system_action(self):
        assert validate_action("system.open_app") is True

    def test_valid_browser_action(self):
        assert validate_action("browser.search") is True

    def test_valid_keyboard_action(self):
        assert validate_action("keyboard.type") is True

    def test_valid_media_action(self):
        assert validate_action("media.play_pause") is True

    def test_valid_files_action(self):
        assert validate_action("files.open_folder") is True

    def test_valid_whatsapp_action(self):
        assert validate_action("whatsapp.open") is True

    def test_valid_office_action(self):
        assert validate_action("office.word.open") is True

    def test_valid_mouse_action(self):
        assert validate_action("mouse.click") is True

    def test_unknown_action_passes(self):
        assert validate_action("unknown") is True

    def test_empty_action_passes(self):
        assert validate_action("") is True

    def test_invalid_prefix(self):
        assert validate_action("hacker.delete_all") is False

    def test_invalid_sub_action(self):
        assert validate_action("system.format_disk") is False

    def test_no_dot_separator(self):
        assert validate_action("systemshutdown") is False

    def test_sql_injection_attempt(self):
        assert validate_action("system.open_app; DROP TABLE") is False


class TestIsRiskyAction:
    def test_shutdown_is_risky(self):
        assert is_risky_action("system.shutdown") is True

    def test_restart_is_risky(self):
        assert is_risky_action("system.restart") is True

    def test_delete_is_risky(self):
        assert is_risky_action("files.delete") is True

    def test_open_app_not_risky(self):
        assert is_risky_action("system.open_app") is False

    def test_browser_search_not_risky(self):
        assert is_risky_action("browser.search") is False


class TestSanitizeTextInput:
    def test_normal_text(self):
        assert sanitize_text_input("open chrome") == "open chrome"

    def test_strips_whitespace(self):
        assert sanitize_text_input("  open chrome  ") == "open chrome"

    def test_removes_control_chars(self):
        assert sanitize_text_input("open\x00chrome") == "openchrome"

    def test_max_length(self):
        long_text = "a" * 1000
        result = sanitize_text_input(long_text, max_length=500)
        assert len(result) == 500

    def test_empty_string(self):
        assert sanitize_text_input("") == ""

    def test_none_returns_empty(self):
        assert sanitize_text_input(None) == ""


class TestValidateUrl:
    def test_http_url(self):
        assert validate_url("http://example.com") is True

    def test_https_url(self):
        assert validate_url("https://example.com") is True

    def test_no_scheme(self):
        assert validate_url("example.com") is False

    def test_ftp_scheme(self):
        assert validate_url("ftp://example.com") is False

    def test_javascript_scheme(self):
        assert validate_url("javascript:alert(1)") is False

    def test_empty_url(self):
        assert validate_url("") is False

    def test_file_scheme(self):
        assert validate_url("file:///etc/passwd") is False


class TestValidatePath:
    def test_normal_path(self):
        assert validate_path("C:\\Users\\test\\Documents") is True

    def test_env_var_path(self):
        assert validate_path("%USERPROFILE%\\Documents") is True

    def test_traversal_blocked(self):
        assert validate_path("..\\..\\etc\\passwd") is False

    def test_traversal_in_middle(self):
        assert validate_path("C:\\Users\\..\\admin") is False

    def test_empty_path(self):
        assert validate_path("") is False


class TestValidateConfig:
    def test_valid_config(self):
        config = {
            "app": {"language": "en-US"},
            "ai": {"backend": "claude", "fallback": "openai", "min_confidence": 0.6},
            "stt": {"engine": "faster-whisper"},
            "remote": {"port": 8765},
            "voice_response": {"volume": 0.9},
        }
        errors = validate_config(config)
        assert len(errors) == 0

    def test_invalid_language(self):
        config = {"app": {"language": "xx-YY"}}
        errors = validate_config(config)
        assert any("language" in e.lower() for e in errors)

    def test_invalid_backend(self):
        config = {"ai": {"backend": "gpt5"}}
        errors = validate_config(config)
        assert any("backend" in e.lower() for e in errors)

    def test_invalid_confidence(self):
        config = {"ai": {"min_confidence": 1.5}}
        errors = validate_config(config)
        assert any("confidence" in e.lower() for e in errors)

    def test_invalid_port(self):
        config = {"remote": {"port": 99999}}
        errors = validate_config(config)
        assert any("port" in e.lower() for e in errors)

    def test_invalid_volume(self):
        config = {"voice_response": {"volume": 2.0}}
        errors = validate_config(config)
        assert any("volume" in e.lower() for e in errors)

    def test_empty_config_no_errors(self):
        errors = validate_config({})
        assert len(errors) == 0


class TestActionWhitelistCompleteness:
    """Ensure the whitelist covers all documented actions."""

    def test_all_prefixes_exist(self):
        expected = {"system", "browser", "whatsapp", "office", "files", "media", "keyboard", "mouse"}
        assert set(VALID_ACTIONS.keys()) == expected

    def test_system_has_core_actions(self):
        core = {"open_app", "close_app", "shutdown", "restart", "screenshot", "volume_up", "lock_screen"}
        assert core.issubset(VALID_ACTIONS["system"])

    def test_browser_has_core_actions(self):
        core = {"open", "search", "new_tab", "close_tab", "refresh"}
        assert core.issubset(VALID_ACTIONS["browser"])
