"""Tests for the i18n module."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.i18n import (
    set_language, get_language, t,
    SUPPORTED_LANGUAGES, STRINGS, DEFAULT_WAKE_WORDS,
    OFFLINE_RULES, CONFIRM_WORDS, CANCEL_WORDS,
    FOLDER_ALIASES_I18N, SEARCH_PREFIXES, TYPE_PREFIXES,
    VOICE_PATTERNS, SPEECH_RECOGNITION_LANG,
)


class TestSetLanguage:
    def test_set_language_short_code(self):
        set_language("en")
        assert get_language() == "en"

    def test_set_language_full_code(self):
        set_language("pt-BR")
        assert get_language() == "pt"

    def test_set_language_es(self):
        set_language("es-MX")
        assert get_language() == "es"

    def test_set_language_invalid_falls_back_to_en(self):
        set_language("xx-YY")
        assert get_language() == "en"

    def test_set_language_case_insensitive(self):
        set_language("PT-BR")
        assert get_language() == "pt"


class TestTranslation:
    def test_translate_existing_key_en(self):
        set_language("en")
        assert t("ready") == "Ready!"

    def test_translate_existing_key_pt(self):
        set_language("pt")
        assert t("ready") == "Pronto!"

    def test_translate_existing_key_es(self):
        set_language("es")
        assert t("ready") == "Listo!"

    def test_translate_with_params(self):
        set_language("en")
        result = t("say_wake_word", wake="computer")
        assert "computer" in result

    def test_translate_missing_key_returns_key(self):
        set_language("en")
        assert t("nonexistent_key_xyz") == "nonexistent_key_xyz"

    def test_translate_fallback_to_english(self):
        set_language("en")
        result = t("done")
        assert result == "Done."


class TestLanguageData:
    def test_all_languages_have_strings(self):
        for lang in SUPPORTED_LANGUAGES:
            assert lang in STRINGS, f"Missing STRINGS for '{lang}'"

    def test_all_languages_have_wake_words(self):
        for lang in SUPPORTED_LANGUAGES:
            assert lang in DEFAULT_WAKE_WORDS
            assert "word" in DEFAULT_WAKE_WORDS[lang]
            assert "aliases" in DEFAULT_WAKE_WORDS[lang]

    def test_all_languages_have_offline_rules(self):
        for lang in SUPPORTED_LANGUAGES:
            assert lang in OFFLINE_RULES
            assert len(OFFLINE_RULES[lang]) > 10  # should have many rules

    def test_all_languages_have_confirm_words(self):
        for lang in SUPPORTED_LANGUAGES:
            assert lang in CONFIRM_WORDS
            assert len(CONFIRM_WORDS[lang]) > 3

    def test_all_languages_have_cancel_words(self):
        for lang in SUPPORTED_LANGUAGES:
            assert lang in CANCEL_WORDS
            assert len(CANCEL_WORDS[lang]) > 3

    def test_all_languages_have_folder_aliases(self):
        for lang in SUPPORTED_LANGUAGES:
            assert lang in FOLDER_ALIASES_I18N

    def test_all_languages_have_search_prefixes(self):
        for lang in SUPPORTED_LANGUAGES:
            assert lang in SEARCH_PREFIXES
            assert len(SEARCH_PREFIXES[lang]) > 0

    def test_all_languages_have_type_prefixes(self):
        for lang in SUPPORTED_LANGUAGES:
            assert lang in TYPE_PREFIXES

    def test_all_languages_have_voice_patterns(self):
        for lang in SUPPORTED_LANGUAGES:
            assert lang in VOICE_PATTERNS
            assert "lang_ids" in VOICE_PATTERNS[lang]
            assert "female_names" in VOICE_PATTERNS[lang]

    def test_all_languages_have_speech_recognition_lang(self):
        for lang in SUPPORTED_LANGUAGES:
            assert lang in SPEECH_RECOGNITION_LANG


class TestOfflineRuleFormat:
    @pytest.mark.parametrize("lang", SUPPORTED_LANGUAGES)
    def test_rule_tuple_format(self, lang):
        for rule in OFFLINE_RULES[lang]:
            assert len(rule) == 4, f"Rule should have 4 elements: {rule}"
            triggers, action, params, response = rule
            assert isinstance(triggers, list)
            assert isinstance(action, str)
            assert isinstance(params, dict)
            assert isinstance(response, str)
            assert len(triggers) > 0
            assert "." in action  # should be prefix.sub_action


class TestStringConsistency:
    def test_all_languages_have_same_keys(self):
        en_keys = set(STRINGS["en"].keys())
        for lang in ["pt", "es"]:
            lang_keys = set(STRINGS[lang].keys())
            missing = en_keys - lang_keys
            assert not missing, f"Language '{lang}' missing keys: {missing}"
