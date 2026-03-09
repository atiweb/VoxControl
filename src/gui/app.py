"""
VoxControl GUI -- Main application window.
Professional desktop interface using customtkinter.
"""

import customtkinter as ctk
import logging
import threading
import time
from pathlib import Path
from typing import Optional

from .frames.status_frame import StatusFrame
from .frames.control_frame import ControlFrame
from .frames.command_frame import CommandFrame
from .frames.log_frame import LogFrame
from .frames.settings_frame import SettingsFrame
from .tray import SystemTrayManager

logger = logging.getLogger(__name__)

# ── Colour palette (matches Flutter app) ────────────────────────────
BG_DARK = "#0D1117"
SURFACE_DARK = "#161B22"
CARD_DARK = "#21262D"
PRIMARY = "#6C63FF"
ACCENT = "#00D9FF"
SUCCESS = "#3FB950"
ERROR = "#F85149"
WARNING = "#D29922"
TEXT_PRIMARY = "#E6EDF3"
TEXT_SECONDARY = "#8B949E"


class VoxControlApp(ctk.CTk):
    """Main GUI window for VoxControl."""

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self._engine = None
        self._listener = None
        self._running = False
        self._mode = "wake_word"  # wake_word | ptt | text
        self._tray: Optional[SystemTrayManager] = None

        # ── Window setup ────────────────────────────────────────────
        self.title("VoxControl")
        self.geometry("520x740")
        self.minsize(480, 600)
        self.configure(fg_color=BG_DARK)
        self._set_icon()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ── Layout: 5 main sections stacked vertically ──────────────
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # log_frame gets remaining space

        # Header / brand
        self._build_header()

        # Status bar (row 1)
        self.status_frame = StatusFrame(self, config)
        self.status_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 4))

        # Control panel (row 2)
        self.control_frame = ControlFrame(
            self, config,
            on_start=self._start_engine,
            on_stop=self._stop_engine,
            on_mode_change=self._change_mode,
        )
        self.control_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=4)

        # Log / history (row 3 — expandable)
        self.log_frame = LogFrame(self, config)
        self.log_frame.grid(row=3, column=0, sticky="nsew", padx=12, pady=4)

        # Command input (row 4)
        self.command_frame = CommandFrame(self, config, on_send=self._send_text_command)
        self.command_frame.grid(row=4, column=0, sticky="ew", padx=12, pady=(4, 12))

        # Settings panel (hidden by default, toggled via menu)
        self.settings_frame: Optional[SettingsFrame] = None
        self._settings_visible = False

        # ── Logging handler → log frame ─────────────────────────────
        self._install_log_handler()

        # ── Protocol handlers ───────────────────────────────────────
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # ── System tray ─────────────────────────────────────────────
        self._init_tray()

    # ────────────────────────────────────────────────────────────────
    # Header
    # ────────────────────────────────────────────────────────────────
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=SURFACE_DARK, corner_radius=10)
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 4))
        header.grid_columnconfigure(1, weight=1)

        # Logo icon
        logo = ctk.CTkLabel(
            header, text="🎤", font=ctk.CTkFont(size=28),
            text_color=PRIMARY, width=40,
        )
        logo.grid(row=0, column=0, padx=(12, 4), pady=10)

        # Title + subtitle
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=1, sticky="w", pady=10)
        ctk.CTkLabel(
            title_frame, text="VoxControl",
            font=ctk.CTkFont(size=20, weight="bold"), text_color=TEXT_PRIMARY,
        ).pack(anchor="w")
        lang = config_language(self.config)
        backend = self.config.get("ai", {}).get("backend", "offline").upper()
        ctk.CTkLabel(
            title_frame, text=f"AI: {backend}  •  Lang: {lang}",
            font=ctk.CTkFont(size=12), text_color=TEXT_SECONDARY,
        ).pack(anchor="w")

        # Settings gear button
        gear_btn = ctk.CTkButton(
            header, text="⚙", width=36, height=36,
            font=ctk.CTkFont(size=18), fg_color="transparent",
            hover_color=CARD_DARK, text_color=TEXT_SECONDARY,
            command=self._toggle_settings,
        )
        gear_btn.grid(row=0, column=2, padx=(4, 12))

    # ────────────────────────────────────────────────────────────────
    # Engine lifecycle
    # ────────────────────────────────────────────────────────────────
    def _start_engine(self):
        """Initialize and start VoiceEngine + listener in a background thread."""
        if self._running:
            return
        self._running = True
        self.status_frame.set_status("loading", "Loading models…")
        self.control_frame.set_running(True)
        threading.Thread(target=self._engine_thread, daemon=True).start()

    def _engine_thread(self):
        try:
            from ..core.engine import VoiceEngine
            from ..i18n import set_language, get_language, WHISPER_LANG_MAP, DEFAULT_WAKE_WORDS
            import os

            app_lang = config_language(self.config)
            set_language(app_lang)
            lang_code = get_language()

            # Auto-set whisper language
            if not os.getenv("WHISPER_LANGUAGE"):
                self.config.setdefault("stt", {}).setdefault("whisper", {})["language"] = (
                    WHISPER_LANG_MAP.get(lang_code, lang_code)
                )

            # Auto-set wake word
            wake_cfg = self.config.get("wake_word", {})
            default_wake = DEFAULT_WAKE_WORDS.get(lang_code, DEFAULT_WAKE_WORDS["en"])
            if not os.getenv("WAKE_WORD"):
                wake_cfg["word"] = default_wake["word"]
                wake_cfg["aliases"] = default_wake["aliases"]
                self.config["wake_word"] = wake_cfg

            self._engine = VoiceEngine(self.config)
            self._engine.setup()

            # Start remote server
            if self.config.get("remote", {}).get("enabled", True):
                from ..remote.server import start_server
                start_server(self.config.get("remote", {}), self._engine, lang_code)

            self._start_listener()

            self.after(0, lambda: self.status_frame.set_status(
                "active",
                f"Listening ({self._mode.replace('_', ' ')})"
            ))
            self.after(0, lambda: self.log_frame.add_entry(
                "system", "✓ Engine started. Ready for commands."
            ))
        except Exception as e:
            logger.exception("Failed to start engine")
            self.after(0, lambda: self.status_frame.set_status("error", str(e)))
            self.after(0, lambda: self.control_frame.set_running(False))
            self._running = False

    def _start_listener(self):
        """Start the appropriate listener based on current mode."""
        if not self._engine:
            return

        if self._mode == "text":
            # No audio listener needed in text mode
            return

        if self._mode == "ptt":
            from ..audio.listener import PushToTalkListener
            self._listener = PushToTalkListener(self.config, self._on_audio_command)
            self._listener.start()
        else:
            from ..audio.listener import AudioListener
            self._listener = AudioListener(self.config, self._on_audio_command)
            self._listener.set_wake_transcriber(self._engine.transcriber)
            self._listener.start()

    def _stop_engine(self):
        """Stop engine and listener."""
        self._running = False
        if self._listener:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None
        self._engine = None
        self.status_frame.set_status("stopped", "Stopped")
        self.control_frame.set_running(False)
        self.log_frame.add_entry("system", "Engine stopped.")

    def _change_mode(self, new_mode: str):
        """Switch between wake_word, ptt, text."""
        was_running = self._running
        if was_running and self._listener:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None

        self._mode = new_mode

        if was_running and self._engine:
            self._start_listener()
            self.status_frame.set_status(
                "active", f"Listening ({new_mode.replace('_', ' ')})"
            )
        self.log_frame.add_entry("system", f"Mode changed to: {new_mode.replace('_', ' ')}")

    # ────────────────────────────────────────────────────────────────
    # Command handling
    # ────────────────────────────────────────────────────────────────
    def _on_audio_command(self, audio):
        """Called by listener when voice command audio is captured."""
        if not self._engine:
            return
        self.after(0, lambda: self.status_frame.set_status("processing", "Processing…"))
        try:
            result = self._engine.process_audio(audio)
            if result:
                self.after(0, lambda r=result: self._show_result(r))
        except Exception as e:
            self.after(0, lambda: self.log_frame.add_entry("error", f"Error: {e}"))
        finally:
            self.after(0, lambda: self.status_frame.set_status(
                "active", f"Listening ({self._mode.replace('_', ' ')})"
            ))

    def _send_text_command(self, text: str):
        """Process a text command typed in the input field."""
        if not self._engine:
            self.log_frame.add_entry("error", "Engine not running. Click Start first.")
            return
        self.log_frame.add_entry("command", text)
        self.status_frame.set_status("processing", "Processing…")

        def process():
            try:
                result = self._engine.process_text(text)
                self.after(0, lambda r=result: self._show_result(r))
            except Exception as e:
                self.after(0, lambda: self.log_frame.add_entry("error", f"Error: {e}"))
            finally:
                self.after(0, lambda: self.status_frame.set_status(
                    "active", f"Listening ({self._mode.replace('_', ' ')})"
                ))

        threading.Thread(target=process, daemon=True).start()

    def _show_result(self, result: str):
        self.log_frame.add_entry("response", result)

    # ────────────────────────────────────────────────────────────────
    # Settings toggle
    # ────────────────────────────────────────────────────────────────
    def _toggle_settings(self):
        if self._settings_visible:
            if self.settings_frame:
                self.settings_frame.destroy()
                self.settings_frame = None
            self._settings_visible = False
        else:
            self.settings_frame = SettingsFrame(
                self, self.config, on_save=self._apply_settings,
            )
            # Insert between control_frame and log_frame
            self.settings_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=4)
            self.control_frame.grid(row=2)  # push down handled by new row
            self.settings_frame.grid(row=5, column=0, sticky="ew", padx=12, pady=4)
            self._settings_visible = True

    def _apply_settings(self, new_config: dict):
        """Apply settings changes."""
        self.config.update(new_config)
        self.log_frame.add_entry("system", "Settings updated.")
        # Save to yaml
        try:
            import yaml
            from ..paths import get_config_dir
            config_path = get_config_dir() / "settings.yaml"
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            self.log_frame.add_entry("system", "Settings saved to config/settings.yaml")
        except Exception as e:
            self.log_frame.add_entry("error", f"Failed to save settings: {e}")

        # Re-init AI clients if engine is running (picks up new API keys from os.environ)
        if self._engine and hasattr(self._engine, "intent_parser"):
            try:
                self._engine.intent_parser._init_clients()
                self.log_frame.add_entry("system", "AI clients reloaded.")
            except Exception as e:
                self.log_frame.add_entry("error", f"Failed to reload AI clients: {e}")

    # ────────────────────────────────────────────────────────────────
    # Logging integration
    # ────────────────────────────────────────────────────────────────
    def _install_log_handler(self):
        """Route Python logging to the GUI log frame."""
        handler = GUILogHandler(self)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(name)s: %(message)s"))
        logging.getLogger().addHandler(handler)

    # ────────────────────────────────────────────────────────────────
    # System tray
    # ────────────────────────────────────────────────────────────────
    def _init_tray(self):
        try:
            self._tray = SystemTrayManager(
                on_show=self._show_from_tray,
                on_quit=self._quit_app,
            )
            self._tray.start()
        except Exception:
            logger.debug("System tray not available")

    def _show_from_tray(self):
        self.after(0, self.deiconify)

    # ────────────────────────────────────────────────────────────────
    # Window management
    # ────────────────────────────────────────────────────────────────
    def _set_icon(self):
        try:
            icon_path = Path(__file__).parent / "assets" / "icon.ico"
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
        except Exception:
            pass

    def _on_close(self):
        """Minimize to tray on close, unless no tray available."""
        if self._tray and self._tray.is_alive():
            self.withdraw()
        else:
            self._quit_app()

    def _quit_app(self):
        self._stop_engine()
        if self._tray:
            self._tray.stop()
        self.destroy()


class GUILogHandler(logging.Handler):
    """Routes log records to the GUI log frame."""

    def __init__(self, app: VoxControlApp):
        super().__init__()
        self.app = app

    def emit(self, record):
        try:
            msg = self.format(record)
            level = record.levelname.lower()
            kind = "error" if level in ("error", "critical") else "system"
            self.app.after(0, lambda: self.app.log_frame.add_entry(kind, msg))
        except Exception:
            pass


def config_language(config: dict) -> str:
    return config.get("app", {}).get("language", "pt-BR")
