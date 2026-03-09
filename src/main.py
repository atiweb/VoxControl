"""
VoxControl -- Ponto de entrada principal.

Uso:
  python -m src.main               # modo padrao (wake word)
  python -m src.main --ptt         # Push-to-Talk (F12)
  python -m src.main --text        # apenas texto (sem microfone)
  python -m src.main --no-remote   # desabilita servidor mobile
  python -m src.main --lang es     # usar espanhol
  python -m src.main --lang en     # usar ingles
"""

import argparse
import logging
import os
import signal
import sys
import time
from pathlib import Path

# Carrega variaveis de ambiente de .env se existir
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def load_config() -> dict:
    """Carrega configuracoes de config/settings.yaml com overrides do .env."""
    config_path = Path("config/settings.yaml")
    config = {}

    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

    # Overrides do .env
    overrides = {
        "app": {
            "language": os.getenv("APP_LANGUAGE"),
        },
        "ai": {
            "backend": os.getenv("AI_BACKEND"),
            "claude": {"model": os.getenv("CLAUDE_MODEL")},
            "openai": {"model": os.getenv("OPENAI_MODEL")},
        },
        "stt": {
            "whisper": {
                "model_size": os.getenv("WHISPER_MODEL"),
                "language": os.getenv("WHISPER_LANGUAGE"),
            }
        },
        "wake_word": {
            "word": os.getenv("WAKE_WORD"),
            "listen_timeout": int(os.getenv("LISTEN_TIMEOUT", 0)) or None,
        },
        "voice_response": {
            "enabled": os.getenv("VOICE_RESPONSE", "").lower() == "true"
            if os.getenv("VOICE_RESPONSE") else None,
        },
        "remote": {
            "host": os.getenv("REMOTE_SERVER_HOST"),
            "port": int(os.getenv("REMOTE_SERVER_PORT", 0)) or None,
            "ssl_certfile": os.getenv("SSL_CERTFILE"),
            "ssl_keyfile": os.getenv("SSL_KEYFILE"),
        },
        "logging": {"level": os.getenv("LOG_LEVEL")},
    }

    def deep_merge(base: dict, override: dict) -> dict:
        result = base.copy()
        for k, v in override.items():
            if v is None:
                continue
            if isinstance(v, dict) and isinstance(result.get(k), dict):
                result[k] = deep_merge(result[k], v)
            else:
                result[k] = v
        return result

    return deep_merge(config, overrides)


def setup_logging(config: dict):
    level_str = config.get("logging", {}).get("level", "INFO")
    level = getattr(logging, level_str.upper(), logging.INFO)
    log_file = config.get("logging", {}).get("file", "logs/voxcontrol.log")
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def print_banner(config: dict, mode: str):
    from src.i18n import t

    backend = config.get("ai", {}).get("backend", "offline")
    wake = config.get("wake_word", {}).get("word", "computador")
    remote_port = config.get("remote", {}).get("port", 8765)
    remote_enabled = config.get("remote", {}).get("enabled", True)
    lang = config.get("app", {}).get("language", "pt-BR")

    text = Text()
    text.append("  VoxControl\n", style="bold bright_magenta")
    text.append(f"  IA: {backend.upper()}  |  Mode: {mode}  |  Lang: {lang}\n", style="cyan")
    if mode == "wake_word":
        text.append(f"  {t('wake_word_label', wake=wake)}\n", style="yellow")
    elif mode == "ptt":
        text.append(f"  {t('ptt_label')}\n", style="yellow")
    if remote_enabled:
        text.append(f"  Remote: http://IP:{remote_port}\n", style="green")
    text.append("  Ctrl+C to exit", style="dim")

    console.print(Panel(text, border_style="bright_magenta", padding=(0, 2)))


