# Architecture and Development

Technical documentation of VoxControl's architecture for developers and contributors.

---

## Overview

The system follows a pipeline architecture:

```
[Input]  ->  [STT]  ->  [Intent]  ->  [Dispatch]  ->  [Action]  ->  [Output]
 Audio      Whisper     Claude/AI     Dispatcher     Handlers      TTS
 Text       (skip)      or Offline     by prefix     pyautogui    pyttsx3
```

Each stage is an independent module that can be replaced or extended.

The application can run in **two modes**:
- **CLI**: headless, controlled from terminal (`python -m src.main`)
- **Desktop GUI**: customtkinter window with status, controls, logs, and settings (`VoxControl.pyw`)

---

## Module Diagram

```
src/
|
|-- main.py                    # CLI, argparse, initialization
|-- i18n.py                    # Internationalization (PT/ES/EN)
|-- paths.py                   # Centralized path resolver (source vs .exe)
|-- validation.py              # Action whitelist + input sanitization
|
|-- core/
|   |-- engine.py              # VoiceEngine: orchestrates the full pipeline
|
|-- audio/
|   |-- listener.py            # AudioListener: wake word + capture
|   |                          # PushToTalkListener: F12 mode
|   |-- transcriber.py         # Transcriber: Whisper or Vosk
|
|-- ai/
|   |-- intent_parser.py       # IntentParser: Claude, OpenAI, offline
|   |-- prompts.py             # Multi-language system prompts with 80+ actions
|
|-- actions/
|   |-- dispatcher.py          # ActionDispatcher: routing + validation
|   |-- system_control.py      # SystemControl: Windows OS
|   |-- browser_control.py     # BrowserControl: Chrome/Edge/Firefox
|   |-- whatsapp_control.py    # WhatsAppControl: WhatsApp Web
|   |-- office_control.py      # OfficeControl: Word/Excel/PPT
|   |-- file_control.py        # FileControl: Explorer, folders
|   |-- media_control.py       # MediaControl: Spotify, YouTube
|   |-- keyboard_control.py    # KeyboardControl: keyboard, mouse
|
|-- voice/
|   |-- speaker.py             # Speaker: TTS pyttsx3
|
|-- auth/
|   |-- auth.py                # AuthManager: JWT + password hashing + rate limiting
|   |-- middleware.py           # FastAPI auth middleware
|
|-- remote/
|   |-- server.py              # FastAPI REST API + JWT auth + WebSocket
|   |-- static/index.html      # Mobile web interface
|
|-- gui/
|   |-- __main__.py            # GUI entry point
|   |-- app.py                 # VoxControlApp: main window (customtkinter)
|   |-- tray.py                # System tray icon (pystray)
|   |-- frames/
|       |-- status_frame.py    # Engine status indicators
|       |-- control_frame.py   # Start/stop/mode controls
|       |-- command_frame.py   # Command history + text input
|       |-- log_frame.py       # Real-time log viewer
|       |-- settings_frame.py  # Visual settings editor

build.py                       # Build script (PyInstaller + Inno Setup)
VoxControl.spec                # PyInstaller spec file
VoxControl.pyw                 # GUI launcher (double-click)
installer/
|-- setup.iss                  # Inno Setup installer script
|-- version_info.txt           # Windows version metadata
```

---

## i18n Module (src/i18n.py)

The internationalization module centralizes all language-specific data:

| Data | Description |
|------|-------------|
| `SUPPORTED_LANGUAGES` | `["pt", "es", "en"]` |
| `DEFAULT_WAKE_WORDS` | Wake word + aliases per language |
| `VOICE_PATTERNS` | TTS voice search patterns per language |
| `SPEECH_RECOGNITION_LANG` | Web Speech API language codes |
| `CONFIRM_WORDS` / `CANCEL_WORDS` | Confirmation/cancel words per language |
| `FOLDER_ALIASES_I18N` | Folder aliases per language (documents, downloads, etc.) |
| `SEARCH_PREFIXES` / `TYPE_PREFIXES` | Offline parser prefixes per language |
| `OFFLINE_RULES` | ~40 keyword-matching rules per language |
| `STRINGS` | All UI strings (engine, remote, dispatcher) |

Key functions:
- `set_language(lang_code)` -- Sets the active language (accepts "pt-BR", "es-ES", "en-US", etc.)
- `get_language()` -- Returns the current 2-letter language code
- `t(key, **kwargs)` -- Returns a translated string for the current language

---

## Data Flow

