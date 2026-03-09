"""
Módulo de síntese de voz (TTS) para resposta ao usuário em português.
"""

import logging
import threading

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
            logger.info("TTS inicializado.")
        except Exception as e:
            logger.warning(f"Erro ao inicializar TTS: {e}. Respostas por voz desabilitadas.")
            self.enabled = False

    def _select_voice(self):
        """Seleciona a melhor voz em português disponível."""
        if self._engine is None:
            return
        voices = self._engine.getProperty("voices")
        pt_voices = [v for v in voices if "pt" in v.id.lower() or "portugu" in v.name.lower()]

        if not pt_voices:
            logger.warning("Nenhuma voz em português encontrada. Usando padrão.")
            return

        if self.prefer_female:
            female = [v for v in pt_voices if any(
                f in v.name.lower() for f in ["female", "woman", "maria", "ana", "lucia", "fernanda"]
            )]
            selected = female[0] if female else pt_voices[0]
        else:
            selected = pt_voices[0]

        self._engine.setProperty("voice", selected.id)
        logger.info(f"Voz selecionada: {selected.name}")

    def say(self, text: str, blocking: bool = False):
        """Fala o texto. Por padrão, não bloqueia a thread principal."""
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
                logger.error(f"Erro ao falar: {e}")
            finally:
                self._speaking = False

    def stop(self):
        """Para a fala atual."""
        if self._engine and self._speaking:
            try:
                self._engine.stop()
            except Exception:
                pass

    def is_speaking(self) -> bool:
        return self._speaking

    def list_voices(self) -> list:
        """Lista todas as vozes disponíveis."""
        if self._engine is None:
            return []
        return [(v.id, v.name) for v in self._engine.getProperty("voices")]
