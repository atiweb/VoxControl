# Guia de Configuracao

Referencia de todas as opcoes configuraveis do VoxControl.

O sistema usa duas fontes de configuracao:
- **`config/settings.yaml`** -- configuracoes gerais (versionadas no Git)
- **`.env`** -- chaves de API e overrides sensiveis (nao versionado)

Valores do `.env` tem prioridade sobre o `settings.yaml`.

---

## Variaveis de ambiente (.env)

```env
# =====================================================
# CHAVES DE API (pelo menos uma recomendada)
# =====================================================

ANTHROPIC_API_KEY=sk-ant-...        # Claude (primario)
OPENAI_API_KEY=sk-...               # OpenAI (fallback)

# =====================================================
# BACKEND DE IA
# =====================================================

AI_BACKEND=claude                   # claude | openai | offline
CLAUDE_MODEL=claude-haiku-4-5-20251001   # modelo Claude
OPENAI_MODEL=gpt-4o-mini           # modelo OpenAI

# =====================================================
# WHISPER (STT)
# =====================================================

WHISPER_MODEL=small                 # tiny | base | small | medium | large-v3
WHISPER_LANGUAGE=pt                 # codigo do idioma

# =====================================================
# WAKE WORD
# =====================================================

WAKE_WORD=computador                # palavra de ativacao
LISTEN_TIMEOUT=5                    # segundos de escuta apos ativacao

# =====================================================
# COMPORTAMENTO
# =====================================================

VOICE_RESPONSE=true                 # true | false
LOG_LEVEL=INFO                      # DEBUG | INFO | WARNING | ERROR

# =====================================================
# SERVIDOR REMOTO
# =====================================================

REMOTE_SERVER_HOST=0.0.0.0          # endereco de escuta
REMOTE_SERVER_PORT=8765             # porta do servidor
SSL_CERTFILE=                       # caminho para certificado HTTPS
SSL_KEYFILE=                        # caminho para chave privada HTTPS
```

---

## settings.yaml -- Referencia completa

### Secao `app`

```yaml
app:
  name: "VoxControl"    # nome da aplicacao
  version: "1.0.0"           # versao
  language: "pt-BR"          # pt-BR ou pt-PT
```

### Secao `audio`

Configuracoes de captura de microfone.

```yaml
audio:
  sample_rate: 16000          # taxa de amostragem (Hz), 16000 e o padrao do Whisper
  channels: 1                 # canais (1 = mono, obrigatorio para Whisper)
  chunk_duration_ms: 30       # duracao de cada chunk de audio em ms
  input_device: null          # null = dispositivo padrao do sistema
                              # use um numero inteiro para selecionar outro mic
  silence_timeout: 1.5        # segundos de silencio para finalizar captura
  min_speech_energy: 0.01     # energia minima para considerar como fala (0.0 - 1.0)
```

**Como encontrar o numero do dispositivo:**
```python
import sounddevice
print(sounddevice.query_devices())
```

### Secao `stt` (Speech-to-Text)

```yaml
stt:
  engine: "faster-whisper"    # "faster-whisper" ou "vosk"

  whisper:
    model_size: "small"       # tiny | base | small | medium | large-v3
    language: "pt"            # codigo do idioma
    device: "auto"            # auto | cpu | cuda
    compute_type: "int8"      # int8 (rapido/leve) | float16 (GPU) | float32 (preciso)
    beam_size: 5              # qualidade da transcricao (1-10, maior = melhor/mais lento)
    vad_filter: true          # filtrar silencio automaticamente

  vosk:
    model_path: "models/vosk-model-pt"   # caminho para modelo Vosk baixado
```

**Escolha de modelo Whisper:**

| Modelo | Download | RAM | Velocidade (CPU) | Quando usar |
|--------|----------|-----|-------------------|-------------|
| tiny | ~75MB | ~1GB | ~10x tempo real | Hardware limitado |
| base | ~150MB | ~1GB | ~7x tempo real | Uso casual |
| **small** | **~500MB** | **~2GB** | **~4x tempo real** | **Uso geral (recomendado)** |
| medium | ~1.5GB | ~5GB | ~2x tempo real | Precisao alta |
| large-v3 | ~3GB | ~10GB | ~1x tempo real | Maxima precisao (GPU recomendada) |

