"""
Modulo de sintese de voz (TTS) para resposta ao usuario.
Supports: pt (Portuguese), es (Spanish), en (English).
"""

import logging
import threading

from ..i18n import get_language, VOICE_PATTERNS

logger = logging.getLogger(__name__)


class Speaker:
    """Sintetiza respostas em voz usando pyttsx3."""

    def __init__(self, config: dict):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.rate = config.get("rate", 180)
        self.volume = config.get("volume", 0.9)
        self.prefer_female = config.get("prefer_female", True)
        self._engine = None
        self._lock = threading.Lock()
        self._speaking = False

        if self.enabled:
            self._init_engine()

    def _init_engine(self):
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self.rate)
            self._engine.setProperty("volume", self.volume)
            self._select_voice()
            logger.info("TTS initialized.")
        except Exception as e:
            logger.warning(f"Error initializing TTS: {e}. Voice responses disabled.")
            self.enabled = False

    def _select_voice(self):
        """Selects the best voice for the current language."""
        if self._engine is None:
            return

        lang = get_language()
        patterns = VOICE_PATTERNS.get(lang, VOICE_PATTERNS.get("en", {}))
        lang_ids = patterns.get("lang_ids", ["en"])
        female_names = patterns.get("female_names", ["female"])

        voices = self._engine.getProperty("voices")

        # Find voices matching the language
        lang_voices = [
            v for v in voices
            if any(lid in v.id.lower() or lid in v.name.lower() for lid in lang_ids)
        ]

        if not lang_voices:
            lang_name = {"pt": "Portuguese", "es": "Spanish", "en": "English"}.get(lang, lang)
            logger.warning(f"No {lang_name} voice found. Using default.")
            return

        if self.prefer_female:
            female = [
                v for v in lang_voices
                if any(f in v.name.lower() for f in female_names)
            ]
            selected = female[0] if female else lang_voices[0]
        else:
            selected = lang_voices[0]

        self._engine.setProperty("voice", selected.id)
        logger.info(f"Voice selected: {selected.name}")

    def say(self, text: str, blocking: bool = False):
        """Speaks the text. By default, non-blocking."""
        if not self.enabled or not text:
            return

        if blocking:
            self._speak(text)
        else:
            thread = threading.Thread(target=self._speak, args=(text,), daemon=True)
            thread.start()

    def _speak(self, text: str):
        with self._lock:
            if self._engine is None:
                return
            try:
                self._speaking = True
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception as e:
                logger.error(f"Error speaking: {e}")
            finally:
                self._speaking = False

    def stop(self):
        """Stops current speech."""
        if self._engine and self._speaking:
            try:
                self._engine.stop()
            except Exception:
                pass

    def is_speaking(self) -> bool:
        return self._speaking

    def list_voices(self) -> list:
        """Lists all available voices."""
        if self._engine is None:
            return []
        return [(v.id, v.name) for v in self._engine.getProperty("voices")]
