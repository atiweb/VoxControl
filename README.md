# VoxControl

**Open source voice control for Windows. Currently supports Portuguese, designed for multi-language expansion.**

Offline-first | AI-powered (Claude / OpenAI) | Mobile remote control | 80+ actions

---

## What is VoxControl?

VoxControl lets you control your Windows PC entirely by voice. It currently supports Portuguese (Brazilian and European) with an architecture designed for easy multi-language expansion.

It uses offline speech-to-text via Whisper and optionally interprets natural language through AI APIs (Claude or OpenAI) for advanced comprehension. It also works as a wireless remote: your smartphone on the same Wi-Fi network can send voice or text commands to the PC.

### Why does this project exist?

There was no complete, ready-to-use open source solution for voice control of Windows in Portuguese. The individual components existed (Whisper, pyautogui, AI APIs), but nobody had integrated them into a functional, extensible system. VoxControl fills that gap and is built to support additional languages over time.

---

## Funcionalidades

| Categoria | O que faz | Exemplos de comandos |
|-----------|-----------|----------------------|
| **Sistema** | Abre/fecha apps, volume, brilho, screenshots, lock, shutdown | "abrir calculadora", "tirar print", "aumentar volume" |
| **Navegador** | Chrome, Edge, Firefox: abas, pesquisa, scroll, zoom, favoritos | "pesquisar no Google noticias de hoje", "nova aba", "fechar aba" |
| **WhatsApp** | Abre chats, envia mensagens, pesquisa, anexos, audio | "enviar mensagem para Joao: oi tudo bem?", "abrir chat com Maria" |
| **Word** | Formatacao, tabelas, ortografia, impressao, localizar/substituir | "negrito", "inserir tabela 3 por 4", "verificar ortografia" |
| **Excel** | Celulas, formulas, graficos, filtros, tabelas dinamicas | "autoSoma", "ir para celula B5", "criar grafico de barras" |
| **PowerPoint** | Slides, apresentacao, imagens, temas | "novo slide", "iniciar apresentacao", "slide anterior" |
| **Arquivos** | Explorador, pastas, renomear, pesquisa, comprimir | "abrir downloads", "criar pasta projetos", "pesquisar relatorio" |
| **Midia** | Play/pause, Spotify, YouTube, faixas | "pausar musica", "proxima faixa", "abrir Spotify com jazz" |
| **Teclado/Mouse** | Digitar, atalhos, cliques, scroll | "copiar", "colar", "desfazer", "digitar ola mundo" |
| **Celular** | Controle remoto via Wi-Fi, interface web com microfone | Todos os comandos acima, do celular |

---

## Instalacao rapida

### Requisitos

- Windows 10 ou 11
- Python 3.10 ou superior
- Microfone (interno ou externo)
- Conexao com internet para primeiro download do modelo Whisper (~500MB para `small`)
- (Opcional) Microsoft Office para controle avancado via COM API
- (Opcional) Chave de API Claude ou OpenAI para compreensao por linguagem natural

### Passo a passo

```bash
# 1. Clone o repositorio
git clone https://github.com/atiweb/VoxControl.git
cd VoxControl

# 2. Crie e ative ambiente virtual
python -m venv .venv
.venv\Scripts\activate

# 3. Instale as dependencias
pip install -r requirements.txt

# 4. Configure (opcional, para IA avancada)
copy .env.example .env
# Edite .env e adicione ANTHROPIC_API_KEY ou OPENAI_API_KEY

# 5. Verifique a instalacao
python -m src.main --setup

# 6. Execute
python -m src.main
```

> Guia completo em [docs/instalacao.md](docs/instalacao.md)

---

## Modos de uso

| Modo | Comando | Descricao |
|------|---------|-----------|
| **Wake Word** | `python -m src.main` | Diga "computador" para ativar, depois o comando |
| **Push-to-Talk** | `python -m src.main --ptt` | Segure F12 enquanto fala |
| **Texto** | `python -m src.main --text` | Digita comandos (para testes) |
| **Verificacao** | `python -m src.main --setup` | Verifica se tudo esta instalado |

