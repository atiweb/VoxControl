"""
Módulo de transcrição de áudio para texto.
Suporta faster-whisper (offline, alta precisão) e Vosk (offline, leve).
"""

import logging
import numpy as np
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class Transcriber:
    """Transcreve áudio para texto em português."""

    def __init__(self, config: dict):
        self.config = config
        self.engine = config.get("engine", "faster-whisper")
        self._model = None
        self._vosk_rec = None
        self._load_model()

    def _load_model(self):
        if self.engine == "faster-whisper":
            self._load_whisper()
        elif self.engine == "vosk":
            self._load_vosk()
        else:
            raise ValueError(f"Engine de STT desconhecida: {self.engine}")

    def _load_whisper(self):
        try:
            from faster_whisper import WhisperModel
            cfg = self.config.get("whisper", {})
            model_size = cfg.get("model_size", "small")
            device = cfg.get("device", "auto")
            compute_type = cfg.get("compute_type", "int8")

            logger.info(f"Carregando Whisper '{model_size}' no dispositivo '{device}'...")
            try:
                self._model = WhisperModel(
                    model_size,
                    device=device,
                    compute_type=compute_type,
                )
            except Exception as e:
                if device != "cpu":
                    logger.warning(f"Falha ao carregar no dispositivo '{device}': {e}")
                    logger.info("Tentando fallback para CPU...")
                    self._model = WhisperModel(
                        model_size,
                        device="cpu",
                        compute_type="int8",
                    )
                else:
                    raise
            logger.info("Whisper carregado com sucesso.")
        except ImportError:
            logger.error("faster-whisper não instalado. Execute: pip install faster-whisper")
            raise
        except Exception as e:
            logger.error(f"Erro ao carregar Whisper: {e}")
            raise

    def _load_vosk(self):
        try:
            from vosk import Model, KaldiRecognizer
            cfg = self.config.get("vosk", {})
            default_model = cfg.get("model_path", "models/vosk-model-pt")
            from ..paths import get_models_dir
            model_path = str(get_models_dir() / Path(default_model).name)
            if not Path(model_path).exists():
                raise FileNotFoundError(
                    f"Modelo Vosk não encontrado em '{model_path}'.\n"
                    "Baixe em: https://alphacephei.com/vosk/models\n"
                    "Recomendado: vosk-model-pt-fb-v0.1.1"
                )
            logger.info(f"Carregando Vosk de '{model_path}'...")
            model = Model(model_path)
            self._vosk_rec = KaldiRecognizer(model, 16000)
            logger.info("Vosk carregado com sucesso.")
        except ImportError:
            logger.error("vosk não instalado. Execute: pip install vosk")
            raise

    def transcribe(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Optional[str]:
        """
        Transcreve array numpy de áudio para texto.
        Retorna None se não detectar fala.
        """
        if self.engine == "faster-whisper":
            return self._transcribe_whisper(audio_data, sample_rate)
        elif self.engine == "vosk":
            return self._transcribe_vosk(audio_data)
        return None

    def _transcribe_whisper(self, audio_data: np.ndarray, sample_rate: int) -> Optional[str]:
        try:
            cfg = self.config.get("whisper", {})
            # Normalizar para float32 entre -1 e 1
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32) / 32768.0

            segments, info = self._model.transcribe(
                audio_data,
                language=cfg.get("language", "pt"),
                beam_size=cfg.get("beam_size", 5),
                vad_filter=cfg.get("vad_filter", True),
                vad_parameters=dict(min_silence_duration_ms=500),
            )
            text = " ".join(s.text for s in segments).strip()
            if not text:
                return None
            logger.debug(f"Whisper transcreveu: '{text}'")
            return text
        except Exception as e:
            logger.error(f"Erro na transcrição Whisper: {e}")
            return None

    def _transcribe_vosk(self, audio_data: np.ndarray) -> Optional[str]:
        try:
            import json
            # Converter para int16 para Vosk
            if audio_data.dtype != np.int16:
                audio_int16 = (audio_data * 32768).astype(np.int16)
            else:
                audio_int16 = audio_data

            self._vosk_rec.AcceptWaveform(audio_int16.tobytes())
            result = json.loads(self._vosk_rec.Result())
            text = result.get("text", "").strip()
            if not text:
                return None
            logger.debug(f"Vosk transcreveu: '{text}'")
            return text
        except Exception as e:
            logger.error(f"Erro na transcrição Vosk: {e}")
            return None
