"""Tests for the IntentParser (offline mode)."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.i18n import set_language
from src.ai.intent_parser import IntentParser


@pytest.fixture
def parser():
    """Create an IntentParser in offline mode (no API keys needed)."""
    set_language("en")
    config = {
        "backend": "offline",
        "fallback": "",
        "min_confidence": 0.6,
    }
    return IntentParser(config)


@pytest.fixture
def parser_pt():
    """Parser in Portuguese."""
    set_language("pt")
    return IntentParser({"backend": "offline", "fallback": ""})


@pytest.fixture
def parser_es():
    """Parser in Spanish."""
    set_language("es")
    return IntentParser({"backend": "offline", "fallback": ""})


class TestOfflineParseEN:
    def test_open_calculator(self, parser):
        result = parser.parse("open calculator")
        assert result["action"] == "system.open_app"
        assert result["params"]["app"] == "calc"
        assert result["confidence"] > 0.5

    def test_open_chrome(self, parser):
        result = parser.parse("open chrome")
        assert result["action"] == "browser.open"
        assert result["params"]["browser"] == "chrome"

    def test_take_screenshot(self, parser):
        result = parser.parse("take screenshot")
        assert result["action"] == "system.screenshot"

    def test_volume_up(self, parser):
        result = parser.parse("volume up")
        assert result["action"] == "system.volume_up"

    def test_volume_down(self, parser):
        result = parser.parse("volume down")
        assert result["action"] == "system.volume_down"

    def test_minimize(self, parser):
        result = parser.parse("minimize")
        assert result["action"] == "system.minimize"

    def test_maximize(self, parser):
        result = parser.parse("maximize")
        assert result["action"] == "system.maximize"

    def test_lock_screen(self, parser):
        result = parser.parse("lock screen")
        assert result["action"] == "system.lock_screen"

    def test_mute(self, parser):
        result = parser.parse("mute")
        assert result["action"] == "system.volume_mute"

    def test_new_tab(self, parser):
        result = parser.parse("new tab")
        assert result["action"] == "browser.new_tab"

    def test_close_tab(self, parser):
        result = parser.parse("close tab")
        assert result["action"] == "browser.close_tab"

    def test_play_pause(self, parser):
        result = parser.parse("play pause")
        assert result["action"] == "media.play_pause"

    def test_next_song(self, parser):
        result = parser.parse("next song")
        assert result["action"] == "media.next"

    def test_copy(self, parser):
        result = parser.parse("copy")
        assert result["action"] == "keyboard.copy"

    def test_paste(self, parser):
        result = parser.parse("paste")
        assert result["action"] == "keyboard.paste"

    def test_undo(self, parser):
        result = parser.parse("undo")
        assert result["action"] == "keyboard.undo"

    def test_save(self, parser):
        result = parser.parse("save")
        assert result["action"] == "keyboard.save"

    def test_open_whatsapp(self, parser):
        result = parser.parse("open whatsapp")
        assert result["action"] == "whatsapp.open"


class TestOfflineParsePT:
    def test_abrir_calculadora(self, parser_pt):
        result = parser_pt.parse("abrir calculadora")
        assert result["action"] == "system.open_app"
        assert result["params"]["app"] == "calc"

    def test_abrir_chrome(self, parser_pt):
        result = parser_pt.parse("abrir chrome")
        assert result["action"] == "browser.open"

    def test_minimizar(self, parser_pt):
        result = parser_pt.parse("minimizar")
        assert result["action"] == "system.minimize"

    def test_tirar_print(self, parser_pt):
        result = parser_pt.parse("tirar print")
        assert result["action"] == "system.screenshot"

    def test_aumentar_volume(self, parser_pt):
        result = parser_pt.parse("aumentar volume")
        assert result["action"] == "system.volume_up"

    def test_bloquear_tela(self, parser_pt):
        result = parser_pt.parse("bloquear tela")
        assert result["action"] == "system.lock_screen"


class TestOfflineParseES:
    def test_abrir_calculadora(self, parser_es):
        result = parser_es.parse("abrir calculadora")
        assert result["action"] == "system.open_app"

    def test_captura_de_pantalla(self, parser_es):
        result = parser_es.parse("captura de pantalla")
        assert result["action"] == "system.screenshot"

    def test_subir_volumen(self, parser_es):
        result = parser_es.parse("subir volumen")
        assert result["action"] == "system.volume_up"


class TestSearchParsing:
    def test_search_for_query_en(self, parser):
        result = parser.parse("search for weather today")
        assert result["action"] == "browser.search"
        assert "weather" in result["params"]["query"]

    def test_google_query_en(self, parser):
        result = parser.parse("google python tutorials")
        assert result["action"] == "browser.search"

    def test_pesquisar_pt(self, parser_pt):
        result = parser_pt.parse("pesquisar receitas de bolo")
        assert result["action"] == "browser.search"
        assert "receitas" in result["params"]["query"]

    def test_buscar_es(self, parser_es):
        result = parser_es.parse("buscar recetas de cocina")
        assert result["action"] == "browser.search"


class TestTypeParsing:
    def test_type_text_en(self, parser):
        result = parser.parse("type hello world")
        assert result["action"] == "keyboard.type"
        assert result["params"]["text"] == "hello world"

    def test_digitar_pt(self, parser_pt):
        result = parser_pt.parse("digitar ola mundo")
        assert result["action"] == "keyboard.type"

    def test_escribir_es(self, parser_es):
        result = parser_es.parse("escribir hola mundo")
        assert result["action"] == "keyboard.type"


class TestUnknownCommands:
    def test_unknown_returns_unknown_action(self, parser):
        result = parser.parse("xyzzy foobar nonsense")
        assert result["action"] == "unknown"

    def test_empty_returns_unknown(self, parser):
        result = parser.parse("")
        assert result["action"] == "unknown"


class TestConfirmation:
    def test_confirm_yes(self, parser):
        assert parser.check_confirmation("shutdown", "Shutting down", "yes") is True

    def test_confirm_sure(self, parser):
        assert parser.check_confirmation("shutdown", "Shutting down", "sure") is True

    def test_cancel_no(self, parser):
        assert parser.check_confirmation("shutdown", "Shutting down", "no") is False

    def test_cancel_cancel(self, parser):
        assert parser.check_confirmation("shutdown", "Shutting down", "cancel") is False

    def test_confirm_pt(self, parser_pt):
        assert parser_pt.check_confirmation("desligar", "Desligando", "sim") is True

    def test_cancel_pt(self, parser_pt):
        assert parser_pt.check_confirmation("desligar", "Desligando", "nao") is False


class TestJsonResponseValidation:
    def test_valid_json(self, parser):
        raw = '{"action": "system.open_app", "params": {"app": "calc"}, "confidence": 0.9, "response_text": "Opening calc"}'
        result = parser._parse_json_response(raw)
        assert result is not None
        assert result["action"] == "system.open_app"

    def test_json_with_code_block(self, parser):
        raw = '```json\n{"action": "system.open_app", "params": {"app": "calc"}, "confidence": 0.9, "response_text": "OK"}\n```'
        result = parser._parse_json_response(raw)
        assert result is not None

    def test_invalid_action_blocked(self, parser):
        raw = '{"action": "hacker.steal_data", "params": {}, "confidence": 0.9, "response_text": "Hacking..."}'
        result = parser._parse_json_response(raw)
        assert result is None

    def test_missing_fields(self, parser):
        raw = '{"action": "system.open_app"}'
        result = parser._parse_json_response(raw)
        assert result is None

    def test_invalid_json(self, parser):
        result = parser._parse_json_response("not json at all")
        assert result is None

    def test_confidence_out_of_range_clamped(self, parser):
        raw = '{"action": "system.open_app", "params": {"app": "calc"}, "confidence": 5.0, "response_text": "OK"}'
        result = parser._parse_json_response(raw)
        assert result is not None
        assert result["confidence"] == 0.5  # clamped
