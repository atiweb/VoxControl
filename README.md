# VoxControl

**Open source voice control for Windows. Supports Portuguese, Spanish, and English.**

Offline-first | AI-powered (Claude / OpenAI) | Mobile remote control | 80+ actions | 3 languages

---

## What is VoxControl?

VoxControl lets you control your Windows PC entirely by voice. It supports **Portuguese**, **Spanish**, and **English**, with an architecture designed for easy expansion to additional languages.

It uses offline speech-to-text via Whisper and optionally interprets natural language through AI APIs (Claude or OpenAI) for advanced comprehension. It also works as a wireless remote: your smartphone on the same Wi-Fi network can send voice or text commands to the PC.

### Why does this project exist?

There was no complete, ready-to-use open source solution for voice control of Windows in Portuguese. The individual components existed (Whisper, pyautogui, AI APIs), but nobody had integrated them into a functional, extensible system. VoxControl fills that gap and now supports Spanish and English as well.

---

## Supported Languages

| Language | Code | Wake Word | Offline Rules | AI (Claude/OpenAI) |
|----------|------|-----------|---------------|---------------------|
| **Portugues** (BR/PT) | `pt-BR`, `pt` | "computador" | ~35 commands | Full NLP |
| **Espanol** (ES/MX) | `es-ES`, `es` | "computadora" | ~35 commands | Full NLP |
| **English** (US/GB) | `en-US`, `en` | "computer" | ~35 commands | Full NLP |

Switch language via CLI, `.env`, or `settings.yaml`:
```bash
python -m src.main --lang es       # Spanish
python -m src.main --lang en       # English
python -m src.main --lang pt       # Portuguese (default)
```

---

## Features

| Category | Actions | Command examples |
|----------|---------|------------------|
| **System** | Open/close apps, volume, brightness, screenshots, lock, shutdown | "open calculator", "take screenshot", "volume up" |
| **Browser** | Chrome, Edge, Firefox: tabs, search, scroll, zoom, bookmarks | "search Google for today's news", "new tab", "close tab" |
| **WhatsApp** | Open chats, send messages, search, attachments, audio | "send message to John: hello!", "open chat with Maria" |
| **Word** | Formatting, tables, spell check, print, find/replace | "bold", "insert table 3 by 4", "spell check" |
| **Excel** | Cells, formulas, charts, filters, pivot tables | "auto sum", "go to cell B5", "create bar chart" |
| **PowerPoint** | Slides, slideshow, images, themes | "new slide", "start slideshow", "previous slide" |
| **Files** | Explorer, folders, rename, search, compress | "open downloads", "create folder projects", "search report" |
| **Media** | Play/pause, Spotify, YouTube, tracks | "pause music", "next track", "open Spotify with jazz" |
| **Keyboard/Mouse** | Type, shortcuts, clicks, scroll | "copy", "paste", "undo", "type hello world" |
| **Mobile** | Remote control via Wi-Fi, web interface with microphone | All commands above, from your phone |

---

## Quick Install

### Requirements

- Windows 10 or 11
- Python 3.10 or higher
- Microphone (built-in or external)
- Internet connection for first download of Whisper model (~500MB for `small`)
- (Optional) Microsoft Office for advanced control via COM API
- (Optional) Claude or OpenAI API key for natural language comprehension

### Step by step

```bash
# 1. Clone the repository
git clone https://github.com/atiweb/VoxControl.git
cd VoxControl

# 2. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure (optional, for advanced AI)
copy .env.example .env
# Edit .env: set APP_LANGUAGE and add ANTHROPIC_API_KEY or OPENAI_API_KEY

# 5. Verify installation
python -m src.main --setup

# 6. Run
python -m src.main
```

> Complete guide at [docs/instalacao.md](docs/instalacao.md)

---

## Usage Modes

| Mode | Command | Description |
|------|---------|-------------|
| **Wake Word** | `python -m src.main` | Say "computador" / "computadora" / "computer" to activate |
| **Push-to-Talk** | `python -m src.main --ptt` | Hold F12 while speaking |
| **Text** | `python -m src.main --text` | Type commands (for testing) |
| **Setup** | `python -m src.main --setup` | Verify installation |

### Flags

| Flag | Effect |
|------|--------|
| `--lang XX` | Set language: `pt`, `es`, `en` (overrides config) |
| `--no-remote` | Disable mobile server |
| `--no-voice` | Disable voice responses (TTS) |

---

## Mobile Remote Control

On startup, the system displays a **QR Code** in the terminal with the access URL:

```
  REMOTE CONTROL AVAILABLE
  Connect from your phone: http://192.168.1.100:8765
```

1. PC and phone on the **same Wi-Fi network**
2. Open the link in your phone's browser (or scan the QR code)
3. Hold the microphone button to speak, or type in the text field

The mobile interface adapts its language automatically based on the server's configured language — quick buttons, status messages, and speech recognition all match.

> Details at [docs/controle-remoto.md](docs/controle-remoto.md)

---

## AI Backends

The system has 3 levels of command interpretation:

| Backend | Accuracy | Cost | Requirements |
|---------|----------|------|-------------|
| **Claude** (recommended) | Excellent | ~$0.001/command | ANTHROPIC_API_KEY |
| **OpenAI** | Very good | ~$0.001/command | OPENAI_API_KEY |
| **Offline** | Basic (~35 rules/lang) | Free | None |

**With AI** (Claude/OpenAI): understands full natural language in pt/es/en. Example: "send a message to John on WhatsApp saying I'll be late" works directly.

