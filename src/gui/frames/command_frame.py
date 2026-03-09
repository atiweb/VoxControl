"""
Command input frame -- text field + send button + quick-action buttons.
"""

import customtkinter as ctk
from typing import Callable

SURFACE_DARK = "#161B22"
CARD_DARK = "#21262D"
PRIMARY = "#6C63FF"
ACCENT = "#00D9FF"
TEXT_PRIMARY = "#E6EDF3"
TEXT_SECONDARY = "#8B949E"

# Quick-action shortcuts visible to users
QUICK_ACTIONS = [
    ("🌐", "open chrome"),
    ("📸", "screenshot"),
    ("🔊", "volume up"),
    ("🔉", "volume down"),
    ("🔇", "mute"),
    ("🔒", "lock screen"),
    ("⏯", "play pause"),
    ("⏭", "next track"),
]


class CommandFrame(ctk.CTkFrame):
    """Text input field + send button + quick actions row."""

    def __init__(self, parent, config: dict, *, on_send: Callable[[str], None]):
        super().__init__(parent, fg_color=SURFACE_DARK, corner_radius=10)
        self.grid_columnconfigure(0, weight=1)
        self._on_send = on_send

        # ── Quick actions row ───────────────────────────────────────
        qa_frame = ctk.CTkFrame(self, fg_color="transparent")
        qa_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=(8, 4))

        for i, (icon, cmd) in enumerate(QUICK_ACTIONS):
            btn = ctk.CTkButton(
                qa_frame, text=icon, width=38, height=32,
                font=ctk.CTkFont(size=16),
                fg_color=CARD_DARK, hover_color="#30363D",
                corner_radius=8,
                command=lambda c=cmd: self._send(c),
            )
            btn.pack(side="left", padx=2)
            # Tooltip on hover
            btn.bind("<Enter>", lambda e, c=cmd, b=btn: self._show_tooltip(b, c))
            btn.bind("<Leave>", lambda e: self._hide_tooltip())

        # ── Input field + send button ───────────────────────────────
        self._entry = ctk.CTkEntry(
            self, placeholder_text="Type a command…",
            font=ctk.CTkFont(size=14), height=40,
            fg_color=CARD_DARK, border_color="#30363D",
            text_color=TEXT_PRIMARY,
        )
        self._entry.grid(row=1, column=0, sticky="ew", padx=(10, 4), pady=(4, 10))
        self._entry.bind("<Return>", lambda e: self._send_from_entry())

        self._send_btn = ctk.CTkButton(
            self, text="➤", width=44, height=40,
            font=ctk.CTkFont(size=18),
            fg_color=PRIMARY, hover_color="#5a52e0",
            corner_radius=8,
            command=self._send_from_entry,
        )
        self._send_btn.grid(row=1, column=1, padx=(0, 10), pady=(4, 10))

        # Tooltip widget (reused)
        self._tooltip: ctk.CTkLabel | None = None

    def _send_from_entry(self):
        text = self._entry.get().strip()
        if text:
            self._send(text)
            self._entry.delete(0, "end")

    def _send(self, text: str):
        self._on_send(text)

    def _show_tooltip(self, widget, text: str):
        self._hide_tooltip()
        x = widget.winfo_rootx()
        y = widget.winfo_rooty() - 30
        self._tooltip = ctk.CTkLabel(
            self.winfo_toplevel(), text=text,
            font=ctk.CTkFont(size=11),
            fg_color=CARD_DARK, corner_radius=6,
            text_color=TEXT_PRIMARY,
            padx=8, pady=2,
        )
        self._tooltip.place(x=x - self.winfo_toplevel().winfo_rootx(),
                            y=y - self.winfo_toplevel().winfo_rooty())

    def _hide_tooltip(self):
        if self._tooltip:
            self._tooltip.destroy()
            self._tooltip = None