### Flags adicionais

| Flag | Efeito |
|------|--------|
| `--no-remote` | Desabilita servidor para celular |
| `--no-voice` | Desabilita resposta por voz (TTS) |

---

## Controle pelo celular

Ao iniciar, o sistema exibe um **QR Code** no terminal com o endereco de acesso:

```
  CONTROLE REMOTO DISPONIVEL
  Conecte pelo celular: http://192.168.1.100:8765
```

1. PC e celular na **mesma rede Wi-Fi**
2. Abra o link no browser do celular (ou escaneie o QR)
3. Segure o botao de microfone para falar, ou digite no campo de texto

A interface mobile inclui botoes rapidos para acoes comuns (Chrome, WhatsApp, print, volume, etc.).

> Detalhes em [docs/controle-remoto.md](docs/controle-remoto.md)

---

## Backends de IA

O sistema tem 3 niveis de interpretacao de comandos:

| Backend | Precisao | Custo | Requisitos |
|---------|----------|-------|------------|
| **Claude** (recomendado) | Excelente | ~$0.001/comando | ANTHROPIC_API_KEY |
| **OpenAI** | Muito boa | ~$0.001/comando | OPENAI_API_KEY |
| **Offline** | Basica (40 regras) | Gratuito | Nenhum |

**Com IA** (Claude/OpenAI): entende linguagem natural completa. Exemplo: "manda mensagem pro Joao no WhatsApp dizendo que vou me atrasar" funciona diretamente.

**Sem IA** (offline): reconhece comandos diretos como "abrir chrome", "copiar", "nova aba". Funciona sem internet apos o modelo Whisper estar baixado.

O fallback e automatico: se Claude falhar, tenta OpenAI; se ambos falharem, usa offline.

---

## Modelos Whisper (STT)

| Modelo | RAM | Velocidade | Precisao PT | Quando usar |
|--------|-----|------------|-------------|-------------|
| `tiny` | ~1GB | Muito rapida | Boa | Maquinas lentas, teste rapido |
| `base` | ~1GB | Rapida | Boa+ | Uso leve |
| **`small`** | ~2GB | Rapida | **Muito boa** | **Recomendado para a maioria** |
| `medium` | ~5GB | Media | Excelente | Hardware bom, max precisao |
| `large-v3` | ~10GB | Lenta | Excelente+ | GPU dedicada, max qualidade |

Configure em `config/settings.yaml` ou `.env`:
```yaml
stt:
  whisper:
    model_size: "small"
```

---

## Exemplos de comandos

### Linguagem natural (com Claude/OpenAI)
```
"Pesquisa no YouTube tutoriais de Python"
"Manda mensagem no WhatsApp para a Ana dizendo que vou me atrasar"
"Abre o Excel e cria uma nova planilha"
"Faz um print da tela e salva na area de trabalho"
"Fecha todas as janelas e mostra a area de trabalho"
"Aumenta o volume para 70 por cento"
```

### Comandos diretos (funciona offline)
```
"abrir chrome"              -> abre o Chrome
"pesquisar clima amanha"    -> Google: "clima amanha"
"tirar print"               -> screenshot na area de trabalho
"aumentar volume"           -> sobe o volume
"salvar"                    -> Ctrl+S
"desfazer"                  -> Ctrl+Z
"copiar"                    -> Ctrl+C
"minimizar"                 -> minimiza janela atual
"nova aba"                  -> Ctrl+T (no navegador)
"rolar para baixo"          -> scroll down
"bloquear tela"             -> Win+L
```

> Referencia completa: [docs/comandos.md](docs/comandos.md)

---

## Comandos personalizados

Adicione seus atalhos em `config/custom_commands.yaml`:

