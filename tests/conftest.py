"""
Minimal mock/fixture module for tests.
Provides shared test utilities.
"""


def make_config(**overrides) -> dict:
    """Create a minimal test config dict."""
    config = {
        "app": {"language": "en-US"},
        "ai": {
            "backend": "offline",
            "fallback": "",
            "min_confidence": 0.6,
            "confirm_risky_actions": True,
        },
        "stt": {"engine": "faster-whisper", "whisper": {"model_size": "tiny", "language": "en"}},
        "voice_response": {"enabled": False},
        "browser": {"default": "chrome"},
        "remote": {
            "enabled": False,
            "port": 8765,
            "auth": {"enabled": False},
        },
        "wake_word": {"word": "computer", "aliases": ["hey computer"]},
    }
    config.update(overrides)
    return config
