# Configuration Guide

Reference for all configurable options in VoxControl.

The system uses two configuration sources:
- **`config/settings.yaml`** -- general settings (versioned in Git)
- **`.env`** -- API keys and sensitive overrides (not versioned)

Values from `.env` take priority over `settings.yaml`.

### Configuration File Locations

| Mode | Config Path |
|------|------------|
| From source (Python) | `<project>/config/settings.yaml` |
| Installed (.exe) | `%APPDATA%\VoxControl\config\settings.yaml` |

When running the installed .exe for the first time, default config files are automatically copied to `%APPDATA%\VoxControl\config\`. You can edit them freely -- they are never overwritten by updates.

### GUI Settings Panel

If using the desktop GUI, most settings can be changed visually via the **Settings** tab:
- Language, Whisper model, AI backend, voice, wake word, remote server
- API key fields (Anthropic, OpenAI) with environment variable integration
- Whisper model download button (downloads the configured model size on demand)

Changes are saved to `settings.yaml` automatically.

---

## Environment Variables (.env)

```env
# =====================================================
# LANGUAGE
# =====================================================

APP_LANGUAGE=pt-BR                  # pt-BR | pt-PT | es-ES | es-MX | en-US | en-GB
                                    # Short codes also accepted: pt | es | en

# =====================================================
# API KEYS (at least one recommended)
# =====================================================

ANTHROPIC_API_KEY=sk-ant-...        # Claude (primary)
OPENAI_API_KEY=sk-...               # OpenAI (fallback)

# =====================================================
# AI BACKEND
# =====================================================

AI_BACKEND=claude                   # claude | openai | offline
CLAUDE_MODEL=claude-haiku-4-5-20251001   # Claude model
OPENAI_MODEL=gpt-4o-mini           # OpenAI model

# =====================================================
# WHISPER (STT)
# =====================================================

WHISPER_MODEL=small                 # tiny | base | small | medium | large-v3
# WHISPER_LANGUAGE=pt               # Auto-set from APP_LANGUAGE. Override only if needed.

# =====================================================
# WAKE WORD
# =====================================================

# WAKE_WORD=computador              # Auto-set from APP_LANGUAGE:
                                    #   pt -> computador
                                    #   es -> computadora
                                    #   en -> computer
                                    # Override only for custom wake word.
LISTEN_TIMEOUT=5                    # seconds of listening after activation

# =====================================================
# BEHAVIOR
# =====================================================

VOICE_RESPONSE=true                 # true | false
LOG_LEVEL=INFO                      # DEBUG | INFO | WARNING | ERROR

# =====================================================
# REMOTE SERVER
# =====================================================

REMOTE_SERVER_HOST=0.0.0.0          # listen address
REMOTE_SERVER_PORT=8765             # server port
SSL_CERTFILE=                       # path to HTTPS certificate
SSL_KEYFILE=                        # path to HTTPS private key
```

---

## settings.yaml -- Complete Reference

### Section `app`

```yaml
app:
  name: "VoxControl"
  version: "1.1.0"
  # Language: pt-BR | pt-PT | es-ES | es-MX | en-US | en-GB
  # Also accepts short codes: pt | es | en
  language: "pt-BR"
```

**Language auto-configuration:** When you set `app.language`, the following are automatically configured (unless manually overridden):

| Setting | pt | es | en |
|---------|----|----|-----|
| Whisper language | pt | es | en |
| Wake word | computador | computadora | computer |
| TTS voice | Portuguese | Spanish | English |
| AI responses | Portuguese | Spanish | English |
| Offline rules | ~35 PT commands | ~35 ES commands | ~35 EN commands |
| Mobile UI | Portuguese | Spanish | English |

### Section `audio`

Microphone capture settings.

```yaml
audio:
  sample_rate: 16000          # sample rate (Hz), 16000 is Whisper's default
  channels: 1                 # channels (1 = mono, required for Whisper)
  chunk_duration_ms: 30       # duration of each audio chunk in ms
  input_device: null          # null = system default device
                              # use an integer to select another mic
  silence_timeout: 1.5        # seconds of silence to end capture
  min_speech_energy: 0.01     # minimum energy to consider as speech (0.0 - 1.0)
```

**How to find the device number:**
```python
import sounddevice
print(sounddevice.query_devices())
```

### Section `stt` (Speech-to-Text)

```yaml
stt:
  engine: "faster-whisper"    # "faster-whisper" or "vosk"

  whisper:
    model_size: "small"       # tiny | base | small | medium | large-v3
    language: "pt"            # Auto-set from app.language. Override only if needed.
    device: "auto"            # auto | cpu | cuda
    compute_type: "int8"      # int8 (fast/light) | float16 (GPU) | float32 (precise)
    beam_size: 5              # transcription quality (1-10, higher = better/slower)
    vad_filter: true          # automatically filter silence

  vosk:
    model_path: "models/vosk-model-pt"   # path to downloaded Vosk model
