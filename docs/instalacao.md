# Installation Guide

Complete guide to install and configure VoxControl on Windows.

---

## System Requirements

### Required

| Requirement | Details |
|-------------|---------|
| **Operating System** | Windows 10 or 11 (64-bit) |
| **Python** | 3.10 or higher |
| **RAM** | Minimum 4GB (8GB recommended for `small` model) |
| **Microphone** | Any USB or built-in microphone |
| **Disk space** | ~1GB for dependencies + ~500MB for Whisper `small` model |

### Optional

| Requirement | Purpose |
|-------------|---------|
| Microsoft Office | Advanced control via COM API (Word, Excel, PowerPoint) |
| NVIDIA GPU (CUDA) | Whisper acceleration (faster transcription) |
| Claude API key | Advanced natural language comprehension |
| OpenAI API key | Alternative to Claude |
| OpenSSL | Generate HTTPS certificate for phone microphone |

---

## Step-by-step Installation

### 1. Install Python

If you don't have Python installed:

1. Download from https://www.python.org/downloads/
2. **IMPORTANT**: check "Add Python to PATH" during installation
3. Verify: `python --version` (should show 3.10+)

### 2. Clone the repository

```bash
git clone https://github.com/atiweb/VoxControl.git
cd VoxControl
```

Or download the ZIP from GitHub and extract it.

### 3. Create virtual environment (recommended)

```bash
python -m venv .venv
.venv\Scripts\activate
```

You'll know it's active when you see `(.venv)` at the beginning of the command line.

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

This installs ~40 packages. Wait 2-3 minutes.

### 5. Configure environment variables

```bash
copy .env.example .env
```

Open the `.env` file in a text editor and configure:

```env
# Set your language (pt-BR, es-ES, en-US, or short: pt, es, en)
APP_LANGUAGE=pt-BR

# At least one API key is recommended (not required)
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Or use without API
AI_BACKEND=offline
```

### 6. Verify installation

```bash
python -m src.main --setup
```

Expected output:
```
Checking installation...
  OK  faster-whisper
  OK  sounddevice
  OK  pyautogui
  OK  pywinauto
  OK  pyttsx3
  OK  fastapi
  OK  uvicorn
  OK  anthropic (Claude API)
  OK  openai (OpenAI API)
  OK  pyyaml
  OK  python-dotenv
  OK  pywin32 (Office COM)
  OK  qrcode
  OK  vosk (optional)

  OK  Claude key found
  --  OpenAI key not configured (optional but recommended)

All ready! Run: python -m src.main
```

### 7. First use

```bash
# Text mode (recommended for first test)
python -m src.main --text --no-voice

# Type commands to test:
>>> open calculator
-> Opening calculator.
>>> search weather today
-> Searching for weather today.
>>> exit
```

For a specific language:
```bash
# Portuguese
python -m src.main --text --no-voice --lang pt
>>> abrir calculadora
>>> pesquisar tempo em sao paulo
>>> sair

# Spanish
python -m src.main --text --no-voice --lang es
>>> abrir calculadora
>>> buscar clima hoy
>>> salir

# English
python -m src.main --text --no-voice --lang en
>>> open calculator
>>> search weather today
>>> exit
```

### 8. Microphone usage

```bash
# Wake word mode (default)
python -m src.main
# Say "computador" (PT), "computadora" (ES), or "computer" (EN) to activate

# Push-to-Talk (hold F12)
python -m src.main --ptt

# With a specific language
python -m src.main --lang es
python -m src.main --ptt --lang en
```

On first use with microphone, the Whisper `small` model (~500MB) will be automatically downloaded from Hugging Face. This happens only once.

---

## Language Configuration

VoxControl supports 3 languages. The language setting automatically configures:

- **Whisper STT language** (speech recognition)
- **Wake word** ("computador" / "computadora" / "computer")
- **TTS voice** (selects appropriate voice for the language)
- **AI system prompt** (responses in the correct language)
- **Offline command rules** (~35 commands per language)
- **Mobile UI** (buttons, messages, speech recognition)

