# Arquitetura e Desenvolvimento

Documentacao tecnica da arquitetura do VoxControl para desenvolvedores e contribuidores.

---

## Visao geral

O sistema segue uma arquitetura em pipeline:

```
[Input]  ->  [STT]  ->  [Intent]  ->  [Dispatch]  ->  [Action]  ->  [Output]
 Audio      Whisper     Claude/AI     Dispatcher     Handlers      TTS
 Texto      (skip)      ou Offline     por prefixo    pyautogui    pyttsx3
```

Cada etapa e um modulo independente que pode ser substituido ou estendido.

---

## Diagrama de modulos

```
src/
|
|-- main.py                    # CLI, argparse, inicializacao
|
|-- core/
|   |-- engine.py              # VoiceEngine: orquestra todo o pipeline
|
|-- audio/
|   |-- listener.py            # AudioListener: wake word + captura
|   |                          # PushToTalkListener: modo F12
|   |-- transcriber.py         # Transcriber: Whisper ou Vosk
|
|-- ai/
|   |-- intent_parser.py       # IntentParser: Claude, OpenAI, offline
|   |-- prompts.py             # SYSTEM_PROMPT com 80+ acoes
|
|-- actions/
|   |-- dispatcher.py          # ActionDispatcher: roteamento
|   |-- system_control.py      # SystemControl: SO Windows
|   |-- browser_control.py     # BrowserControl: Chrome/Edge/Firefox
|   |-- whatsapp_control.py    # WhatsAppControl: WhatsApp Web
|   |-- office_control.py      # OfficeControl: Word/Excel/PPT
|   |-- file_control.py        # FileControl: Explorador, pastas
|   |-- media_control.py       # MediaControl: Spotify, YouTube
|   |-- keyboard_control.py    # KeyboardControl: teclado, mouse
|
|-- voice/
|   |-- speaker.py             # Speaker: TTS pyttsx3
|
|-- remote/
    |-- server.py              # FastAPI + WebSocket
    |-- static/index.html      # Interface mobile
```

---

## Fluxo de dados detalhado

### 1. Captura de audio (listener.py)

```
Microfone (sounddevice)
    |
    v
AudioListener._audio_callback()     # Coleta chunks de audio
    |
    v
AudioListener._listen_loop()        # Loop principal em thread
    |
    |-- Modo wake word:
    |   |-- Acumula buffer de 2 segundos
    |   |-- Verifica energia do audio (min_speech_energy)
    |   |-- Transcreve janela com Whisper para detectar wake word
    |   |-- Se detectada: muda para modo captura
    |
    |-- Modo captura:
    |   |-- Grava audio ate silencio (silence_timeout) ou timeout
    |   |-- Envia numpy array para callback on_command()
    |
    v
engine.process_audio(audio_data)    # Processamento pelo engine
```

### 2. Transcricao (transcriber.py)

```
numpy array (float32, 16kHz)
    |
    v
Transcriber.transcribe()
    |
    |-- faster-whisper:
    |   |-- WhisperModel.transcribe()
    |   |-- VAD filter integrado
    |   |-- beam_size para qualidade
    |   |-- Retorna texto em portugues
    |
    |-- vosk:
    |   |-- KaldiRecognizer.AcceptWaveform()
    |   |-- JSON result
    |   |-- Retorna texto
    |
    v
texto: str (ex: "abrir calculadora")
```

### 3. Interpretacao de intencao (intent_parser.py)

```
texto em portugues
    |
    v
IntentParser.parse()
    |
    |-- Tenta backend primario (Claude):
    |   |-- Envia texto + SYSTEM_PROMPT para API
    |   |-- Recebe JSON estruturado
    |   |-- Valida campos obrigatorios
    |
    |-- Se falhar, tenta fallback (OpenAI):
    |   |-- Mesmo processo com API diferente
    |
    |-- Se ambos falharem, usa offline:
    |   |-- _offline_parse(): regex/contains matching
    |   |-- ~40 regras pre-definidas
    |
    v
{
  "action": "system.open_app",
  "params": {"app": "calc"},
  "confidence": 0.95,
  "response_text": "Abrindo a calculadora.",
  "requires_confirmation": false
}
```

### 4. Despacho (dispatcher.py)

```
intent dict
    |
    v
ActionDispatcher.dispatch()
    |
    |-- Extrai prefixo: "system" de "system.open_app"
    |
    |-- Roteia para handler:
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
resultado: str (ex: "Calculadora aberta.")
```

### 5. Execucao da acao (handlers)

Cada handler usa uma combinacao de:
- **pyautogui**: atalhos de teclado, mouse, screenshots
- **pywinauto**: foco em janelas, controle de apps
- **subprocess**: abrir programas, comandos do sistema
- **win32com**: API COM para Office (mais confiavel)
- **webbrowser**: abrir URLs
- **os.startfile**: abrir arquivos e URIs do Windows

### 6. Resposta por voz (speaker.py)

```
texto de resposta
    |
    v
Speaker.say()
    |
    |-- Thread separada (nao bloqueia)
    |-- pyttsx3 engine
    |-- Voz PT selecionada automaticamente
    |
    v
Audio no alto-falante
```

---

## Classes principais

### VoiceEngine (core/engine.py)

Orquestrador central. Conecta todos os modulos.

```python
class VoiceEngine:
    def setup()              # Inicializa todos os modulos
    def process_audio(data)  # Pipeline completo: STT -> AI -> acao -> TTS
    def process_text(text)   # Pula STT, direto para AI -> acao -> TTS
```

Propriedades:
- `transcriber`: instancia do Transcriber
- `speaker`: instancia do Speaker

### IntentParser (ai/intent_parser.py)

Interpreta linguagem natural em acoes estruturadas.