```

**Whisper model comparison:**

| Model | Download | RAM | Speed (CPU) | When to use |
|-------|----------|-----|-------------|-------------|
| tiny | ~75MB | ~1GB | ~10x real time | Limited hardware |
| base | ~150MB | ~1GB | ~7x real time | Casual use |
| **small** | **~500MB** | **~2GB** | **~4x real time** | **General use (recommended)** |
| medium | ~1.5GB | ~5GB | ~2x real time | High accuracy |
| large-v3 | ~3GB | ~10GB | ~1x real time | Maximum accuracy (GPU recommended) |

### Section `wake_word`

```yaml
wake_word:
  enabled: true               # true = wait for wake word; false = always listening
  # Wake word: auto-set based on app.language
  # pt: "computador" | es: "computadora" | en: "computer"
  # Override here to use a custom wake word
  word: "computador"
  # Alternative triggers (accent variations)
  aliases:
    - "computado"
    - "ei computador"
    - "oi computador"
  sensitivity: 0.7             # sensitivity (0.0 - 1.0, higher = more sensitive)
  listen_timeout: 6            # seconds of listening after wake word
```

**Default wake words per language:**

| Language | Wake word | Aliases |
|----------|-----------|---------|
| pt | computador | computado, ei computador, oi computador |
| es | computadora | computador, oye computadora, hola computadora |
| en | computer | hey computer, hi computer, ok computer |

### Section `ai`

```yaml
ai:
  backend: "claude"            # "claude" | "openai" | "offline"
  fallback: "openai"           # alternative backend if primary fails

  claude:
    model: "claude-haiku-4-5-20251001"
    max_tokens: 512            # maximum tokens in response
    temperature: 0.1           # creativity (0.0 = deterministic, 1.0 = creative)

  openai:
    model: "gpt-4o-mini"
    max_tokens: 512
    temperature: 0.1

  min_confidence: 0.6          # minimum confidence to execute without confirmation (0.0 - 1.0)
  confirm_risky_actions: true  # request voice confirmation for dangerous actions
```

**Actions that require confirmation** (when `confirm_risky_actions: true`):
- `system.shutdown` (shutdown)
- `system.restart` (restart)
- `files.delete` (delete file)
- Any action with `requires_confirmation: true` in AI response

### Section `voice_response`

```yaml
voice_response:
  enabled: true                # enable TTS (text-to-speech)
  rate: 180                    # speech rate (words per minute)
  volume: 0.9                  # volume (0.0 - 1.0)
  prefer_female: true          # prefer female voice
```

The TTS engine automatically selects a voice matching the configured language (Portuguese, Spanish, or English).

To list available voices on your system:
```python
import pyttsx3
engine = pyttsx3.init()
for v in engine.getProperty('voices'):
    print(v.id, v.name)
```

### Section `browser`

```yaml
browser:
  default: "chrome"            # chrome | edge | firefox
  chrome_path: null            # null = auto-detect
  edge_path: null              # custom path if needed
  firefox_path: null
```

### Section `office`

```yaml
office:
  use_com_api: true            # true = COM API (reliable) | false = keyboard shortcuts
  confirm_before_delete: true  # confirm deletion of slides, sheets, etc.
```

### Section `remote`

```yaml
remote:
  enabled: true                # enable server for phone control
  host: "0.0.0.0"              # 0.0.0.0 = accessible on local network
  port: 8765                   # server port
  show_qr: true                # show QR code in terminal on startup
  auth_token: ""               # empty = no auth | string = required token
```

### Section `logging`

```yaml
logging:
  level: "INFO"                # DEBUG | INFO | WARNING | ERROR
  file: "logs/voxcontrol.log"
  max_bytes: 5242880           # max file size (5 MB)
  backup_count: 3              # how many backup files to keep
```

---

## Custom Commands (custom_commands.yaml)

Add your own voice shortcuts:

```yaml
custom_commands:
  # Format:
  #   trigger: "phrase you say"
  #   action: "category.action"
  #   params: { parameters }

  - trigger: "open gmail"
    action: "browser.open_url"
    params:
      url: "https://mail.google.com"

  - trigger: "focus mode"
    action: "system.do_not_disturb"
    params:
      enabled: true

  - trigger: "open my project"
    action: "files.open_folder"
    params:
      path: "C:\\Users\\MyUser\\Projects\\MyApp"
```

Available `actions` are documented in [docs/comandos.md](comandos.md).

---

## Configuration Priority

Priority order (highest to lowest):

1. CLI flags (`--lang`, `--no-voice`, `--ptt`, etc.)
2. Environment variables (`.env`)
3. `config/settings.yaml`
4. Default values in code

---

## Authentication (Remote API)

The remote server uses JWT authentication. When auth is enabled, users must log in to access the API.

### Section `auth` in settings.yaml

```yaml
auth:
  enabled: true                     # true = require login | false = open access
  credentials_file: "credentials.json"  # stored in config dir
  token_expiry_hours: 24            # JWT token lifetime
  max_attempts: 5                   # failed login attempts before lockout
  lockout_minutes: 15               # lockout duration after max_attempts
```

### Managing Users

```bash
# Create/update a user (from project root)
python -c "from src.auth.auth import AuthManager; AuthManager().create_user('admin', 'your_password')"
```

Credentials are stored with iterated SHA-256 hashing (100k rounds) in `credentials.json` inside the config directory.

### API Authentication Flow

1. `POST /auth/login` with `{"username": "admin", "password": "..."}` returns a JWT token
2. Include the token in subsequent requests: `Authorization: Bearer <token>`
3. WebSocket connections also require the token as a query parameter: `ws://IP:8765/ws?token=<token>`