### Priority order

1. CLI flag: `--lang es` (highest priority)
2. Environment variable: `APP_LANGUAGE=es` in `.env`
3. Config file: `app.language: "es-ES"` in `settings.yaml`
4. Default: `pt-BR`

### Accepted language codes

| Short | Full | Description |
|-------|------|-------------|
| `pt` | `pt-BR`, `pt-PT` | Portuguese (Brazil or Portugal) |
| `es` | `es-ES`, `es-MX` | Spanish (Spain or Mexico) |
| `en` | `en-US`, `en-GB` | English (US or UK) |

---

## Getting API Keys

### Claude (Anthropic) - Recommended

1. Go to https://console.anthropic.com/
2. Create an account
3. Go to "API Keys"
4. Create a new key
5. Copy to `.env` as `ANTHROPIC_API_KEY=sk-ant-...`

The default model (`claude-haiku-4-5`) costs approximately $0.001 per command. For typical usage (100 commands/day), the cost is ~$3/month.

### OpenAI

1. Go to https://platform.openai.com/
2. Create an account
3. Go to "API Keys"
4. Create a new key
5. Copy to `.env` as `OPENAI_API_KEY=sk-...`

The default model (`gpt-4o-mini`) has similar cost to Claude.

### Offline mode (no API)

If you don't want to use paid APIs:
```env
AI_BACKEND=offline
```

Offline mode recognizes ~35 direct commands per language. Works well for common actions like "open chrome", "copy", "save", but doesn't understand complex natural language.

---

## GPU Configuration (optional)

If you have an NVIDIA GPU, Whisper can use CUDA for faster transcription:

1. Install CUDA Toolkit: https://developer.nvidia.com/cuda-downloads
2. Install cuDNN
3. In `config/settings.yaml`:
```yaml
stt:
  whisper:
    device: "cuda"
    compute_type: "float16"
```

Without a GPU, Whisper works fine on CPU (slightly slower but perfectly functional).

---

## Troubleshooting

### "No module named 'sounddevice'"
```bash
pip install sounddevice
```

### "webrtcvad requires Visual C++ Build Tools"
webrtcvad is optional and is commented out in requirements.txt. Whisper already has built-in VAD.

### Microphone not detected
1. Check Windows settings to ensure the microphone is enabled
2. Test: `python -c "import sounddevice; print(sounddevice.query_devices())"`
3. If you have multiple microphones, configure in `settings.yaml`:
```yaml
audio:
  input_device: 1  # device number
```

### Whisper takes too long to load
On first run, the model is downloaded (~500MB for `small`). Subsequent runs are fast (3-5 seconds). If you want a smaller model:
```yaml
stt:
  whisper:
    model_size: "base"  # ~150MB, faster
```

### "UnicodeEncodeError" in terminal
The Windows terminal may not support special characters. Run with:
```bash
set PYTHONIOENCODING=utf-8
python -m src.main
```

### APIs return errors
- Verify the API key is correct in `.env`
- Check you have credits in your account
- The system will automatically fallback to offline parser

### Office doesn't respond to commands
- Verify Microsoft Office is installed
- COM API control requires the app to be open
- Alternative: keyboard shortcuts work even without COM API

### No voice found for my language
Windows may not have TTS voices installed for all languages. To check available voices:
```python
import pyttsx3
engine = pyttsx3.init()
for v in engine.getProperty('voices'):
    print(v.id, v.name)
```
For Spanish/English voices, you may need to install them via Windows Settings > Time & Language > Speech.

---

## Update

```bash
cd VoxControl
git pull
pip install -r requirements.txt --upgrade
```

---

## Uninstall

```bash
# Remove the virtual environment
rmdir /s /q .venv

# Remove the project directory
cd ..
rmdir /s /q VoxControl
```

Whisper models are stored in `%USERPROFILE%\.cache\huggingface\` and can be manually removed if desired.
