"""
Listener de microfone com detecção de wake word e VAD (Voice Activity Detection).
Escuta continuamente e captura áudio após detectar a palavra de ativação.
"""

import logging
import queue
import threading
import time
import numpy as np
import sounddevice as sd
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class AudioListener:
    """
    Escuta o microfone continuamente.
    Detecta a wake word e captura o comando subsequente.
    """

    def __init__(self, config: dict, on_command: Callable[[np.ndarray], None]):
        self.config = config
        self.on_command = on_command

        audio_cfg = config.get("audio", {})
        self.sample_rate = audio_cfg.get("sample_rate", 16000)
        self.channels = audio_cfg.get("channels", 1)
        self.chunk_ms = audio_cfg.get("chunk_duration_ms", 30)
        self.silence_timeout = audio_cfg.get("silence_timeout", 1.5)
        self.min_energy = audio_cfg.get("min_speech_energy", 0.01)
        self.input_device = audio_cfg.get("input_device", None)

        wake_cfg = config.get("wake_word", {})
        self.wake_word = wake_cfg.get("word", "computador").lower()
        self.wake_aliases = [a.lower() for a in wake_cfg.get("aliases", [])]
        self.listen_timeout = wake_cfg.get("listen_timeout", 6)

        self.chunk_size = int(self.sample_rate * self.chunk_ms / 1000)
        self._running = False
        self._audio_queue: queue.Queue = queue.Queue()
        self._wake_detected = threading.Event()

        # Transcriber leve apenas para wake word (pode ser diferente do principal)
        self._wake_transcriber = None

    def set_wake_transcriber(self, transcriber):
        """Define o transcriber usado para detecção de wake word."""
        self._wake_transcriber = transcriber

    def start(self):
        """Inicia a escuta em background."""
        self._running = True
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            blocksize=self.chunk_size,
            device=self.input_device,
            callback=self._audio_callback,
        )
        self._stream.start()
        self._listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._listen_thread.start()
        logger.info(f"Listener iniciado. Diga '{self.wake_word}' para ativar.")

    def stop(self):
        """Para a escuta."""
        self._running = False
        if hasattr(self, "_stream"):
            self._stream.stop()
            self._stream.close()

    def trigger_manually(self):
        """Ativa o modo de escuta manualmente (sem wake word)."""
        self._wake_detected.set()

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status):
        if status:
            logger.warning(f"Status áudio: {status}")
        self._audio_queue.put(indata.copy().flatten())

    def _listen_loop(self):
        """Loop principal: aguarda wake word, então captura comando."""
        buffer = []
        last_speech_time = time.time()
        collecting_wake = True

        while self._running:
            try:
                chunk = self._audio_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            buffer.append(chunk)

            # Janela deslizante de 2 segundos para detectar wake word
            max_chunks = int(2.0 * self.sample_rate / self.chunk_size)
            if len(buffer) > max_chunks:
                buffer = buffer[-max_chunks:]

            if collecting_wake:
                # Verifica energia para não processar silêncio
                energy = np.abs(chunk).mean()
                if energy < self.min_energy:
                    continue

                # Transcreve a janela para detectar wake word
                window = np.concatenate(buffer)
                detected = self._check_wake_word(window)
                if detected:
                    logger.info(f"Wake word '{self.wake_word}' detectada!")
                    buffer.clear()
                    collecting_wake = False
                    last_speech_time = time.time()
            else:
                # Modo de captura do comando
                energy = np.abs(chunk).mean()
                if energy > self.min_energy:
                    last_speech_time = time.time()

                elapsed_silence = time.time() - last_speech_time
                elapsed_total = time.time() - (last_speech_time - len(buffer) * self.chunk_ms / 1000)

                # Finaliza captura por silêncio ou timeout
                if elapsed_silence >= self.silence_timeout or elapsed_total >= self.listen_timeout:
                    if buffer:
                        command_audio = np.concatenate(buffer)
                        if np.abs(command_audio).mean() > self.min_energy * 0.5:
                            self.on_command(command_audio)
                    buffer.clear()
                    collecting_wake = True
                    logger.info(f"Aguardando '{self.wake_word}'...")

    def _check_wake_word(self, audio: np.ndarray) -> bool:
        """Verifica se a wake word está presente no áudio."""
        if self._wake_transcriber is None:
            return False
        try:
            text = self._wake_transcriber.transcribe(audio, self.sample_rate)
            if not text:
                return False
            text_lower = text.lower()
            all_triggers = [self.wake_word] + self.wake_aliases
            return any(trigger in text_lower for trigger in all_triggers)
        except Exception as e:
            logger.debug(f"Erro na detecção de wake word: {e}")
            return False


class PushToTalkListener:
    """
    Modo alternativo: segura uma tecla para gravar (ex: F12).
    Útil quando wake word não é prático.
    """

    def __init__(self, config: dict, on_command: Callable[[np.ndarray], None]):
        self.config = config
        self.on_command = on_command
        self.hotkey = "f12"

        audio_cfg = config.get("audio", {})
        self.sample_rate = audio_cfg.get("sample_rate", 16000)
        self.channels = audio_cfg.get("channels", 1)
        self.input_device = audio_cfg.get("input_device", None)

        self._recording = False
        self._buffer = []
        self._running = False

    def start(self):
        from pynput import keyboard

        self._running = True
        logger.info(f"Push-to-Talk: segure {self.hotkey.upper()} para falar.")

        def on_press(key):
            try:
                if str(key) == f"Key.{self.hotkey}" and not self._recording:
                    self._start_recording()
            except Exception:
                pass

        def on_release(key):
            try:
                if str(key) == f"Key.{self.hotkey}" and self._recording:
                    self._stop_recording()
            except Exception:
                pass

        self._kb_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self._kb_listener.start()

    def _start_recording(self):
        self._recording = True
        self._buffer = []
        logger.info("Gravando... (solte F12 para parar)")
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            device=self.input_device,
            callback=self._callback,
        )
        self._stream.start()

    def _callback(self, indata, frames, time_info, status):
        self._buffer.append(indata.copy().flatten())

    def _stop_recording(self):
        self._recording = False
        self._stream.stop()
        self._stream.close()
        if self._buffer:
            audio = np.concatenate(self._buffer)
            self.on_command(audio)

    def stop(self):
        self._running = False
        if hasattr(self, "_kb_listener"):
            self._kb_listener.stop()
