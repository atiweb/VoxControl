"""
Settings panel -- inline configurable options.
"""

import os
import logging
import threading
import customtkinter as ctk
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)

SURFACE_DARK = "#161B22"
CARD_DARK = "#21262D"
PRIMARY = "#6C63FF"
SUCCESS = "#3FB950"
ERROR = "#F85149"
WARNING = "#D29922"
TEXT_PRIMARY = "#E6EDF3"
TEXT_SECONDARY = "#8B949E"

# faster-whisper model repo names on HuggingFace
_WHISPER_REPOS = {
    "tiny": "Systran/faster-whisper-tiny",
    "base": "Systran/faster-whisper-base",
    "small": "Systran/faster-whisper-small",
    "medium": "Systran/faster-whisper-medium",
    "large-v3": "Systran/faster-whisper-large-v3",
}


def _hf_cache_dir() -> Path:
    """Return the HuggingFace hub cache directory."""
    return Path(os.environ.get(
        "HF_HOME", Path.home() / ".cache" / "huggingface"
    )) / "hub"


def _is_model_cached(model_size: str) -> bool:
    """Check if a faster-whisper model is already downloaded."""
    repo = _WHISPER_REPOS.get(model_size, "")
    if not repo:
        return False
    # HF cache uses models--{org}--{name} directory structure
    dir_name = "models--" + repo.replace("/", "--")
    cache_path = _hf_cache_dir() / dir_name
    if not cache_path.exists():
        return False
    # Check that snapshots directory has content (model actually downloaded)
    snapshots = cache_path / "snapshots"
    if snapshots.exists():
        return any(snapshots.iterdir())
    return False