**Without AI** (offline): recognizes direct commands like "open chrome", "copy", "new tab". Works without internet after the Whisper model is downloaded.

Fallback is automatic: if Claude fails, tries OpenAI; if both fail, uses offline.

---

## Whisper Models (STT)

| Model | RAM | Speed | Accuracy | When to use |
|-------|-----|-------|----------|-------------|
| `tiny` | ~1GB | Very fast | Good | Slow hardware, quick test |
| `base` | ~1GB | Fast | Good+ | Light usage |
| **`small`** | ~2GB | Fast | **Very good** | **Recommended for most** |
| `medium` | ~5GB | Medium | Excellent | Good hardware, max accuracy |
| `large-v3` | ~10GB | Slow | Excellent+ | Dedicated GPU, max quality |

Configure in `config/settings.yaml` or `.env`:
```yaml
stt:
  whisper:
    model_size: "small"
```

---

## Command Examples

### Portuguese (with AI)
```
"Pesquisa no YouTube tutoriais de Python"
"Manda mensagem no WhatsApp para a Ana dizendo que vou me atrasar"
"Abre o Excel e cria uma nova planilha"
"Faz um print da tela e salva na area de trabalho"
```

### Spanish (with AI)
```
"Busca en YouTube tutoriales de Python"
"Abre Chrome y busca noticias de hoy"
"Captura de pantalla del escritorio"
"Subir volumen al maximo"
```

### English (with AI)
```
"Search YouTube for Python tutorials"
"Open Chrome and search for today's news"
"Take a screenshot of the desktop"
"Volume up to maximum"
```

### Offline commands (all languages)
```
PT: "abrir chrome", "copiar", "nova aba", "aumentar volume"
ES: "abrir chrome", "copiar", "nueva pestana", "subir volumen"
EN: "open chrome", "copy", "new tab", "volume up"
```

> Full reference: [docs/comandos.md](docs/comandos.md)

---

## Custom Commands

Add your own voice shortcuts in `config/custom_commands.yaml`:

```yaml
custom_commands:
  - trigger: "open my email"
    action: "browser.open_url"
    params:
      url: "https://mail.google.com"

  - trigger: "focus mode"
    action: "system.do_not_disturb"
    params:
      enabled: true
```

---

## Project Structure

```
VoxControl/
|-- config/
|   |-- settings.yaml          # general settings
|   |-- custom_commands.yaml   # custom voice shortcuts
|-- docs/                      # full documentation
|   |-- instalacao.md
|   |-- configuracao.md
|   |-- comandos.md
|   |-- controle-remoto.md
|   |-- arquitetura.md
|-- src/
|   |-- main.py                # CLI entry point
|   |-- i18n.py                # internationalization (pt/es/en)
|   |-- core/engine.py         # main orchestrator
|   |-- audio/
|   |   |-- listener.py        # mic capture + wake word
|   |   |-- transcriber.py     # STT (Whisper / Vosk)
|   |-- ai/
|   |   |-- intent_parser.py   # Claude / OpenAI / offline
|   |   |-- prompts.py         # multi-language system prompt, 80+ actions
|   |-- actions/
|   |   |-- dispatcher.py      # action router
|   |   |-- system_control.py  # Windows (apps, volume, screen)
|   |   |-- browser_control.py # Chrome / Edge / Firefox
|   |   |-- whatsapp_control.py# WhatsApp Web
|   |   |-- office_control.py  # Word / Excel / PowerPoint
|   |   |-- file_control.py    # files and folders
|   |   |-- media_control.py   # Spotify / YouTube / player
|   |   |-- keyboard_control.py# keyboard and mouse
|   |-- voice/speaker.py       # TTS with auto language voice selection
|   |-- remote/
|       |-- server.py          # FastAPI + WebSocket
|       |-- static/index.html  # mobile interface (multi-language)
|-- models/                    # Vosk models (optional)
|-- logs/                      # application logs
|-- requirements.txt
|-- .env.example
|-- .gitignore
```

---

## Code Statistics

| Metric | Value |
|--------|-------|
| Python files | 24 |
| Lines of code | ~3,800 |
| Supported actions | 80+ |
| Offline rules | ~35 per language |
| Languages | 3 (pt, es, en) |
| Dependencies | 40+ packages |

---

## Full Documentation

| Document | Content |
|----------|---------|
| [docs/instalacao.md](docs/instalacao.md) | Installation guide, requirements, troubleshooting |
| [docs/configuracao.md](docs/configuracao.md) | All settings.yaml and .env options |
| [docs/comandos.md](docs/comandos.md) | Reference for all 80+ actions with parameters |
| [docs/controle-remoto.md](docs/controle-remoto.md) | Mobile setup, HTTPS, WebSocket API |
| [docs/arquitetura.md](docs/arquitetura.md) | System architecture, how to contribute, roadmap |

---

## Contributing

PRs are welcome! Priority areas:

- More command handlers for specific apps (Outlook, Teams, VS Code, Telegram)
- Telegram bot integration (alternative to web server for mobile)
- Automated tests (pytest)
- Packaging as `.exe` via PyInstaller
- GUI (tray icon)
- Plugin system for community extensions
- Additional languages (French, German, Italian, etc.)

### How to contribute

1. Fork the repository
2. Create a branch: `git checkout -b my-feature`
3. Make your changes
4. Test with `python -m src.main --text --lang en`
5. Submit a PR

---

## License

MIT -- use freely, including in commercial projects.

---

*Built for the global community. If this project was useful, leave a star on GitHub!*
