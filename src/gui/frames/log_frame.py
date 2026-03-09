"""
Log / history frame -- scrollable log with colour-coded entries.
"""

import customtkinter as ctk
from datetime import datetime

SURFACE_DARK = "#161B22"
CARD_DARK = "#21262D"
PRIMARY = "#6C63FF"
ACCENT = "#00D9FF"
SUCCESS = "#3FB950"
ERROR = "#F85149"
WARNING = "#D29922"
TEXT_PRIMARY = "#E6EDF3"
TEXT_SECONDARY = "#8B949E"

ENTRY_COLOURS = {
    "command": PRIMARY,
    "response": SUCCESS,
    "error": ERROR,
    "system": TEXT_SECONDARY,
}

ENTRY_PREFIX = {
    "command": "▸ ",
    "response": "◂ ",
    "error": "✗ ",
    "system": "• ",
}

MAX_LOG_ENTRIES = 500


class LogFrame(ctk.CTkFrame):
    """Scrollable log display with colour-coded entries."""

    def __init__(self, parent, config: dict):
        super().__init__(parent, fg_color=SURFACE_DARK, corner_radius=10)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── Header ──────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent", height=28)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 0))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="Command History",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SECONDARY,
        ).grid(row=0, column=0, sticky="w")

        self._clear_btn = ctk.CTkButton(
            header, text="Clear", width=50, height=22,
            font=ctk.CTkFont(size=11),
            fg_color="transparent", hover_color=CARD_DARK,
            text_color=TEXT_SECONDARY,
            command=self.clear,
        )
        self._clear_btn.grid(row=0, column=1, sticky="e")

        # ── Scrollable text area ────────────────────────────────────
        self._text = ctk.CTkTextbox(
            self, fg_color=CARD_DARK, corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=13),
            text_color=TEXT_PRIMARY,
            wrap="word",
            activate_scrollbars=True,
            state="disabled",
        )
        self._text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(4, 10))

        self._entry_count = 0

    def add_entry(self, kind: str, text: str):
        """Add a log entry. `kind` is one of: command, response, error, system."""
        colour = ENTRY_COLOURS.get(kind, TEXT_SECONDARY)
        prefix = ENTRY_PREFIX.get(kind, "  ")
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Configure a tag for this colour if not present
        tag = f"tag_{kind}"

        self._text.configure(state="normal")

        # Add text
        line = f"[{timestamp}] {prefix}{text}\n"
        self._text.insert("end", line, tag)

        # Colour the tag
        try:
            self._text._textbox.tag_configure(tag, foreground=colour)
        except Exception:
            pass

        self._text.see("end")
        self._text.configure(state="disabled")

        self._entry_count += 1
        if self._entry_count > MAX_LOG_ENTRIES:
            self._trim()

    def clear(self):
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.configure(state="disabled")
        self._entry_count = 0

    def _trim(self):
        """Remove oldest entries when log grows too large."""
        self._text.configure(state="normal")
        # Delete first 100 lines
        self._text.delete("1.0", "100.0")
        self._text.configure(state="disabled")
        self._entry_count -= 100
