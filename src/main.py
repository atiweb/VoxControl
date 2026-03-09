"""
voxcontrol-pt — Ponto de entrada principal.

Uso:
  python -m src.main               # modo padrão (wake word)
  python -m src.main --ptt         # Push-to-Talk (F12)
  python -m src.main --text        # apenas texto (sem microfone)
  python -m src.main --no-remote   # desabilita servidor mobile
"""

import argparse
import logging
import os
import signal
import sys
import time
from pathlib import Path

# Carrega variáveis de ambiente de .env se existir
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
    """Carrega configurações de config/settings.yaml com overrides do .env."""
    config_path = Path("config/settings.yaml")
    config = {}

    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

    # Overrides do .env
    overrides = {
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
    backend = config.get("ai", {}).get("backend", "offline")
    wake = config.get("wake_word", {}).get("word", "computador")
    remote_port = config.get("remote", {}).get("port", 8765)
    remote_enabled = config.get("remote", {}).get("enabled", True)

    text = Text()
    text.append("  VoxControl\n", style="bold bright_magenta")
    text.append(f"  IA: {backend.upper()}  |  Modo: {mode}\n", style="cyan")
    if mode == "wake_word":
        text.append(f"  Wake word: \"{wake}\"\n", style="yellow")
    elif mode == "ptt":
        text.append("  Push-to-Talk: segure F12 para falar\n", style="yellow")
    if remote_enabled:
        text.append(f"  Remoto: http://IP:{remote_port}\n", style="green")
    text.append("  Ctrl+C para sair", style="dim")

    console.print(Panel(text, border_style="bright_magenta", padding=(0, 2)))


def main():
    parser = argparse.ArgumentParser(description="VoxControl -- voice control for Windows")
    parser.add_argument("--ptt", action="store_true", help="Modo Push-to-Talk (F12)")
    parser.add_argument("--text", action="store_true", help="Modo texto (sem microfone)")
    parser.add_argument("--no-remote", action="store_true", help="Desabilita servidor remoto")
    parser.add_argument("--no-voice", action="store_true", help="Desabilita resposta por voz")
    parser.add_argument("--setup", action="store_true", help="Apenas verifica a instalação")
    args = parser.parse_args()

    config = load_config()
    setup_logging(config)
    logger = logging.getLogger(__name__)

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
    engine = VoiceEngine(config)
    console.print("[yellow]Carregando modelos...[/yellow]")
    engine.setup()
    console.print("[green]Pronto![/green]\n")

    # Servidor remoto
    if not args.no_remote and config.get("remote", {}).get("enabled", True):
        from src.remote.server import start_server
        start_server(config.get("remote", {}), engine)

    # Sinal de saída limpa
    def handle_exit(sig, frame):
        console.print("\n[yellow]Encerrando...[/yellow]")
        sys.exit(0)
    signal.signal(signal.SIGINT, handle_exit)

    # ---- Modo texto ----
    if args.text:
        console.print("[cyan]Modo texto. Digite um comando (ou 'sair' para encerrar):[/cyan]")
        while True:
            try:
                cmd = input(">>> ").strip()
                if cmd.lower() in ("sair", "exit", "quit"):
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
        console.print("[cyan]Segure F12 para falar. Ctrl+C para sair.[/cyan]")
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        return

    # ---- Modo Wake Word (padrão) ----
    from src.audio.listener import AudioListener

    def on_command(audio):
        result = engine.process_audio(audio)
        if result:
            console.print(f"[green]-> {result}[/green]")

    listener = AudioListener(config, on_command)
    listener.set_wake_transcriber(engine.transcriber)
    listener.start()

    wake = config.get("wake_word", {}).get("word", "computador")
    console.print(f"[cyan]Diga [bold]'{wake}'[/bold] para ativar. Ctrl+C para sair.[/cyan]")

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()


def _run_setup_check():
    """Verifica se todos os requisitos estão instalados."""
    console.print("[bold cyan]Verificando instalação...[/bold cyan]\n")
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
        ("vosk", "vosk (opcional)"),
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
    for key, desc in [("ANTHROPIC_API_KEY", "Chave Claude"), ("OPENAI_API_KEY", "Chave OpenAI")]:
        val = os.getenv(key)
        if val:
            console.print(f"  [green]OK[/green]  {desc} encontrada")
        else:
            console.print(f"  [yellow]--[/yellow]  {desc} nao configurada (opcional mas recomendada)")

    console.print()
    if all_ok:
        console.print("[bold green]Tudo pronto! Execute: python -m src.main[/bold green]")
    else:
        console.print("[yellow]Execute: pip install -r requirements.txt[/yellow]")


if __name__ == "__main__":
    main()
