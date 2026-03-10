"""
Interpretador de intencoes usando IA (Claude ou OpenAI).
Converte texto falado em acoes estruturadas JSON.
Supports: pt (Portuguese), es (Spanish), en (English).
"""

import json
import logging
import re
from typing import Optional

from .prompts import get_system_prompt, get_unknown_response, get_confirmation_prompt
from ..i18n import (
    get_language, OFFLINE_RULES, SEARCH_PREFIXES, TYPE_PREFIXES,
    CONFIRM_WORDS, CANCEL_WORDS,
)
from ..validation import validate_action, sanitize_text_input

logger = logging.getLogger(__name__)


class IntentParser:
    """Interpreta comandos de voz usando IA (Claude ou OpenAI)."""

    def __init__(self, config: dict):
        self.config = config
        self.backend = config.get("backend", "claude")
        self.fallback = config.get("fallback", "openai")
        self.min_confidence = config.get("min_confidence", 0.6)
        self._lang = get_language()

        self._claude_client = None
        self._openai_client = None
        self._init_clients()

    def _init_clients(self):
        import os

        if self.backend == "claude" or self.fallback == "claude":
            try:
                import anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if api_key:
                    self._claude_client = anthropic.Anthropic(api_key=api_key)
                    logger.info("Claude client initialized.")
                else:
                    logger.warning("ANTHROPIC_API_KEY not found.")
            except ImportError:
                logger.warning("anthropic not installed. pip install anthropic")

        if self.backend == "openai" or self.fallback == "openai":
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self._openai_client = OpenAI(api_key=api_key)
                    logger.info("OpenAI client initialized.")
                else:
                    logger.warning("OPENAI_API_KEY not found.")
            except ImportError:
                logger.warning("openai not installed. pip install openai")

    def parse(self, text: str) -> dict:
        """
        Interprets text and returns a structured action.
        Tries the primary backend; if it fails, uses the fallback.
        """
        self._lang = get_language()
        text = sanitize_text_input(text)
        if not text:
            return get_unknown_response(self._lang)
        logger.info(f"Interpreting ({self._lang}): '{text}'")

        result = None
        if self.backend != "offline":
            result = self._try_parse(text, self.backend)

        if result is None and self.fallback and self.fallback != self.backend:
            logger.info(f"Trying fallback: {self.fallback}")
            result = self._try_parse(text, self.fallback)

        if result is None:
            logger.warning("All backends failed. Using offline keyword matching.")
            result = self._offline_parse(text)

        logger.info(f"Interpreted action: {result.get('action')} (confidence: {result.get('confidence', 0):.2f})")
        return result

    def _try_parse(self, text: str, backend: str) -> Optional[dict]:
        try:
            if backend == "claude" and self._claude_client:
                return self._parse_claude(text)
            elif backend == "openai" and self._openai_client:
                return self._parse_openai(text)
        except Exception as e:
            logger.error(f"Error in backend '{backend}': {e}")
        return None

    def _parse_claude(self, text: str) -> Optional[dict]:
        cfg = self.config.get("claude", {})
        system_prompt = get_system_prompt(self._lang)
        response = self._claude_client.messages.create(
            model=cfg.get("model", "claude-haiku-4-5-20251001"),
            max_tokens=cfg.get("max_tokens", 512),
            temperature=cfg.get("temperature", 0.1),
            system=system_prompt,
            messages=[{"role": "user", "content": text}],
        )
        raw = response.content[0].text.strip()
        return self._parse_json_response(raw)

    def _parse_openai(self, text: str) -> Optional[dict]:
        cfg = self.config.get("openai", {})
        system_prompt = get_system_prompt(self._lang)
        response = self._openai_client.chat.completions.create(
            model=cfg.get("model", "gpt-4o-mini"),
            max_tokens=cfg.get("max_tokens", 512),
            temperature=cfg.get("temperature", 0.1),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
        )
        raw = response.choices[0].message.content.strip()
        return self._parse_json_response(raw)

    def _parse_json_response(self, raw: str) -> Optional[dict]:
        """Extracts and validates JSON from the AI response."""
        raw = re.sub(r"```(?:json)?\n?", "", raw).strip()
        try:
            data = json.loads(raw)
            required = {"action", "params", "confidence", "response_text"}
            if not required.issubset(data.keys()):
                logger.warning(f"Incomplete JSON response: {data}")
                return None

            # Validate action against whitelist
            action = data.get("action", "")
            if action and action != "unknown" and not validate_action(action):
                logger.warning(f"AI returned invalid action: '{action}' — blocked")
                return None

            # Validate confidence is a number in range
            confidence = data.get("confidence", 0)
            if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                data["confidence"] = 0.5

            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}\nResponse: {raw}")
            return None

    # Filler words stripped during offline matching (articles, prepositions, etc.)
    _FILLER_WORDS = {
        "pt": {"o", "a", "os", "as", "um", "uma", "uns", "umas", "do", "da",
               "dos", "das", "no", "na", "nos", "nas", "de", "em", "para",
               "por", "com", "ao", "aos", "meu", "minha"},
        "es": {"el", "la", "los", "las", "un", "una", "unos", "unas", "del",
               "al", "de", "en", "para", "por", "con", "mi"},
        "en": {"the", "a", "an", "my", "please"},
    }

    # Common verb conjugation mappings (imperative → infinitive)
    _VERB_NORMALIZATIONS = {
        "pt": {
            "abre": "abrir", "fecha": "fechar", "abre": "abrir",
            "minimiza": "minimizar", "maximiza": "maximizar",
            "mostra": "mostrar", "bloqueia": "bloquear",
            "tira": "tirar", "aumenta": "aumentar", "diminui": "diminuir",
            "baixa": "baixar", "silencia": "silenciar",
            "recarrega": "recarregar", "atualiza": "atualizar",
            "rola": "rolar", "desce": "descer", "sobe": "subir",
            "salva": "salvar", "copia": "copiar", "cola": "colar",
            "recorta": "recortar", "seleciona": "selecionar",
            "pausa": "pausar", "para": "parar", "digita": "digitar",
            "pesquisa": "pesquisar", "busca": "buscar",
        },
        "es": {
            "abre": "abrir", "cierra": "cerrar",
            "minimiza": "minimizar", "maximiza": "maximizar",
            "muestra": "mostrar", "bloquea": "bloquear",
            "sube": "subir", "baja": "bajar",
            "recarga": "recargar", "actualiza": "actualizar",
            "guarda": "guardar", "copia": "copiar", "pega": "pegar",
            "corta": "cortar", "selecciona": "seleccionar",
            "pausa": "pausar", "busca": "buscar",
        },
        "en": {},
    }

    def _normalize_text(self, text: str) -> str:
        """Strip filler words and normalize verb forms for offline matching."""
        lang = self._lang
        words = text.lower().split()

        # Normalize verbs (first word is usually the verb)
        verb_map = self._VERB_NORMALIZATIONS.get(lang, {})
        if words and words[0] in verb_map:
            words[0] = verb_map[words[0]]

        # Strip filler words
        fillers = self._FILLER_WORDS.get(lang, set())
        words = [w for w in words if w not in fillers]

        return " ".join(words)

    # Known app names that can appear as targets in voice commands
    _APP_KEYWORDS = {
        "chrome", "google chrome", "firefox", "edge", "safari",
        "word", "excel", "powerpoint", "power point", "outlook",
        "notepad", "bloco de notas", "bloc de notas",
        "explorer", "explorador", "spotify", "discord", "vscode",
        "teams", "whatsapp", "calculadora", "calculator", "calc",
        "cmd", "powershell", "terminal",
    }

    def _extract_target_app(self, text: str, action: str, params: dict) -> str | None:
        """
        Extract the target application from the command text.
        Returns the normalized app name or None.
        """
        text_lower = text.lower()

        # If params already has an app (e.g., from triggers), use it
        if params.get("app"):
            return params["app"]
        if params.get("browser"):
            return params["browser"]

        # Search for known app names in the text
        # Check longer patterns first to avoid partial matches
        for app in sorted(self._APP_KEYWORDS, key=len, reverse=True):
            if app in text_lower:
                # Normalize multi-word app names
                norm = {
                    "google chrome": "chrome", "bloco de notas": "notepad",
                    "bloc de notas": "notepad", "power point": "powerpoint",
                    "explorador": "explorer", "calculadora": "calc",
                    "calculator": "calc", "terminal": "cmd",
                }.get(app, app)
                return norm

        return None

    def _offline_parse(self, text: str) -> dict:
        """
        Simple keyword matching when AI is not available.
        Uses language-specific rules from i18n module.
        """
        text_lower = text.lower().strip()
        text_normalized = self._normalize_text(text_lower)
        lang = self._lang

        # Get language-specific rules (fallback to English)
        rules = OFFLINE_RULES.get(lang, OFFLINE_RULES.get("en", []))

        for triggers, action, params, response in rules:
            if any(t in text_lower or t in text_normalized
                   or self._normalize_text(t) in text_normalized
                   for t in triggers):
                target = self._extract_target_app(text_lower, action, params)
                return {
                    "action": action,
                    "params": params,
                    "target_app": target,
                    "confidence": 0.85,
                    "response_text": response,
                    "requires_confirmation": False,
                }

        # Web search (generic)
        prefixes = SEARCH_PREFIXES.get(lang, SEARCH_PREFIXES["en"])
        for prefix in prefixes:
            if text_lower.startswith(prefix):
                query = text[len(prefix):].strip()
                if query:
                    responses = {
                        "pt": f"Pesquisando por {query}.",
                        "es": f"Buscando {query}.",
                        "en": f"Searching for {query}.",
                    }
                    return {
                        "action": "browser.search",
                        "params": {"query": query, "engine": "google"},
                        "confidence": 0.80,
                        "response_text": responses.get(lang, responses["en"]),
                        "requires_confirmation": False,
                    }

        # Type text
        type_prefixes = TYPE_PREFIXES.get(lang, TYPE_PREFIXES["en"])
        for prefix in type_prefixes:
            if text_lower.startswith(prefix):
                type_text = text[len(prefix):].strip()
                if type_text:
                    responses = {
                        "pt": f"Digitando: {type_text}",
                        "es": f"Escribiendo: {type_text}",
                        "en": f"Typing: {type_text}",
                    }
                    return {
                        "action": "keyboard.type",
                        "params": {"text": type_text},
                        "confidence": 0.85,
                        "response_text": responses.get(lang, responses["en"]),
                        "requires_confirmation": False,
                    }

        unknown = get_unknown_response(lang)
        unknown_texts = {
            "pt": f"Nao entendi '{text}'. Pode repetir?",
            "es": f"No entendi '{text}'. Puede repetir?",
            "en": f"I didn't understand '{text}'. Can you repeat?",
        }
        return {**unknown, "response_text": unknown_texts.get(lang, unknown_texts["en"])}

    def check_confirmation(self, original_command: str, action_desc: str, user_response: str) -> bool:
        """Checks if the user response is a confirmation."""
        lang = self._lang
        confirm_words = CONFIRM_WORDS.get(lang, CONFIRM_WORDS["en"])
        cancel_words = CANCEL_WORDS.get(lang, CANCEL_WORDS["en"])

        response_lower = user_response.lower()

        if any(w in response_lower for w in confirm_words):
            return True
        if any(w in response_lower for w in cancel_words):
            return False

        # Use AI for ambiguous cases
        if self._claude_client or self._openai_client:
            prompt_template = get_confirmation_prompt(lang)
            prompt = prompt_template.format(
                original_command=original_command,
                action_description=action_desc,
                confirmation_text=user_response,
            )
            try:
                result = self._try_parse(prompt, self.backend) or self._try_parse(prompt, self.fallback)
                if result and isinstance(result, str):
                    return "confirm" in result.lower()
            except Exception:
                pass

        return False
