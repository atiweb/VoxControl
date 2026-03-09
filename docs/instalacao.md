# Guia de Instalacao

Guia completo para instalar e configurar o VoxControl no Windows.

---

## Requisitos do sistema

### Obrigatorios

| Requisito | Detalhes |
|-----------|----------|
| **Sistema operacional** | Windows 10 ou 11 (64-bit) |
| **Python** | 3.10 ou superior |
| **RAM** | Minimo 4GB (8GB recomendado para modelo `small`) |
| **Microfone** | Qualquer microfone USB ou integrado |
| **Espaco em disco** | ~1GB para dependencias + ~500MB para modelo Whisper `small` |

### Opcionais

| Requisito | Para que serve |
|-----------|----------------|
| Microsoft Office | Controle avancado via COM API (Word, Excel, PowerPoint) |
| GPU NVIDIA (CUDA) | Aceleracao do Whisper (transcricao mais rapida) |
| Chave API Claude | Compreensao avancada de linguagem natural |
| Chave API OpenAI | Alternativa ao Claude |
| OpenSSL | Gerar certificado HTTPS para microfone no celular |

---

## Instalacao passo a passo

### 1. Instalar Python

Se ainda nao tem Python instalado:

1. Baixe em https://www.python.org/downloads/
2. **IMPORTANTE**: marque "Add Python to PATH" durante a instalacao
3. Verifique: `python --version` (deve mostrar 3.10+)

### 2. Clonar o repositorio

```bash
git clone https://github.com/atiweb/VoxControl.git
cd VoxControl
```

Ou baixe o ZIP pelo GitHub e extraia.

### 3. Criar ambiente virtual (recomendado)

```bash
python -m venv .venv
.venv\Scripts\activate
```

Voce sabera que esta ativo quando ver `(.venv)` no inicio da linha de comando.

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

Isso instala ~40 pacotes. Aguarde 2-3 minutos.

### 5. Configurar variaveis de ambiente

```bash
copy .env.example .env
```

Abra o arquivo `.env` em um editor de texto e configure:

```env
# Pelo menos uma chave de API e recomendada (nao obrigatoria)
ANTHROPIC_API_KEY=sua_chave_aqui
OPENAI_API_KEY=sua_chave_aqui

# Ou use sem API
AI_BACKEND=offline
```

### 6. Verificar instalacao

```bash
python -m src.main --setup
```

Saida esperada:
```
Verificando instalacao...
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
  OK  vosk (opcional)

  OK  Chave Claude encontrada
  --  Chave OpenAI nao configurada

Tudo pronto! Execute: python -m src.main
```

### 7. Primeiro uso

```bash
# Modo texto (recomendado para primeiro teste)
python -m src.main --text --no-voice

# Digite comandos para testar:
>>> abrir calculadora
-> Calc aberto.
>>> pesquisar tempo em sao paulo
-> Pesquisando 'tempo em sao paulo' no Google.
>>> sair
```

### 8. Uso com microfone

```bash
# Modo wake word
python -m src.main

# Modo Push-to-Talk (segure F12)
python -m src.main --ptt
```

No primeiro uso com microfone, o modelo Whisper `small` (~500MB) sera baixado automaticamente do Hugging Face. Isso acontece apenas uma vez.

---

## Obtendo chaves de API

### Claude (Anthropic) - Recomendado

1. Acesse https://console.anthropic.com/
2. Crie uma conta
3. Va em "API Keys"
4. Crie uma nova chave
5. Copie para `.env` como `ANTHROPIC_API_KEY=sk-ant-...`

O modelo padrao (`claude-haiku-4-5`) custa aproximadamente $0.001 por comando. Para uso tipico (100 comandos/dia), o custo e de ~$3/mes.

### OpenAI

1. Acesse https://platform.openai.com/
2. Crie uma conta
3. Va em "API Keys"
4. Crie uma nova chave
5. Copie para `.env` como `OPENAI_API_KEY=sk-...`

O modelo padrao (`gpt-4o-mini`) tem custo similar ao Claude.

### Modo offline (sem API)

Se nao quiser usar APIs pagas, configure:
```env
AI_BACKEND=offline
```

O modo offline reconhece ~40 comandos diretos em portugues. Funciona bem para acoes comuns como "abrir chrome", "copiar", "salvar", mas nao entende linguagem natural complexa.

---

## Configuracao de GPU (opcional)

Se voce tem uma GPU NVIDIA, o Whisper pode usar CUDA para transcricao mais rapida:

1. Instale CUDA Toolkit: https://developer.nvidia.com/cuda-downloads
2. Instale cuDNN
3. No `config/settings.yaml`:
```yaml
stt:
  whisper:
    device: "cuda"
    compute_type: "float16"
```

Sem GPU, o Whisper funciona na CPU normalmente (um pouco mais lento, mas perfeitamente funcional).

---

## Troubleshooting

### "No module named 'sounddevice'"
```bash
pip install sounddevice
```

### "webrtcvad requires Visual C++ Build Tools"
O webrtcvad e opcional e esta comentado no requirements.txt. O Whisper ja tem VAD integrado.

### O microfone nao e detectado
1. Verifique nas configuracoes do Windows se o microfone esta habilitado
2. Teste: `python -c "import sounddevice; print(sounddevice.query_devices())"`
3. Se tiver multiplos microfones, configure em `settings.yaml`:
```yaml
audio:
  input_device: 1  # numero do dispositivo
```

### Whisper demora muito para carregar
Na primeira execucao, o modelo e baixado (~500MB para `small`). Execucoes subsequentes sao rapidas (3-5 segundos). Se quiser um modelo menor:
```yaml
stt:
  whisper:
    model_size: "base"  # ~150MB, mais rapido
```

### "UnicodeEncodeError" no terminal
O terminal do Windows pode nao suportar caracteres especiais. Execute com:
```bash
set PYTHONIOENCODING=utf-8
python -m src.main
```

### APIs retornam erro
- Verifique se a chave de API esta correta no `.env`
- Verifique se tem creditos na sua conta
- O sistema fara fallback automatico para o parser offline

### Office nao responde aos comandos
- Verifique se o Microsoft Office esta instalado
- O controle via COM API requer que o app esteja aberto
- Alternativa: os atalhos de teclado funcionam mesmo sem a COM API

---

## Atualizacao

```bash
cd VoxControl
git pull
pip install -r requirements.txt --upgrade
```

---

## Desinstalacao

```bash
# Remove o ambiente virtual
rmdir /s /q .venv

# Remove o diretorio do projeto
cd ..
rmdir /s /q VoxControl
```

Os modelos Whisper ficam em `%USERPROFILE%\.cache\huggingface\` e podem ser removidos manualmente se desejado.
