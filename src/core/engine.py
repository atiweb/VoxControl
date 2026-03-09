"""
Engine principal: orquestra audio -> STT -> AI -> ação -> TTS.
"""

import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class VoiceEngine:
    """
    Engine central que conecta todos os módulos.
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
        """Inicializa todos os módulos."""
        from ..audio.transcriber import Transcriber
        from ..ai.intent_parser import IntentParser
        from ..actions.dispatcher import ActionDispatcher
        from ..voice.speaker import Speaker

        logger.info("Inicializando módulos...")

        self._transcriber = Transcriber(self.config.get("stt", {}))
        self._intent_parser = IntentParser(self.config.get("ai", {}))
        self._dispatcher = ActionDispatcher({
            **self.config.get("browser", {}),
            **self.config,
            "custom_commands_path": "config/custom_commands.yaml",
        })
        self._speaker = Speaker(self.config.get("voice_response", {}))

        logger.info("Engine pronta.")

    def process_audio(self, audio_data) -> Optional[str]:
        """
        Processa áudio capturado: STT -> AI -> ação -> resposta.
        Retorna o texto da resposta.
        """
        if self._transcriber is None:
            return None

        # 1. Transcrever áudio
        text = self._transcriber.transcribe(audio_data)
        if not text:
            logger.debug("Nenhum texto detectado no áudio.")
            return None

        return self.process_text(text)

    def process_text(self, text: str) -> str:
        """
        Processa texto direto (usado pelo controle remoto).
        STT já feito, vai direto para AI -> ação -> resposta.
        """
        logger.info(f"Comando recebido: '{text}'")

        # 2. Verificar se aguarda confirmação
        if self._pending_confirmation:
            return self._handle_confirmation(text)

        # 3. Interpretar intenção via IA
        intent = self._intent_parser.parse(text)
        confidence = intent.get("confidence", 0)
        action = intent.get("action", "unknown")
        response_text = intent.get("response_text", "")
        requires_confirmation = intent.get("requires_confirmation", False)

        logger.info(f"Intenção: {action} (confiança: {confidence:.2f})")

        # 4. Confiança baixa: pedir para repetir
        min_conf = self.config.get("ai", {}).get("min_confidence", 0.6)
        if confidence < min_conf and action != "unknown":
            response = f"Não tenho certeza. Quis dizer: {response_text}? Confirme dizendo 'sim' ou repita o comando."
            self._pending_confirmation = {"intent": intent, "original": text}
            self._speak(response)
            return response

        # 5. Ações perigosas: pedir confirmação
        confirm_risky = self.config.get("ai", {}).get("confirm_risky_actions", True)
        if requires_confirmation and confirm_risky:
            response = f"{response_text} Confirma?"
            self._pending_confirmation = {"intent": intent, "original": text}
            self._speak(response)
            return response

        # 6. Executar ação
        result = self._dispatcher.dispatch(intent)
        self._speak(result)
        return result

    def _handle_confirmation(self, text: str) -> str:
        """Processa resposta de confirmação pendente."""
        pending = self._pending_confirmation
        self._pending_confirmation = None

        original = pending.get("original", "")
        intent = pending.get("intent", {})
        action_desc = intent.get("response_text", "")

        confirmed = self._intent_parser.check_confirmation(original, action_desc, text)

        if confirmed:
            result = self._dispatcher.dispatch(intent)
            self._speak(result)
            return result
        else:
            response = "Tudo bem, comando cancelado."
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
