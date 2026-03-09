# Controle Remoto pelo Celular

Use seu smartphone como controle remoto do PC, sem fio, pela rede Wi-Fi local.

---

## Como funciona

O VoxControl inicia um servidor web no PC. Seu celular acessa esse servidor pelo navegador e envia comandos por voz ou texto. A comunicacao e em tempo real via WebSocket.

```
Celular (navegador)  <----Wi-Fi---->  PC (servidor FastAPI)
     |                                       |
     | WebSocket / HTTP                      | VoiceEngine
     |                                       |
   Voz ou Texto  -------->  Transcricao + IA + Acao
                  <--------  Resposta de texto
```

---

## Configuracao basica

### 1. Iniciar o servidor

Por padrao, o servidor remoto e habilitado. Basta iniciar normalmente:

```bash
python -m src.main
```

O terminal mostrara:

```
  CONTROLE REMOTO DISPONIVEL
  Conecte pelo celular: http://192.168.1.100:8765
  [QR CODE aqui]
```

### 2. Conectar o celular

1. Celular e PC devem estar na **mesma rede Wi-Fi**
2. Abra o navegador do celular (Chrome, Safari, etc.)
3. Acesse o endereco mostrado no terminal (ex: `http://192.168.1.100:8765`)
4. Ou escaneie o QR Code com a camera

### 3. Usar

A interface mobile oferece:

- **Botao de microfone**: segure para falar (se HTTPS configurado)
- **Campo de texto**: digite comandos (sempre funciona)
- **Botoes rapidos**: acoes comuns com um toque

---

## Interface mobile

A interface web foi projetada para uso no celular com design escuro e responsivo.

### Elementos

| Elemento | Funcao |
|----------|--------|
| Indicador verde/vermelho | Status da conexao (conectado/desconectado) |
| Area de mensagens | Historico de comandos e respostas (estilo chat) |
| Botoes rapidos | Chrome, WhatsApp, Print, Play/Pause, Volume, Minimizar, Bloquear |
| Campo de texto | Digitar comandos manualmente |
| Botao de microfone | Segure para falar (requer HTTPS para mic) |

### Botoes rapidos incluidos

- **Chrome** -- abre o Google Chrome
- **WhatsApp** -- abre WhatsApp Web
- **Print** -- tira screenshot
- **Play/Pause** -- controla midia
- **Vol +** / **Vol -** -- ajusta volume
- **Minimizar** -- minimiza janela atual
- **Bloquear** -- bloqueia a tela

---

## Configuracao HTTPS (para microfone no celular)

Browsers modernos **exigem HTTPS** para acessar o microfone em redes locais.
Sem HTTPS, o campo de texto ainda funciona, mas o botao de microfone nao.

### Gerar certificado auto-assinado

```bash
# Requer OpenSSL instalado
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=voz-controle"
```

### Configurar no .env

```env
SSL_CERTFILE=cert.pem
SSL_KEYFILE=key.pem
```

### No celular

1. Acesse `https://192.168.1.100:8765` (note o **https**)
2. O navegador mostrara aviso de certificado nao confiavel
3. Aceite/prossiga (isso e normal para certificados auto-assinados)
4. Agora o microfone funciona

---

## API HTTP

Alem da interface web, o servidor expoe endpoints HTTP para integracao programatica.

### GET /status

Verifica se o servidor esta online.

```bash
curl http://192.168.1.100:8765/status
```

Resposta:
```json
{
  "status": "online",
  "engine_ready": true,
  "connected_clients": 1
}
```

### POST /command

Envia um comando de texto.

```bash
curl -X POST http://192.168.1.100:8765/command \
  -H "Content-Type: application/json" \
  -d '{"text": "abrir calculadora"}'
```

Resposta:
```json
{
  "command": "abrir calculadora",
  "response": "Calc aberto."
}
```

---

## Protocolo WebSocket

Para comunicacao em tempo real, conecte via WebSocket em `ws://IP:8765/ws` (ou `wss://` com HTTPS).

### Mensagens do cliente para o servidor

```json
// Comando de texto
{"type": "text", "data": "abrir chrome"}

// Audio em base64 (PCM float32 16kHz)
{"type": "audio_b64", "data": "AAAA...base64..."}

// Ping
{"type": "ping"}
```

### Mensagens do servidor para o cliente

```json
// Resposta a um comando
{"type": "response", "data": "Chrome aberto."}

// Status de conexao
{"type": "status", "data": "connected"}

// Pong (resposta a ping)
{"type": "pong"}

// Broadcast (mensagem para todos os clientes)
{"type": "broadcast", "data": "Alguma notificacao"}
```

### Exemplo em Python

```python
import asyncio
import json
import websockets

async def controlar():
    async with websockets.connect("ws://192.168.1.100:8765/ws") as ws:
        # Enviar comando
        await ws.send(json.dumps({"type": "text", "data": "abrir calculadora"}))

        # Receber resposta
        resp = json.loads(await ws.recv())
        print(f"Resposta: {resp['data']}")

asyncio.run(controlar())
```

### Exemplo em JavaScript

```javascript
const ws = new WebSocket("ws://192.168.1.100:8765/ws");

ws.onopen = () => {
    ws.send(JSON.stringify({type: "text", data: "abrir chrome"}));
};

ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    console.log("Resposta:", msg.data);
};
```

---

## Configuracao avancada

### Mudar a porta

```yaml
# config/settings.yaml
remote:
  port: 9090
```

Ou via `.env`:
```env
REMOTE_SERVER_PORT=9090
```

### Desabilitar QR Code

```yaml
remote:
  show_qr: false
```

### Desabilitar servidor remoto

```bash
python -m src.main --no-remote
```

Ou em `settings.yaml`:
```yaml
remote:
  enabled: false
```

### Autenticacao basica

Defina um token em `settings.yaml`:
```yaml
remote:
  auth_token: "meu_token_secreto_123"
```

Os clientes precisarao enviar este token nas requisicoes.

---

## Multiplos clientes

O servidor suporta multiplos celulares/tablets conectados simultaneamente. Todos podem enviar comandos e todos recebem as respostas.

---

## Limitacoes conhecidas

1. **Microfone requer HTTPS**: sem certificado SSL, o campo de texto e a unica opcao
2. **Mesma rede Wi-Fi**: nao funciona pela internet (por seguranca)
3. **Latencia**: depende da qualidade da rede Wi-Fi local (~100-500ms tipico)
4. **Web Speech API**: o reconhecimento de voz no celular usa a API do navegador, que pode requerer internet (Google Speech) mesmo que o PC use Whisper offline
5. **iOS Safari**: pode ter restricoes adicionais para Web Speech API