### 1. Audio Capture (listener.py)

```
Microphone (sounddevice)
    |
    v
AudioListener._audio_callback()     # Collects audio chunks
    |
    v
AudioListener._listen_loop()        # Main loop in thread
    |
    |-- Drains the entire audio queue each iteration
    |   (stays in sync with real-time audio)
    |
    |-- Wake word mode:
    |   |-- Accumulates 2-second sliding buffer
    |   |-- Checks audio energy (min_speech_energy)
    |   |-- Throttles: waits 1.5s between transcription attempts
    |   |-- Transcribes window with fast wake word method
    |   |   (beam_size=1, no VAD filter, ~5x faster)
    |   |-- If detected: switches to capture mode
    |
    |-- Capture mode:
    |   |-- Records audio until silence (silence_timeout) or timeout
    |   |-- Sends numpy array to on_command() callback
    |
    v
engine.process_audio(audio_data)    # Processing by engine
```

### 2. Transcription (transcriber.py)

```
numpy array (float32, 16kHz)
    |
    v
Transcriber.transcribe()            # Full transcription (commands)
    |                               # beam_size=5, VAD filter enabled
    |
Transcriber.transcribe_wake_word()  # Fast transcription (wake word only)
    |                               # beam_size=1, no VAD filter (~5x faster)
    |
    |-- faster-whisper:
    |   |-- WhisperModel.transcribe()
    |   |-- Returns text in configured language
    |
    |-- vosk:
    |   |-- KaldiRecognizer.AcceptWaveform()
    |   |-- JSON result
    |   |-- Returns text
    |
    v
text: str (e.g., "open calculator")
```

### 3. Intent Interpretation (intent_parser.py)

```
text in user's language
    |
    v
IntentParser.parse()
    |
    |-- Gets current language from i18n
    |
    |-- Tries primary backend (Claude):
    |   |-- Sends text + language-specific SYSTEM_PROMPT to API
    |   |-- Receives structured JSON
    |   |-- Validates required fields
    |
    |-- If fails, tries fallback (OpenAI):
    |   |-- Same process with different API
    |
    |-- If both fail, uses offline:
    |   |-- _offline_parse(): regex/contains matching
    |   |-- Uses OFFLINE_RULES for current language (~35 rules)
    |
    v
{
  "action": "system.open_app",
  "params": {"app": "calc"},
  "confidence": 0.95,
  "response_text": "Opening calculator.",   // in user's language
  "requires_confirmation": false
}
```

### 4. Dispatch (dispatcher.py)

```
intent dict
    |
    v
ActionDispatcher.dispatch()
    |
    |-- Extracts prefix: "system" from "system.open_app"
    |
    |-- Routes to handler:
    |   system.   -> SystemControl.execute()
    |   browser.  -> BrowserControl.execute()
    |   whatsapp. -> WhatsAppControl.execute()
    |   office.   -> OfficeControl.execute()
    |   files.    -> FileControl.execute()
    |   media.    -> MediaControl.execute()
    |   keyboard. -> KeyboardControl.execute()
    |   mouse.    -> KeyboardControl.execute()
    |
    v
result: str (internal log string)
```

### 5. Action Execution (handlers)

Each handler uses a combination of:
- **pyautogui**: keyboard shortcuts, mouse, screenshots
- **pywinauto**: window focus, app control
- **subprocess**: open programs, system commands
- **win32com**: COM API for Office (more reliable)
- **webbrowser**: open URLs
- **os.startfile**: open files and Windows URIs

### 6. Voice Response (speaker.py)

```
response_text from intent (in user's language)
    |
    v
Speaker.say()
    |
    |-- Separate thread (non-blocking)
    |-- pyttsx3 engine
    |-- Voice auto-selected based on language (VOICE_PATTERNS)
    |
    v
Audio on speaker
```

> **Note**: TTS uses `intent["response_text"]` directly. This text is already in the user's language -- generated by AI in AI mode, or from language-specific offline rules in offline mode.

---

## Key Classes

### VoiceEngine (core/engine.py)

Central orchestrator. Connects all modules.

```python
class VoiceEngine:
    def setup()              # Initializes all modules
    def process_audio(data)  # Full pipeline: STT -> AI -> action -> TTS
    def process_text(text)   # Skips STT, goes to AI -> action -> TTS
```

Properties:
- `transcriber`: Transcriber instance
- `speaker`: Speaker instance

### IntentParser (ai/intent_parser.py)

Interprets natural language into structured actions.

