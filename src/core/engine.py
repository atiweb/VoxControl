"""
Engine principal: orquestra audio -> STT -> AI -> acao -> TTS.
"""

import logging
import time
from typing import Optional

from ..i18n import t

logger = logging.getLogger(__name__)


class VoiceEngine:
    """
    Engine central que conecta todos os modulos.
    Pode ser usado tanto pelo listener de microfone
    quanto pela API remota (celular).
    """

    def __init__(self, config: dict):
        self.config = config
        self._transcriber = None
        self._intent_parser = None
        self._dispatcher = None
        self._speaker = None
        self._pending_confirmation: Optional[dict] = None
        self._running = False

    def setup(self):
        """Inicializa todos os modulos."""
        from ..audio.transcriber import Transcriber
        from ..ai.intent_parser import IntentParser
        from ..actions.dispatcher import ActionDispatcher
        from ..voice.speaker import Speaker

        logger.info("Initializing modules...")

        self._transcriber = Transcriber(self.config.get("stt", {}))
        self._intent_parser = IntentParser(self.config.get("ai", {}))
        self._dispatcher = ActionDispatcher({
            **self.config.get("browser", {}),
            **self.config,
            "custom_commands_path": "config/custom_commands.yaml",
        })
        self._speaker = Speaker(self.config.get("voice_response", {}))

        logger.info("Engine ready.")

    def process_audio(self, audio_data) -> Optional[str]:
        """
        Processa audio capturado: STT -> AI -> acao -> resposta.
        Retorna o texto da resposta.
        """
        if self._transcriber is None:
            return None

        # 1. Transcrever audio
        text = self._transcriber.transcribe(audio_data)
        if not text:
            logger.debug("No text detected in audio.")
            return None

        return self.process_text(text)

    def process_text(self, text: str) -> str:
        """
        Processa texto direto (usado pelo controle remoto e modo texto).
        STT ja feito, vai direto para AI -> acao -> resposta.
        """
        logger.info(f"Command received: '{text}'")

        # 2. Verificar se aguarda confirmacao
        if self._pending_confirmation:
            return self._handle_confirmation(text)

        # 3. Interpretar intencao via IA
        intent = self._intent_parser.parse(text)
        confidence = intent.get("confidence", 0)
        action = intent.get("action", "unknown")
        response_text = intent.get("response_text", "")
        requires_confirmation = intent.get("requires_confirmation", False)

        logger.info(f"Intent: {action} (confidence: {confidence:.2f})")

        # 4. Confianca baixa: pedir para repetir
        min_conf = self.config.get("ai", {}).get("min_confidence", 0.6)
        if confidence < min_conf and action != "unknown":
            response = t("not_sure", response=response_text)
            self._pending_confirmation = {"intent": intent, "original": text}
            self._speak(response)
            return response

        # 5. Acoes perigosas: pedir confirmacao
        confirm_risky = self.config.get("ai", {}).get("confirm_risky_actions", True)
        if requires_confirmation and confirm_risky:
            response = t("confirm_prompt", response=response_text)
            self._pending_confirmation = {"intent": intent, "original": text}
            self._speak(response)
            return response

        # 6. Executar acao
        result = self._dispatcher.dispatch(intent)
        # Use the AI/offline response_text for speaking (already in correct language)
        # Use dispatcher result only as fallback
        spoken = response_text if response_text else result
        self._speak(spoken)
        return spoken

    def _handle_confirmation(self, text: str) -> str:
        """Processa resposta de confirmacao pendente."""
        pending = self._pending_confirmation
        self._pending_confirmation = None

        original = pending.get("original", "")
        intent = pending.get("intent", {})
        action_desc = intent.get("response_text", "")

        confirmed = self._intent_parser.check_confirmation(original, action_desc, text)

        if confirmed:
            result = self._dispatcher.dispatch(intent)
            response_text = intent.get("response_text", result)
            spoken = response_text if response_text else result
            self._speak(spoken)
            return spoken
        else:
            response = t("cancelled")
            self._speak(response)
            return response

    def _speak(self, text: str):
        if self._speaker:
            self._speaker.say(text)

    @property
    def transcriber(self):
        return self._transcriber

    @property
    def speaker(self):
        return self._speaker