```yaml
custom_commands:
  - trigger: "abrir meu email"
    action: "browser.open_url"
    params:
      url: "https://mail.google.com"

  - trigger: "modo foco"
    action: "system.do_not_disturb"
    params:
      enabled: true

  - trigger: "mensagem para o chefe"
    action: "whatsapp.open_chat"
    params:
      contact: "Carlos"
```

---

## Estrutura do projeto

```
VoxControl/
|-- config/
|   |-- settings.yaml          # configuracoes gerais
|   |-- custom_commands.yaml   # comandos personalizados
|-- docs/                      # documentacao completa
|   |-- instalacao.md
|   |-- configuracao.md
|   |-- comandos.md
|   |-- controle-remoto.md
|   |-- arquitetura.md
|-- src/
|   |-- main.py                # ponto de entrada CLI
|   |-- core/engine.py         # orquestrador principal
|   |-- audio/
|   |   |-- listener.py        # captura de microfone + wake word
|   |   |-- transcriber.py     # STT (Whisper / Vosk)
|   |-- ai/
|   |   |-- intent_parser.py   # Claude / OpenAI / offline
|   |   |-- prompts.py         # prompt do sistema com 80+ acoes
|   |-- actions/
|   |   |-- dispatcher.py      # roteador de acoes
|   |   |-- system_control.py  # Windows (apps, volume, tela)
|   |   |-- browser_control.py # Chrome / Edge / Firefox
|   |   |-- whatsapp_control.py# WhatsApp Web
|   |   |-- office_control.py  # Word / Excel / PowerPoint
|   |   |-- file_control.py    # arquivos e pastas
|   |   |-- media_control.py   # Spotify / YouTube / player
|   |   |-- keyboard_control.py# teclado e mouse
|   |-- voice/speaker.py       # TTS portugues (pyttsx3)
|   |-- remote/
|       |-- server.py          # FastAPI + WebSocket
|       |-- static/index.html  # interface mobile
|-- models/                    # modelos Vosk (opcional)
|-- logs/                      # logs da aplicacao
|-- requirements.txt
|-- .env.example
|-- .gitignore
```

---

## Estatisticas do codigo

| Metrica | Valor |
|---------|-------|
| Arquivos Python | 23 |
| Linhas de codigo | ~2.700 |
| Acoes suportadas | 80+ |
| Regras offline | ~40 |
| Dependencias | 40+ pacotes |

---

## Documentacao completa

| Documento | Conteudo |
|-----------|----------|
| [docs/instalacao.md](docs/instalacao.md) | Guia completo de instalacao, requisitos, troubleshooting |
| [docs/configuracao.md](docs/configuracao.md) | Todas as opcoes de settings.yaml e .env |
| [docs/comandos.md](docs/comandos.md) | Referencia de todas as 80+ acoes com parametros |
| [docs/controle-remoto.md](docs/controle-remoto.md) | Configuracao do celular, HTTPS, WebSocket API |
| [docs/arquitetura.md](docs/arquitetura.md) | Arquitetura do sistema, como contribuir, roadmap |

---

## Contribuindo

PRs sao bem-vindos! Areas prioritarias:

- Mais comandos para apps especificos (Outlook, Teams, VS Code, Telegram)
- Integracao com Telegram bot (alternativa ao servidor web para celular)
- Melhorias no suporte a PT-PT (europeu)
- Testes automatizados
- Empacotamento como `.exe` via PyInstaller
- Interface grafica (tray icon)
- Plugin system para extensoes da comunidade

### Como contribuir

1. Fork o repositorio
2. Crie uma branch: `git checkout -b minha-feature`
3. Faca suas alteracoes
4. Teste com `python -m src.main --text`
5. Envie um PR

---

## Licenca

MIT -- use livremente, inclusive em projetos comerciais.

---

*Desenvolvido para a comunidade lusofona. Se este projeto foi util, deixe uma estrela no GitHub!*