```python
class IntentParser:
    def parse(text) -> dict          # Returns intent with action, params, confidence
    def check_confirmation() -> bool # Checks if user confirmed risky action
```

Backends:
- `_parse_claude()`: Anthropic Messages API
- `_parse_openai()`: OpenAI Chat Completions API
- `_offline_parse()`: Language-aware keyword matching (uses `OFFLINE_RULES`)

### ActionDispatcher (actions/dispatcher.py)

Routes intents to specialized handlers.

```python
class ActionDispatcher:
    def dispatch(intent) -> str      # Executes action and returns result
    def get_available_actions() -> list  # Lists all supported actions
```

---

## Adding a New Handler

### Example: Add Telegram Control

1. Create `src/actions/telegram_control.py`:

```python
import logging
import webbrowser

logger = logging.getLogger(__name__)

class TelegramControl:
    def execute(self, action: str, params: dict) -> str:
        sub = action.replace("telegram.", "")
        method = getattr(self, f"_{sub}", None)
        if method is None:
            return f"Unknown Telegram action: {action}"
        return method(params)

    def _open(self, params: dict) -> str:
        webbrowser.open("https://web.telegram.org")
        return "Telegram Web opened."

    def _send_message(self, params: dict) -> str:
        contact = params.get("contact", "")
        message = params.get("message", "")
        # ... implementation
        return f"Message sent to {contact}."
```

2. Register in `dispatcher.py`:

```python
from .telegram_control import TelegramControl

class ActionDispatcher:
    def __init__(self, config):
        # ... existing handlers
        self._telegram = TelegramControl()

    def _route(self, action, params):
        routes = {
            # ... existing routes
            "telegram": self._telegram.execute,
        }
```

3. Add actions to `prompts.py` (in the `_ACTIONS_SECTION`):

```python
_ACTIONS_SECTION = """
...
### Telegram
- telegram.open -- params: {}
- telegram.send_message -- params: {contact: string, message: string}
...
"""
```

4. (Optional) Add offline rules to `src/i18n.py`:

```python
OFFLINE_RULES = {
    "pt": [
        # ... existing rules
        (["abrir telegram"], "telegram.open", {}, "Abrindo o Telegram."),
    ],
    "es": [
        # ... existing rules
        (["abrir telegram"], "telegram.open", {}, "Abriendo Telegram."),
    ],
    "en": [
        # ... existing rules
        (["open telegram"], "telegram.open", {}, "Opening Telegram."),
    ],
}
```

---

## Adding a New Offline Command

Edit the `OFFLINE_RULES` dict in `src/i18n.py`:

```python
OFFLINE_RULES = {
    "pt": [
        # ... existing rules
        (["minha frase", "frase alternativa"], "action.name", {"param": "value"}, "Resposta em portugues."),
    ],
    "es": [
        # ... existing rules
        (["mi frase", "frase alternativa"], "action.name", {"param": "value"}, "Respuesta en espanol."),
    ],
    "en": [
        # ... existing rules
        (["my phrase", "alternative phrase"], "action.name", {"param": "value"}, "Response in English."),
    ],
}
```

Format:
- List of triggers (strings that must be contained in the text)
- Action name (category.action)
- Parameters dict
- Response text **in the rule's language**

---

## Tech Stack

| Layer | Technology | Function |
|-------|-----------|----------|
| STT | faster-whisper (CTranslate2) | Offline transcription, optimized |
| STT alt. | Vosk (Kaldi) | Lightweight alternative |
| AI | Anthropic Claude API | Natural language interpretation |
| AI alt. | OpenAI API | Fallback |
| Automation | pyautogui | Mouse, keyboard, screenshots |
| Windows | pywinauto | Window control |
| Office | win32com (pywin32) | Office COM API |
| TTS | pyttsx3 (SAPI5) | Voice synthesis (PT/ES/EN) |
| Server | FastAPI + uvicorn | REST API + JWT auth + WebSocket |
| Auth | PyJWT + hashlib | JWT tokens + password hashing |
| Desktop GUI | customtkinter | Native Windows GUI (dark theme) |
| System tray | pystray + Pillow | Tray icon with context menu |
| Mobile app | Flutter + Dart | Native iOS/Android client |
| Frontend | HTML/CSS/JS vanilla | Responsive mobile web interface |
| Config | PyYAML + python-dotenv | YAML + .env files |
| CLI | argparse + Rich | Formatted terminal interface |
| i18n | src/i18n.py | Centralized translations (3 languages) |
| Paths | src/paths.py | Source vs .exe path resolution |
| Validation | src/validation.py | Action whitelist + input sanitization |
| Packaging | PyInstaller | Standalone .exe build |
| Installer | Inno Setup | Windows installer creation |
| Testing | pytest (180 tests) | Unit + integration test suite |