```python
class IntentParser:
    def parse(text) -> dict          # Retorna intencao com acao, params, confianca
    def check_confirmation() -> bool # Verifica se usuario confirmou acao arriscada
```

Backends:
- `_parse_claude()`: Anthropic Messages API
- `_parse_openai()`: OpenAI Chat Completions API
- `_offline_parse()`: Regex/contains matching

### ActionDispatcher (actions/dispatcher.py)

Roteia intencoes para handlers especializados.

```python
class ActionDispatcher:
    def dispatch(intent) -> str      # Executa acao e retorna texto de resposta
    def get_available_actions() -> list  # Lista todas as acoes suportadas
```

---

## Como adicionar um novo handler

### Exemplo: Adicionar controle do Telegram

1. Crie `src/actions/telegram_control.py`:

```python
import logging
import webbrowser

logger = logging.getLogger(__name__)

class TelegramControl:
    def execute(self, action: str, params: dict) -> str:
        sub = action.replace("telegram.", "")
        method = getattr(self, f"_{sub}", None)
        if method is None:
            return f"Acao Telegram desconhecida: {action}"
        return method(params)

    def _open(self, params: dict) -> str:
        webbrowser.open("https://web.telegram.org")
        return "Telegram Web aberto."

    def _send_message(self, params: dict) -> str:
        contact = params.get("contact", "")
        message = params.get("message", "")
        # ... implementacao
        return f"Mensagem enviada para {contact}."
```

2. Registre no `dispatcher.py`:

```python
from .telegram_control import TelegramControl

class ActionDispatcher:
    def __init__(self, config):
        # ... handlers existentes
        self._telegram = TelegramControl()

    def _route(self, action, params):
        routes = {
            # ... rotas existentes
            "telegram": self._telegram.execute,
        }
```

3. Adicione as acoes no `prompts.py`:

```python
SYSTEM_PROMPT = """
...
### Telegram
- telegram.open -- params: {}
- telegram.send_message -- params: {contact: string, message: string}
...
"""
```

4. (Opcional) Adicione regras offline no `intent_parser.py`:

```python
def _offline_parse(self, text):
    rules = [
        # ... regras existentes
        (["abrir telegram"], "telegram.open", {}, "Abrindo o Telegram."),
    ]
```

---

## Como adicionar um novo comando offline

Edite `_offline_parse()` em `src/ai/intent_parser.py`:

```python
rules = [
    # ... regras existentes
    (["minha frase", "frase alternativa"], "action.name", {"param": "value"}, "Resposta."),
]
```

Formato:
- Lista de triggers (strings que devem estar contidas no texto)
- Action name (categoria.acao)
- Parametros dict
- Texto de resposta

---

## Stack tecnologico

| Camada | Tecnologia | Funcao |
|--------|-----------|--------|
| STT | faster-whisper (CTranslate2) | Transcricao offline, otimizada |
| STT alt. | Vosk (Kaldi) | Alternativa leve |
| IA | Anthropic Claude API | Interpretacao de linguagem natural |
| IA alt. | OpenAI API | Fallback |
| Automacao | pyautogui | Mouse, teclado, screenshots |
| Windows | pywinauto | Controle de janelas |
| Office | win32com (pywin32) | API COM do Office |
| TTS | pyttsx3 (SAPI5) | Sintese de voz em PT |
| Servidor | FastAPI + uvicorn | API REST + WebSocket |
| Frontend | HTML/CSS/JS vanilla | Interface mobile responsiva |
| Config | PyYAML + python-dotenv | Arquivos YAML + .env |
| CLI | argparse + Rich | Interface de terminal formatada |

---

## Seguranca

- **Chaves de API**: armazenadas em `.env`, excluido do Git via `.gitignore`
- **Sem telemetria**: nenhum dado enviado exceto para APIs de IA quando configuradas
- **Rede local**: servidor remoto aceita conexoes apenas na rede Wi-Fi local
- **Offline-first**: funciona completamente sem internet (apos download do modelo)
- **Confirmacao de acoes**: acoes perigosas (shutdown, delete) requerem confirmacao por voz

---

## Roadmap

### v1.1
- [ ] Integracao com Telegram Bot (alternativa ao WebSocket)
- [ ] Tray icon (bandeja do sistema) com menu
- [ ] Historico de comandos persistente

### v1.2
- [ ] Plugin system para extensoes da comunidade
- [ ] Suporte a macros (sequencia de comandos)
- [ ] Perfis de configuracao (trabalho, casa, jogo)

### v2.0
- [ ] Interface grafica completa (Electron ou Tauri)
- [ ] Suporte a multiplos idiomas (ES, EN, FR)
- [ ] Empacotamento como .exe via PyInstaller
- [ ] Streaming de audio do celular (sem Web Speech API)

---

## Testes

### Teste rapido

```bash
# Modo texto (sem microfone, sem voz)
python -m src.main --text --no-voice --no-remote

>>> abrir calculadora
-> Calc aberto.
>>> pesquisar clima
-> Pesquisando 'clima' no Google.
>>> copiar
-> Copiado.
>>> sair
```

### Verificar modulos

```bash
python -m src.main --setup
```

### Testar API remotamente

```bash
# Em outro terminal ou maquina na mesma rede
curl -X POST http://IP:8765/command -H "Content-Type: application/json" -d "{\"text\": \"abrir calculadora\"}"
```

---

## Contribuindo

1. Fork o repositorio
2. Crie uma branch: `git checkout -b minha-feature`
3. Faca alteracoes
4. Teste com `python -m src.main --text`
5. Envie um PR

### Areas prioritarias

- Mais handlers de acoes (Outlook, Teams, VS Code, Telegram)
- Testes automatizados (pytest)
- Melhorias no parser offline (mais regras em PT)
- Documentacao em ingles
- Empacotamento como executavel
