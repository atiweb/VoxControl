"""Tests for the VoiceEngine."""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.i18n import set_language
from src.core.engine import VoiceEngine


@pytest.fixture
def engine():
    """Create an engine with mocked sub-components."""
    set_language("en")
    config = {
        "ai": {"backend": "offline", "fallback": "", "min_confidence": 0.6, "confirm_risky_actions": True},
        "stt": {"engine": "faster-whisper", "whisper": {"model_size": "tiny"}},
        "voice_response": {"enabled": False},
    }
    e = VoiceEngine(config)

    # Mock all sub-modules to avoid real hardware/API interaction
    e._transcriber = MagicMock()
    e._intent_parser = MagicMock()
    e._dispatcher = MagicMock()
    e._speaker = MagicMock()

    return e


class TestProcessText:
    def test_basic_command(self, engine):
        engine._intent_parser.parse.return_value = {
            "action": "system.open_app",
            "params": {"app": "calc"},
            "confidence": 0.9,
            "response_text": "Opening calculator.",
            "requires_confirmation": False,
        }
        engine._dispatcher.dispatch.return_value = "Done."

        result = engine.process_text("open calculator")
        assert result == "Opening calculator."
        engine._intent_parser.parse.assert_called_once_with("open calculator")
        engine._dispatcher.dispatch.assert_called_once()

    def test_low_confidence_asks_confirmation(self, engine):
        engine._intent_parser.parse.return_value = {
            "action": "system.open_app",
            "params": {"app": "calc"},
            "confidence": 0.4,  # below 0.6 threshold
            "response_text": "Opening calculator?",
            "requires_confirmation": False,
        }
        result = engine.process_text("maybe calculator")
        # Should NOT dispatch, should ask for confirmation
        engine._dispatcher.dispatch.assert_not_called()
        assert engine._pending_confirmation is not None

    def test_risky_action_asks_confirmation(self, engine):
        engine._intent_parser.parse.return_value = {
            "action": "system.shutdown",
            "params": {},
            "confidence": 0.95,
            "response_text": "Shutting down...",
            "requires_confirmation": True,
        }
        result = engine.process_text("shutdown")
        engine._dispatcher.dispatch.assert_not_called()
        assert engine._pending_confirmation is not None


class TestConfirmationFlow:
    def test_confirm_executes(self, engine):
        # Set up pending confirmation
        engine._pending_confirmation = {
            "intent": {
                "action": "system.shutdown",
                "params": {},
                "confidence": 0.95,
                "response_text": "Shutting down...",
            },
            "original": "shutdown",
        }
        engine._intent_parser.check_confirmation.return_value = True
        engine._dispatcher.dispatch.return_value = "System shutting down."

        result = engine.process_text("yes")
        engine._dispatcher.dispatch.assert_called_once()
        assert engine._pending_confirmation is None  # cleared

    def test_cancel_does_not_execute(self, engine):
        engine._pending_confirmation = {
            "intent": {
                "action": "system.shutdown",
                "params": {},
                "confidence": 0.95,
                "response_text": "Shutting down...",
            },
            "original": "shutdown",
        }
        engine._intent_parser.check_confirmation.return_value = False

        result = engine.process_text("no")
        engine._dispatcher.dispatch.assert_not_called()
        assert engine._pending_confirmation is None


class TestProcessAudio:
    def test_audio_with_no_transcription(self, engine):
        engine._transcriber.transcribe.return_value = None
        result = engine.process_audio(b"fake_audio_data")
        assert result is None

    def test_audio_with_transcription(self, engine):
        engine._transcriber.transcribe.return_value = "open calculator"
        engine._intent_parser.parse.return_value = {
            "action": "system.open_app",
            "params": {"app": "calc"},
            "confidence": 0.9,
            "response_text": "Opening calculator.",
            "requires_confirmation": False,
        }
        engine._dispatcher.dispatch.return_value = "Done."

        result = engine.process_audio(b"fake_audio_data")
        assert result == "Opening calculator."

    def test_audio_with_no_transcriber(self, engine):
        engine._transcriber = None
        result = engine.process_audio(b"fake_audio_data")
        assert result is None


class TestSpeaker:
    def test_speak_called_on_success(self, engine):
        engine._intent_parser.parse.return_value = {
            "action": "system.open_app",
            "params": {"app": "calc"},
            "confidence": 0.9,
            "response_text": "Opening calculator.",
            "requires_confirmation": False,
        }
        engine._dispatcher.dispatch.return_value = "Done."

        engine.process_text("open calculator")
        engine._speaker.say.assert_called()

    def test_no_speaker_doesnt_crash(self, engine):
        engine._speaker = None
        engine._intent_parser.parse.return_value = {
            "action": "system.open_app",
            "params": {"app": "calc"},
            "confidence": 0.9,
            "response_text": "Opening calculator.",
            "requires_confirmation": False,
        }
        engine._dispatcher.dispatch.return_value = "Done."
        # Should not raise
        result = engine.process_text("open calculator")
        assert result is not None
