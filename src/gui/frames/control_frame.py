"""
Control panel frame -- Start/Stop, mode selector, language selector.
"""

import customtkinter as ctk
from typing import Callable

SURFACE_DARK = "#161B22"
CARD_DARK = "#21262D"
PRIMARY = "#6C63FF"
SUCCESS = "#3FB950"
ERROR = "#F85149"
TEXT_PRIMARY = "#E6EDF3"
TEXT_SECONDARY = "#8B949E"

MODES = {
    "wake_word": "🎙  Wake Word",
    "ptt": "🔘  Push to Talk (F12)",
    "text": "⌨  Text Only",
}


class ControlFrame(ctk.CTkFrame):
    """Start/stop button + mode selector."""

    def __init__(
        self, parent, config: dict, *,
        on_start: Callable, on_stop: Callable,
        on_mode_change: Callable[[str], None],
    ):
        super().__init__(parent, fg_color=SURFACE_DARK, corner_radius=10)
        self.grid_columnconfigure(1, weight=1)
        self._on_start = on_start
        self._on_stop = on_stop
        self._on_mode_change = on_mode_change
        self._is_running = False

        # ── Start / Stop button ─────────────────────────────────────
        self._btn = ctk.CTkButton(
            self, text="▶  Start", width=120, height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=SUCCESS, hover_color="#2ea043",
            text_color="#ffffff",
            command=self._toggle,
        )
        self._btn.grid(row=0, column=0, padx=12, pady=12)

        # ── Mode selector ───────────────────────────────────────────
        mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        mode_frame.grid(row=0, column=1, sticky="e", padx=12, pady=12)

        ctk.CTkLabel(
            mode_frame, text="Mode", font=ctk.CTkFont(size=11),
            text_color=TEXT_SECONDARY,
        ).pack(anchor="e")

        self._mode_var = ctk.StringVar(value="wake_word")

        self._display_var = ctk.StringVar(value=MODES["wake_word"])
        self._mode_menu = ctk.CTkOptionMenu(
            mode_frame,
            values=list(MODES.values()),
            variable=self._display_var,
            command=self._mode_selected,
            width=200, height=32,
            fg_color=CARD_DARK, button_color=PRIMARY,
            button_hover_color="#5a52e0",
            font=ctk.CTkFont(size=12),
        )
        self._mode_menu.pack(anchor="e", pady=(2, 0))

    @property
    def _display_to_key(self) -> dict:
        return {v: k for k, v in MODES.items()}

    def _toggle(self):
        if self._is_running:
            self._on_stop()
        else:
            self._on_start()

    def _mode_selected(self, display_value: str):
        key = self._display_to_key.get(display_value, "wake_word")
        self._on_mode_change(key)

    def set_running(self, running: bool):
        self._is_running = running
        if running:
            self._btn.configure(
                text="⏹  Stop", fg_color=ERROR, hover_color="#d73a49"
            )
        else:
            self._btn.configure(
                text="▶  Start", fg_color=SUCCESS, hover_color="#2ea043"
            )
