"""
Status bar frame -- shows current engine state with coloured indicator.
"""

import customtkinter as ctk

BG_DARK = "#0D1117"
SURFACE_DARK = "#161B22"
CARD_DARK = "#21262D"
PRIMARY = "#6C63FF"
SUCCESS = "#3FB950"
ERROR = "#F85149"
WARNING = "#D29922"
TEXT_PRIMARY = "#E6EDF3"
TEXT_SECONDARY = "#8B949E"

STATE_COLOURS = {
    "stopped": TEXT_SECONDARY,
    "loading": WARNING,
    "active": SUCCESS,
    "processing": PRIMARY,
    "error": ERROR,
}

STATE_ICONS = {
    "stopped": "⏹",
    "loading": "⏳",
    "active": "🟢",
    "processing": "⚡",
    "error": "🔴",
}


class StatusFrame(ctk.CTkFrame):
    """Compact status bar showing current engine state."""

    def __init__(self, parent, config: dict):
        super().__init__(parent, fg_color=SURFACE_DARK, corner_radius=8, height=36)
        self.grid_columnconfigure(1, weight=1)

        self._indicator = ctk.CTkLabel(
            self, text="⏹", font=ctk.CTkFont(size=14), width=24,
        )
        self._indicator.grid(row=0, column=0, padx=(10, 4), pady=6)

        self._label = ctk.CTkLabel(
            self, text="Ready — click Start to begin",
            font=ctk.CTkFont(size=13), text_color=TEXT_SECONDARY,
            anchor="w",
        )
        self._label.grid(row=0, column=1, sticky="w", pady=6)

        self._remote_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=11),
            text_color=TEXT_SECONDARY,
        )
        self._remote_label.grid(row=0, column=2, padx=(4, 10), pady=6)

        # Show remote info if enabled
        remote_cfg = config.get("remote", {})
        if remote_cfg.get("enabled", True):
            port = remote_cfg.get("port", 8765)
            self._remote_label.configure(text=f"📡 :{port}")

    def set_status(self, state: str, message: str):
        colour = STATE_COLOURS.get(state, TEXT_SECONDARY)
        icon = STATE_ICONS.get(state, "⏹")
        self._indicator.configure(text=icon)
        self._label.configure(text=message, text_color=colour)