---

## Security

- **API keys**: stored in `.env`, excluded from Git via `.gitignore`
- **No telemetry**: no data sent except to AI APIs when configured
- **Local network**: remote server accepts connections only on local Wi-Fi
- **Offline-first**: works completely without internet (after model download)
- **Action confirmation**: dangerous actions (shutdown, delete) require voice confirmation
- **JWT authentication**: remote API protected with HMAC-SHA256 signed tokens (configurable expiry)
- **Password hashing**: iterated SHA-256 with random salt (100,000 rounds)
- **Rate limiting**: brute-force protection with configurable lockout (max attempts + lockout period)
- **Action validation**: whitelist-based action validation prevents execution of unknown actions
- **Input sanitization**: command parameters are sanitized before execution (path traversal, injection prevention)

---

## Roadmap

### v1.0
- [x] Multi-language support (Portuguese, Spanish, English)
- [x] Dynamic mobile UI language adaptation
- [x] Language-aware offline rules (~35 rules per language)

### v1.1 (Current)
- [x] JWT authentication + rate limiting
- [x] Action validation + input sanitization
- [x] Desktop GUI (customtkinter, dark theme)
- [x] System tray icon with context menu
- [x] Standalone .exe packaging (PyInstaller)
- [x] Windows installer (Inno Setup)
- [x] Centralized path resolver (source vs .exe)
- [x] Full test suite (180 tests, pytest)
- [x] Flutter mobile app (iOS/Android)
- [x] Settings UI: API key fields + Whisper model download
- [x] CUDA auto-fallback to CPU when GPU libraries unavailable
- [x] Duplicate middleware prevention on engine restart
- [x] Network drive build fix (.exe to local path)
- [x] Offline keyword normalization (accent-insensitive matching)
- [x] Focus-first window management with AI target detection
- [x] Tab navigation: goto specific tab, next/prev tab
- [x] WhatsApp Unicode support (clipboard-based typing)
- [x] Word: select paragraph, increase/decrease font size
- [x] Real-time wake word detection (queue draining + fast transcription)
- [ ] Telegram Bot integration (alternative to WebSocket)
- [ ] Persistent command history

### v2.0
- [ ] Plugin system for community extensions
- [ ] Macro support (command sequences)
- [ ] Configuration profiles (work, home, gaming)
- [ ] Additional languages (FR, DE, IT)
- [ ] Phone audio streaming (without Web Speech API)

---

## Testing

### Automated test suite

VoxControl has a comprehensive test suite with **180 tests** covering all modules:

```bash
# Run all tests
python -m pytest tests/ --tb=short

# Run with verbose output
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/test_dispatcher.py
```

Test files:
- `tests/test_dispatcher.py` -- ActionDispatcher routing + custom commands
- `tests/test_intent_parser.py` -- AI intent parsing (Claude, OpenAI, offline)
- `tests/test_engine.py` -- VoiceEngine pipeline orchestration
- `tests/test_i18n.py` -- Internationalization + language switching
- `tests/test_server.py` -- REST API endpoints + WebSocket + JWT auth
- `tests/test_auth.py` -- Authentication, password hashing, rate limiting
- `tests/test_validation.py` -- Action whitelist + input sanitization

### Quick manual test

```bash
# Text mode (no microphone, no voice)
python -m src.main --text --no-voice --no-remote

# English
python -m src.main --text --no-voice --no-remote --lang en
>>> open calculator
-> Calculator opened.
>>> search weather
-> Searching 'weather' on Google.
>>> copy
-> Copied.
>>> exit
```

### Verify modules

```bash
python -m src.main --setup
```

### Test API remotely

```bash
# From another terminal or machine on the same network
curl http://IP:8765/status
```

---

## Contributing

1. Fork the repository
2. Create a branch: `git checkout -b my-feature`
3. Make changes
4. Run tests: `python -m pytest tests/ --tb=short` (all 180 must pass)
5. Test manually: `python -m src.main --text`
6. Submit a PR

### Priority Areas

- More action handlers (Outlook, Teams, VS Code, Telegram)
- Improvements to offline parser (more rules)
- Additional language support (FR, DE, IT)
- Plugin system for community extensions