### Secao `wake_word`

```yaml
wake_word:
  enabled: true               # true = aguarda wake word; false = sempre escutando
  word: "computador"           # palavra de ativacao principal
  aliases:                     # variacoes aceitas (sotaques, informalidade)
    - "computado"
    - "ei computador"
    - "oi computador"
  sensitivity: 0.7             # sensibilidade (0.0 - 1.0, maior = mais sensivel)
  listen_timeout: 6            # segundos de escuta apos wake word
```

### Secao `ai`

```yaml
ai:
  backend: "claude"            # "claude" | "openai" | "offline"
  fallback: "openai"           # backend alternativo se o primario falhar

  claude:
    model: "claude-haiku-4-5-20251001"
    max_tokens: 512            # tokens maximos na resposta
    temperature: 0.1           # criatividade (0.0 = deterministico, 1.0 = criativo)

  openai:
    model: "gpt-4o-mini"
    max_tokens: 512
    temperature: 0.1

  min_confidence: 0.6          # confianca minima para executar sem confirmar (0.0 - 1.0)
  confirm_risky_actions: true  # pede confirmacao por voz para acoes perigosas
```

**Acoes que requerem confirmacao** (quando `confirm_risky_actions: true`):
- `system.shutdown` (desligar)
- `system.restart` (reiniciar)
- `files.delete` (excluir arquivo)
- Qualquer acao com `requires_confirmation: true` na resposta da IA

### Secao `voice_response`

```yaml
voice_response:
  enabled: true                # habilitar TTS (texto para voz)
  rate: 180                    # velocidade da fala (palavras por minuto)
  volume: 0.9                  # volume (0.0 - 1.0)
  prefer_female: true          # preferir voz feminina em portugues
```

Para listar vozes disponiveis no seu sistema:
```python
import pyttsx3
engine = pyttsx3.init()
for v in engine.getProperty('voices'):
    print(v.id, v.name)
```

### Secao `browser`

```yaml
browser:
  default: "chrome"            # chrome | edge | firefox
  chrome_path: null            # null = detectar automaticamente
  edge_path: null              # caminho personalizado se necessario
  firefox_path: null
```

### Secao `office`

```yaml
office:
  use_com_api: true            # true = API COM (confiavel) | false = atalhos de teclado
  confirm_before_delete: true  # confirma exclusao de slides, planilhas, etc.
```

### Secao `remote`

```yaml
remote:
  enabled: true                # habilitar servidor para controle pelo celular
  host: "0.0.0.0"              # 0.0.0.0 = acessivel na rede local
  port: 8765                   # porta do servidor
  show_qr: true                # exibir QR code no terminal ao iniciar
  auth_token: ""               # vazio = sem autenticacao | string = token necessario
```

### Secao `logging`

```yaml
logging:
  level: "INFO"                # DEBUG | INFO | WARNING | ERROR
  file: "logs/voz-controle.log"
  max_bytes: 5242880           # tamanho maximo do arquivo (5 MB)
  backup_count: 3              # quantos arquivos de backup manter
```

---

## Comandos personalizados (custom_commands.yaml)

Adicione atalhos de voz proprios:

```yaml
custom_commands:
  # Formato:
  #   trigger: "frase que voce fala"
  #   action: "categoria.acao"
  #   params: { parametros }

  - trigger: "abrir gmail"
    action: "browser.open_url"
    params:
      url: "https://mail.google.com"

  - trigger: "modo foco"
    action: "system.do_not_disturb"
    params:
      enabled: true

  - trigger: "abrir meu projeto"
    action: "files.open_folder"
    params:
      path: "C:\\Users\\MeuUsuario\\Projetos\\MeuApp"
```

As `actions` disponiveis estao documentadas em [docs/comandos.md](comandos.md).

---

## Prioridade de configuracao

Ordem de prioridade (maior para menor):

1. Flags de linha de comando (`--no-voice`, `--ptt`, etc.)
2. Variaveis de ambiente (`.env`)
3. `config/settings.yaml`
4. Valores padrao no codigo
