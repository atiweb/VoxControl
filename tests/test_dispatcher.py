"""Tests for the ActionDispatcher."""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.i18n import set_language
from src.actions.dispatcher import ActionDispatcher


@pytest.fixture
def dispatcher():
    """Create a dispatcher with mocked handlers."""
    set_language("en")
    config = {"custom_commands_path": "nonexistent.yaml"}
    d = ActionDispatcher(config)
    # Mock all handlers to avoid real system interaction
    d._system = MagicMock()
    d._browser = MagicMock()
    d._whatsapp = MagicMock()
    d._office = MagicMock()
    d._files = MagicMock()
    d._media = MagicMock()
    d._keyboard = MagicMock()
    # Default return value
    for handler in [d._system, d._browser, d._whatsapp, d._office, d._files, d._media, d._keyboard]:
        handler.execute.return_value = "Done."
    return d


class TestDispatchRouting:
    def test_routes_to_system(self, dispatcher):
        intent = {"action": "system.open_app", "params": {"app": "calc"}, "response_text": "Opening calc"}
        dispatcher.dispatch(intent)
        dispatcher._system.execute.assert_called_once_with("system.open_app", {"app": "calc"})

    def test_routes_to_browser(self, dispatcher):
        intent = {"action": "browser.search", "params": {"query": "test"}, "response_text": "Searching"}
        dispatcher.dispatch(intent)
        dispatcher._browser.execute.assert_called_once_with("browser.search", {"query": "test"})

    def test_routes_to_whatsapp(self, dispatcher):
        intent = {"action": "whatsapp.open", "params": {}, "response_text": "Opening WhatsApp"}
        dispatcher.dispatch(intent)
        dispatcher._whatsapp.execute.assert_called_once()

    def test_routes_to_office(self, dispatcher):
        intent = {"action": "office.word.open", "params": {}, "response_text": "Opening Word"}
        dispatcher.dispatch(intent)
        dispatcher._office.execute.assert_called_once()

    def test_routes_to_files(self, dispatcher):
        intent = {"action": "files.open_folder", "params": {"path": "Documents"}, "response_text": "Opening"}
        dispatcher.dispatch(intent)
        dispatcher._files.execute.assert_called_once()

    def test_routes_to_media(self, dispatcher):
        intent = {"action": "media.play_pause", "params": {}, "response_text": "Play/Pause"}
        dispatcher.dispatch(intent)
        dispatcher._media.execute.assert_called_once()

    def test_routes_to_keyboard(self, dispatcher):
        intent = {"action": "keyboard.type", "params": {"text": "hello"}, "response_text": "Typing"}
        dispatcher.dispatch(intent)
        dispatcher._keyboard.execute.assert_called_once()

    def test_routes_mouse_to_keyboard(self, dispatcher):
        intent = {"action": "mouse.click", "params": {}, "response_text": "Clicking"}
        dispatcher.dispatch(intent)
        dispatcher._keyboard.execute.assert_called_once()


class TestDispatchUnknown:
    def test_unknown_action(self, dispatcher):
        intent = {"action": "unknown", "params": {}, "response_text": ""}
        result = dispatcher.dispatch(intent)
        assert result  # should return error message

    def test_invalid_action_blocked(self, dispatcher):
        intent = {"action": "hacker.steal_data", "params": {}, "response_text": ""}
        result = dispatcher.dispatch(intent)
        # Should not call any handler
        dispatcher._system.execute.assert_not_called()
        dispatcher._browser.execute.assert_not_called()

    def test_missing_action_key(self, dispatcher):
        intent = {"params": {}, "response_text": ""}
        result = dispatcher.dispatch(intent)
        assert result  # returns error/unknown message


class TestDispatchErrorHandling:
    def test_handler_exception_caught(self, dispatcher):
        dispatcher._system.execute.side_effect = RuntimeError("Boom!")
        intent = {"action": "system.open_app", "params": {"app": "calc"}, "response_text": "Opening"}
        result = dispatcher.dispatch(intent)
        assert "Erro" in result or "error" in result.lower() or "comando" in result.lower()

    def test_response_text_used_when_handler_returns_none(self, dispatcher):
        dispatcher._system.execute.return_value = None
        intent = {"action": "system.open_app", "params": {"app": "calc"}, "response_text": "Opening calc"}
        result = dispatcher.dispatch(intent)
        # Should use response_text or "Done"
        assert result


class TestGetAvailableActions:
    def test_returns_list(self, dispatcher):
        actions = dispatcher.get_available_actions()
        assert isinstance(actions, list)
        assert len(actions) > 50

    def test_contains_core_actions(self, dispatcher):
        actions = dispatcher.get_available_actions()
        assert "system.open_app" in actions
        assert "browser.search" in actions
        assert "keyboard.type" in actions
        assert "media.play_pause" in actions
