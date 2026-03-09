"""
Settings panel -- inline configurable options.
"""

import customtkinter as ctk
from typing import Callable

SURFACE_DARK = "#161B22"
CARD_DARK = "#21262D"
PRIMARY = "#6C63FF"
SUCCESS = "#3FB950"
TEXT_PRIMARY = "#E6EDF3"
TEXT_SECONDARY = "#8B949E"


class SettingsFrame(ctk.CTkFrame):
    """Expandable settings panel for quick configuration."""

    def __init__(self, parent, config: dict, *, on_save: Callable[[dict], None]):
        super().__init__(parent, fg_color=SURFACE_DARK, corner_radius=10)
        self.grid_columnconfigure(1, weight=1)
        self._config = config
        self._on_save = on_save

        row = 0

        # ── Title ───────────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="⚙  Settings", font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).grid(row=row, column=0, columnspan=3, sticky="w", padx=12, pady=(10, 8))
        row += 1

        # ── Language ────────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="Language", font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
        ).grid(row=row, column=0, sticky="w", padx=12, pady=4)

        self._lang_var = ctk.StringVar(
            value=config.get("app", {}).get("language", "pt-BR")
        )
        lang_menu = ctk.CTkOptionMenu(
            self, values=["pt-BR", "es-ES", "en-US"],
            variable=self._lang_var, width=140,
            fg_color=CARD_DARK, button_color=PRIMARY,
            font=ctk.CTkFont(size=12),
        )
        lang_menu.grid(row=row, column=1, sticky="w", padx=8, pady=4)
        row += 1

        # ── AI Backend ──────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="AI Backend", font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
        ).grid(row=row, column=0, sticky="w", padx=12, pady=4)

        self._backend_var = ctk.StringVar(
            value=config.get("ai", {}).get("backend", "claude")
        )
        backend_menu = ctk.CTkOptionMenu(
            self, values=["claude", "openai", "offline"],
            variable=self._backend_var, width=140,
            fg_color=CARD_DARK, button_color=PRIMARY,
            font=ctk.CTkFont(size=12),
        )
        backend_menu.grid(row=row, column=1, sticky="w", padx=8, pady=4)
        row += 1

        # ── Whisper Model ───────────────────────────────────────────
        ctk.CTkLabel(
            self, text="Whisper Model", font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
        ).grid(row=row, column=0, sticky="w", padx=12, pady=4)

        self._model_var = ctk.StringVar(
            value=config.get("stt", {}).get("whisper", {}).get("model_size", "small")
        )
        model_menu = ctk.CTkOptionMenu(
            self, values=["tiny", "base", "small", "medium", "large-v3"],
            variable=self._model_var, width=140,
            fg_color=CARD_DARK, button_color=PRIMARY,
            font=ctk.CTkFont(size=12),
        )
        model_menu.grid(row=row, column=1, sticky="w", padx=8, pady=4)
        row += 1

        # ── Voice enabled ───────────────────────────────────────────
        self._voice_var = ctk.BooleanVar(
            value=config.get("voice_response", {}).get("enabled", True)
        )
        voice_switch = ctk.CTkSwitch(
            self, text="Voice responses (TTS)",
            variable=self._voice_var,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            progress_color=SUCCESS,
        )
        voice_switch.grid(row=row, column=0, columnspan=2, sticky="w", padx=12, pady=4)
        row += 1

        # ── Remote enabled ──────────────────────────────────────────
        self._remote_var = ctk.BooleanVar(
            value=config.get("remote", {}).get("enabled", True)
        )
        remote_switch = ctk.CTkSwitch(
            self, text="Remote server (mobile)",
            variable=self._remote_var,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
            progress_color=SUCCESS,
        )
        remote_switch.grid(row=row, column=0, columnspan=2, sticky="w", padx=12, pady=4)
        row += 1

        # ── Remote port ─────────────────────────────────────────────
        ctk.CTkLabel(
            self, text="Remote Port", font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
        ).grid(row=row, column=0, sticky="w", padx=12, pady=4)

        self._port_entry = ctk.CTkEntry(
            self, width=100, height=32,
            fg_color=CARD_DARK, border_color="#30363D",
            font=ctk.CTkFont(size=12),
        )
        self._port_entry.insert(0, str(config.get("remote", {}).get("port", 8765)))
        self._port_entry.grid(row=row, column=1, sticky="w", padx=8, pady=4)
        row += 1

        # ── Save button ─────────────────────────────────────────────
        save_btn = ctk.CTkButton(
            self, text="Save Changes", width=140, height=34,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=PRIMARY, hover_color="#5a52e0",
            command=self._save,
        )
        save_btn.grid(row=row, column=0, columnspan=2, pady=(8, 12), padx=12, sticky="w")

    def _save(self):
        new = dict(self._config)  # shallow copy
        new.setdefault("app", {})["language"] = self._lang_var.get()
        new.setdefault("ai", {})["backend"] = self._backend_var.get()
        new.setdefault("stt", {}).setdefault("whisper", {})["model_size"] = self._model_var.get()
        new.setdefault("voice_response", {})["enabled"] = self._voice_var.get()
        new.setdefault("remote", {})["enabled"] = self._remote_var.get()

        port_text = self._port_entry.get().strip()
        if port_text.isdigit() and 1024 <= int(port_text) <= 65535:
            new.setdefault("remote", {})["port"] = int(port_text)

        self._on_save(new)