def main():
    parser = argparse.ArgumentParser(description="VoxControl -- voice control for Windows")
    parser.add_argument("--ptt", action="store_true", help="Push-to-Talk mode (F12)")
    parser.add_argument("--text", action="store_true", help="Text mode (no microphone)")
    parser.add_argument("--no-remote", action="store_true", help="Disable remote server")
    parser.add_argument("--no-voice", action="store_true", help="Disable voice responses")
    parser.add_argument("--lang", type=str, default=None,
                        help="Language: pt, pt-BR, es, es-ES, en, en-US (overrides config)")
    parser.add_argument("--setup", action="store_true", help="Only verify installation")
    args = parser.parse_args()

    config = load_config()
    setup_logging(config)
    logger = logging.getLogger(__name__)

    # ---- Set language ----
    # Priority: CLI --lang > .env APP_LANGUAGE > settings.yaml app.language
    if args.lang:
        config.setdefault("app", {})["language"] = args.lang

    app_language = config.get("app", {}).get("language", "pt-BR")

    # Initialize i18n
    from src.i18n import set_language, get_language, WHISPER_LANG_MAP, DEFAULT_WAKE_WORDS
    set_language(app_language)
    lang_code = get_language()  # 2-letter code

    # Auto-set Whisper language if not explicitly overridden
    whisper_lang_env = os.getenv("WHISPER_LANGUAGE")
    if not whisper_lang_env:
        config.setdefault("stt", {}).setdefault("whisper", {})["language"] = WHISPER_LANG_MAP.get(lang_code, lang_code)

    # Auto-set wake word defaults if not explicitly overridden by user
    wake_cfg = config.get("wake_word", {})
    default_wake = DEFAULT_WAKE_WORDS.get(lang_code, DEFAULT_WAKE_WORDS["en"])
    if not os.getenv("WAKE_WORD"):
        wake_cfg["word"] = default_wake["word"]
        wake_cfg["aliases"] = default_wake["aliases"]
        config["wake_word"] = wake_cfg

    if args.no_voice:
        config.setdefault("voice_response", {})["enabled"] = False

    if args.setup:
        _run_setup_check()
        return

    # Determinar modo
    mode = "text" if args.text else ("ptt" if args.ptt else "wake_word")
    print_banner(config, mode)

    # Inicializar engine
    from src.core.engine import VoiceEngine
    from src.i18n import t

    engine = VoiceEngine(config)
    console.print(f"[yellow]{t('loading_models')}[/yellow]")
    engine.setup()
    console.print(f"[green]{t('ready')}[/green]\n")

    # Servidor remoto
    if not args.no_remote and config.get("remote", {}).get("enabled", True):
        from src.remote.server import start_server
        start_server(config.get("remote", {}), engine, lang_code)

    # Sinal de saida limpa
    def handle_exit(sig, frame):
        console.print(f"\n[yellow]{t('shutting_down')}[/yellow]")
        sys.exit(0)
    signal.signal(signal.SIGINT, handle_exit)

    # ---- Modo texto ----
    if args.text:
        exit_words = t("exit_words").split(",")
        console.print(f"[cyan]{t('text_mode_prompt')}[/cyan]")
        while True:
            try:
                cmd = input(">>> ").strip()
                if cmd.lower() in exit_words:
                    break
                if cmd:
                    result = engine.process_text(cmd)
                    console.print(f"[green]-> {result}[/green]")
            except (EOFError, KeyboardInterrupt):
                break
        return

    # ---- Modo Push-to-Talk ----
    if args.ptt:
        from src.audio.listener import PushToTalkListener
        listener = PushToTalkListener(config, engine.process_audio)
        listener.start()
        console.print(f"[cyan]{t('hold_f12')}[/cyan]")
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        return

    # ---- Modo Wake Word (padrao) ----
    from src.audio.listener import AudioListener

    def on_command(audio):
        result = engine.process_audio(audio)
        if result:
            console.print(f"[green]-> {result}[/green]")

    listener = AudioListener(config, on_command)
    listener.set_wake_transcriber(engine.transcriber)
    listener.start()

    wake = config.get("wake_word", {}).get("word", "computador")
    console.print(f"[cyan]{t('say_wake_word', wake=wake)}[/cyan]")

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()


def _run_setup_check():
    """Verifica se todos os requisitos estao instalados."""
    console.print("[bold cyan]Checking installation...[/bold cyan]\n")
    checks = [
        ("faster_whisper", "faster-whisper"),
        ("sounddevice", "sounddevice"),
        ("pyautogui", "pyautogui"),
        ("pywinauto", "pywinauto"),
        ("pyttsx3", "pyttsx3"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("anthropic", "anthropic (Claude API)"),
        ("openai", "openai (OpenAI API)"),
        ("yaml", "pyyaml"),
        ("dotenv", "python-dotenv"),
        ("win32com", "pywin32 (Office COM)"),
        ("qrcode", "qrcode"),
        ("vosk", "vosk (optional)"),
    ]

    all_ok = True
    for module, name in checks:
        try:
            __import__(module)
            console.print(f"  [green]OK[/green]  {name}")
        except ImportError:
            console.print(f"  [red]FALTA[/red] {name}")
            all_ok = False

    # Verificar chaves de API
    console.print()
    for key, desc in [("ANTHROPIC_API_KEY", "Claude key"), ("OPENAI_API_KEY", "OpenAI key")]:
        val = os.getenv(key)
        if val:
            console.print(f"  [green]OK[/green]  {desc} found")
        else:
            console.print(f"  [yellow]--[/yellow]  {desc} not configured (optional but recommended)")

    console.print()
    if all_ok:
        console.print("[bold green]All ready! Run: python -m src.main[/bold green]")
    else:
        console.print("[yellow]Run: pip install -r requirements.txt[/yellow]")


if __name__ == "__main__":
    main()