class SettingsFrame(ctk.CTkFrame):
    """Expandable settings panel for quick configuration."""

    def __init__(self, parent, config: dict, *, on_save: Callable[[dict], None]):
        super().__init__(parent, fg_color=SURFACE_DARK, corner_radius=10)
        self.grid_columnconfigure(1, weight=1)
        self._config = config
        self._on_save = on_save
        self._downloading = False

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

        # ── Claude API Key ──────────────────────────────────────────
        ctk.CTkLabel(
            self, text="Claude API Key", font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
        ).grid(row=row, column=0, sticky="w", padx=12, pady=4)

        key_frame_claude = ctk.CTkFrame(self, fg_color="transparent")
        key_frame_claude.grid(row=row, column=1, columnspan=2, sticky="ew", padx=8, pady=4)
        key_frame_claude.grid_columnconfigure(0, weight=1)

        self._claude_key_entry = ctk.CTkEntry(
            key_frame_claude, height=32, show="•",
            fg_color=CARD_DARK, border_color="#30363D",
            placeholder_text="sk-ant-...",
            font=ctk.CTkFont(size=11),
        )
        self._claude_key_entry.grid(row=0, column=0, sticky="ew")
        current_claude = os.environ.get("ANTHROPIC_API_KEY", "")
        if current_claude:
            self._claude_key_entry.insert(0, current_claude)

        self._claude_show = False
        self._claude_toggle_btn = ctk.CTkButton(
            key_frame_claude, text="👁", width=32, height=32,
            fg_color="transparent", hover_color=CARD_DARK,
            font=ctk.CTkFont(size=14),
            command=lambda: self._toggle_key_visibility("claude"),
        )
        self._claude_toggle_btn.grid(row=0, column=1, padx=(4, 0))
        row += 1

        # ── OpenAI API Key ──────────────────────────────────────────
        ctk.CTkLabel(
            self, text="OpenAI API Key", font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
        ).grid(row=row, column=0, sticky="w", padx=12, pady=4)

        key_frame_openai = ctk.CTkFrame(self, fg_color="transparent")
        key_frame_openai.grid(row=row, column=1, columnspan=2, sticky="ew", padx=8, pady=4)
        key_frame_openai.grid_columnconfigure(0, weight=1)

        self._openai_key_entry = ctk.CTkEntry(
            key_frame_openai, height=32, show="•",
            fg_color=CARD_DARK, border_color="#30363D",
            placeholder_text="sk-...",
            font=ctk.CTkFont(size=11),
        )
        self._openai_key_entry.grid(row=0, column=0, sticky="ew")
        current_openai = os.environ.get("OPENAI_API_KEY", "")
        if current_openai:
            self._openai_key_entry.insert(0, current_openai)

        self._openai_show = False
        self._openai_toggle_btn = ctk.CTkButton(
            key_frame_openai, text="👁", width=32, height=32,
            fg_color="transparent", hover_color=CARD_DARK,
            font=ctk.CTkFont(size=14),
            command=lambda: self._toggle_key_visibility("openai"),
        )
        self._openai_toggle_btn.grid(row=0, column=1, padx=(4, 0))
        row += 1

        # ── Whisper Model ───────────────────────────────────────────
        ctk.CTkLabel(
            self, text="Whisper Model", font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY,
        ).grid(row=row, column=0, sticky="w", padx=12, pady=4)

        whisper_frame = ctk.CTkFrame(self, fg_color="transparent")
        whisper_frame.grid(row=row, column=1, columnspan=2, sticky="ew", padx=8, pady=4)

        self._model_var = ctk.StringVar(
            value=config.get("stt", {}).get("whisper", {}).get("model_size", "small")
        )
        self._model_var.trace_add("write", lambda *_: self._update_model_status())

        model_menu = ctk.CTkOptionMenu(
            whisper_frame, values=["tiny", "base", "small", "medium", "large-v3"],
            variable=self._model_var, width=120,
            fg_color=CARD_DARK, button_color=PRIMARY,
            font=ctk.CTkFont(size=12),
        )
        model_menu.pack(side="left")

        self._model_status_label = ctk.CTkLabel(
            whisper_frame, text="", font=ctk.CTkFont(size=11),
            text_color=TEXT_SECONDARY,
        )
        self._model_status_label.pack(side="left", padx=(8, 4))

        self._download_btn = ctk.CTkButton(
            whisper_frame, text="⬇ Download", width=90, height=28,
            font=ctk.CTkFont(size=11), fg_color=PRIMARY, hover_color="#5a52e0",
            command=self._download_model,
        )
        self._download_btn.pack(side="left", padx=(4, 0))
        row += 1

        # Update model status indicator
        self._update_model_status()

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

    # ── API key visibility toggle ───────────────────────────────────
    def _toggle_key_visibility(self, provider: str):
        if provider == "claude":
            self._claude_show = not self._claude_show
            self._claude_key_entry.configure(show="" if self._claude_show else "•")
        else:
            self._openai_show = not self._openai_show
            self._openai_key_entry.configure(show="" if self._openai_show else "•")

    # ── Whisper model status ────────────────────────────────────────
    def _update_model_status(self):
        model = self._model_var.get()
        if _is_model_cached(model):
            self._model_status_label.configure(text="✓ Ready", text_color=SUCCESS)
            self._download_btn.configure(state="normal", text="⬇ Re-download")
        else:
            self._model_status_label.configure(text="✗ Not downloaded", text_color=WARNING)
            self._download_btn.configure(state="normal", text="⬇ Download")

    def _download_model(self):
        if self._downloading:
            return
        self._downloading = True
        model = self._model_var.get()
        self._download_btn.configure(state="disabled", text="Downloading…")
        self._model_status_label.configure(text="⏳ Downloading…", text_color=TEXT_SECONDARY)
        threading.Thread(target=self._do_download, args=(model,), daemon=True).start()

    def _do_download(self, model_size: str):
        """Download a faster-whisper model in background."""
        try:
            from faster_whisper import WhisperModel
            logger.info(f"Downloading Whisper model '{model_size}'…")
            # This triggers the HuggingFace download
            WhisperModel(model_size, device="cpu", compute_type="int8")
            logger.info(f"Whisper model '{model_size}' downloaded.")
            self.after(0, lambda: self._on_download_done(model_size, True))
        except Exception as e:
            logger.error(f"Failed to download Whisper model: {e}")
            self.after(0, lambda: self._on_download_done(model_size, False, str(e)))

    def _on_download_done(self, model_size: str, success: bool, error: str = ""):
        self._downloading = False
        if success:
            self._model_status_label.configure(text="✓ Ready", text_color=SUCCESS)
            self._download_btn.configure(state="normal", text="⬇ Re-download")
        else:
            self._model_status_label.configure(
                text=f"✗ Error: {error[:40]}", text_color=ERROR
            )
            self._download_btn.configure(state="normal", text="⬇ Retry")

    # ── Save ────────────────────────────────────────────────────────
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

        # Save API keys to .env and os.environ
        claude_key = self._claude_key_entry.get().strip()
        openai_key = self._openai_key_entry.get().strip()
        self._save_api_keys(claude_key, openai_key)

        self._on_save(new)

    def _save_api_keys(self, claude_key: str, openai_key: str):
        """Persist API keys to .env file and update os.environ."""
        # Update environment immediately
        if claude_key:
            os.environ["ANTHROPIC_API_KEY"] = claude_key
        elif "ANTHROPIC_API_KEY" in os.environ:
            del os.environ["ANTHROPIC_API_KEY"]

        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
        elif "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]

        # Write to .env file
        try:
            from ...paths import get_data_dir
            env_path = get_data_dir() / ".env"
        except Exception:
            env_path = Path(".env")

        # Read existing .env content
        lines: list[str] = []
        if env_path.exists():
            lines = env_path.read_text(encoding="utf-8").splitlines()

        # Update or add keys
        updated = {"ANTHROPIC_API_KEY": False, "OPENAI_API_KEY": False}
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("ANTHROPIC_API_KEY="):
                new_lines.append(f"ANTHROPIC_API_KEY={claude_key}")
                updated["ANTHROPIC_API_KEY"] = True
            elif stripped.startswith("OPENAI_API_KEY="):
                new_lines.append(f"OPENAI_API_KEY={openai_key}")
                updated["OPENAI_API_KEY"] = True
            else:
                new_lines.append(line)

        if not updated["ANTHROPIC_API_KEY"] and claude_key:
            new_lines.append(f"ANTHROPIC_API_KEY={claude_key}")
        if not updated["OPENAI_API_KEY"] and openai_key:
            new_lines.append(f"OPENAI_API_KEY={openai_key}")

        env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        logger.info(f"API keys saved to {env_path}")
