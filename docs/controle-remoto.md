# Remote Control via Smartphone

Use your smartphone as a wireless PC remote control over local Wi-Fi.

---

## How It Works

VoxControl starts a web server on the PC. Your phone accesses this server through the browser and sends voice or text commands. Communication is real-time via WebSocket.

There are **three ways** to control VoxControl remotely:

| Client | Type | Best For |
|--------|------|----------|
| **Mobile browser** | Web app (HTML) | Quick access, no install |
| **Flutter app** | Native app (iOS/Android) | Full experience |
| **Custom client** | REST API + WebSocket | Integration / automation |

```
Phone (browser/app)  <----Wi-Fi---->    PC (FastAPI server)
     |                                       |
     | REST API + WebSocket (JWT auth)       | VoiceEngine
     |                                       |
   Voice or Text  -------->  Transcription + AI + Action
                   <--------  Text response
```

---

## Language Adaptation

The mobile interface **automatically adapts to the configured language**. When the phone connects via WebSocket, the server sends a `config` message with all UI strings in the active language. This includes:

- Placeholder text
- Status messages (connecting, connected, disconnected)
- Quick command button values
- Speech recognition language (Web Speech API)

Change language on the server (e.g., `--lang en`), and the mobile UI updates automatically.

---

## Basic Setup

### 1. Start the server

By default, the remote server is enabled. Just start normally:

```bash
python -m src.main
```

The terminal will show:

```
  REMOTE CONTROL AVAILABLE
  Connect from your phone: http://192.168.1.100:8765
  [QR CODE here]
```

> The banner text adapts to the configured language (PT/ES/EN).

### 2. Connect your phone

1. Phone and PC must be on the **same Wi-Fi network**
2. Open the phone browser (Chrome, Safari, etc.)
3. Navigate to the address shown in terminal (e.g., `http://192.168.1.100:8765`)
4. Or scan the QR code with your camera

### 3. Use it

The mobile interface offers:

- **Microphone button**: hold to speak (HTTPS required)
- **Text field**: type commands (always works)
- **Quick buttons**: common actions with one tap

---

## Mobile Interface

The web interface is designed for mobile use with a dark, responsive layout.

### Elements

| Element | Function |
|---------|----------|
| Green/red indicator | Connection status (connected/disconnected) |
| Message area | Command and response history (chat style) |
| Quick buttons | Chrome, WhatsApp, Screenshot, Play/Pause, Volume, Minimize, Lock |
| Text field | Type commands manually |
| Microphone button | Hold to speak (requires HTTPS for mic) |

### Quick Buttons

Quick buttons send localized commands based on the server language:

| Button | PT Command | ES Command | EN Command |
|--------|-----------|-----------|-----------|
| Chrome | abrir chrome | abrir chrome | open chrome |
| WhatsApp | abrir whatsapp | abrir whatsapp | open whatsapp |
| Screenshot | tirar print | captura de pantalla | take screenshot |
| Vol + | aumentar volume | subir volumen | volume up |
| Vol - | diminuir volume | bajar volumen | volume down |
| Minimize | minimizar | minimizar | minimize |
| Lock | bloquear tela | bloquear pantalla | lock screen |

---

## HTTPS Setup (for phone microphone)

Modern browsers **require HTTPS** to access the microphone on local networks.
Without HTTPS, the text field still works, but the microphone button won't.

### Generate a self-signed certificate

```bash
# Requires OpenSSL installed
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=voxcontrol"
```

### Configure in .env

```env
SSL_CERTFILE=cert.pem
SSL_KEYFILE=key.pem
```

### On the phone

1. Navigate to `https://192.168.1.100:8765` (note the **https**)
2. The browser will show an untrusted certificate warning
3. Accept/proceed (this is normal for self-signed certificates)
4. Now the microphone works

---

## HTTP API

In addition to the web interface, the server exposes HTTP endpoints for programmatic integration.

### GET /status

Check if the server is online.

```bash
curl http://192.168.1.100:8765/status
```

Response:
```json
{
  "status": "online",
  "engine_ready": true,
  "connected_clients": 1,
  "language": "en"
}
```

> The `language` field shows the current server language.

---

## WebSocket Protocol

For real-time communication, connect via WebSocket at `ws://IP:8765/ws` (or `wss://` with HTTPS).

### Server -> Client messages

```json
// Config (sent immediately on connect, contains language strings)
{"type": "config", "data": {"language": "en-US", "connecting": "Connecting...", ...}}

// Status
{"type": "status", "data": "connected"}

// Response to a command
{"type": "response", "data": "Chrome opened."}

// Pong (reply to ping)
{"type": "pong"}

// Broadcast (message to all clients)
{"type": "broadcast", "data": "Some notification"}
```

### Client -> Server messages

```json
// Text command
{"type": "text", "data": "open chrome"}

// Base64 audio (PCM float32 16kHz)
{"type": "audio_b64", "data": "AAAA...base64..."}

// Ping
{"type": "ping"}
```

### Python Example

```python
import asyncio
import json
import websockets

async def control():
    async with websockets.connect("ws://192.168.1.100:8765/ws") as ws:
        # Receive config
        config = json.loads(await ws.recv())
        print(f"Language: {config['data']['language']}")

        # Receive status
        status = json.loads(await ws.recv())
        print(f"Status: {status['data']}")

        # Send command
        await ws.send(json.dumps({"type": "text", "data": "open calculator"}))

        # Receive response
        resp = json.loads(await ws.recv())
        print(f"Response: {resp['data']}")

asyncio.run(control())
```

### JavaScript Example

```javascript
const ws = new WebSocket("ws://192.168.1.100:8765/ws");

ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.type === "config") {
        console.log("Language:", msg.data.language);
    } else if (msg.type === "response") {
        console.log("Response:", msg.data);
    }
};

ws.onopen = () => {
    ws.send(JSON.stringify({type: "text", data: "open chrome"}));
};
```

---

## Advanced Configuration

### Change the port

```yaml
# config/settings.yaml
remote:
  port: 9090
```

Or via `.env`:
```env
REMOTE_SERVER_PORT=9090
```

### Disable QR Code

```yaml
remote:
  show_qr: false
```

### Disable remote server

```bash
python -m src.main --no-remote
```

Or in `settings.yaml`:
```yaml
remote:
  enabled: false
```

### Basic authentication

The remote server supports **JWT authentication** for secure access.

#### Enable authentication

In `settings.yaml`:
```yaml
auth:
  enabled: true
  token_expiry_hours: 24
  max_attempts: 5
  lockout_minutes: 15
```

#### Create a user

```bash
python -c "from src.auth.auth import AuthManager; AuthManager().create_user('admin', 'your_password')"
```

#### Login flow

```bash
# 1. Login to get JWT token
curl -X POST http://IP:8765/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
# Response: {"access_token": "eyJ...", "token_type": "bearer"}

# 2. Use token in subsequent requests
curl http://IP:8765/status -H "Authorization: Bearer eyJ..."

# 3. WebSocket with token
ws://IP:8765/ws?token=eyJ...
```

The mobile web interface and Flutter app handle login automatically with a login screen.

---

## Flutter Mobile App

A native mobile app is available for iOS and Android, built with Flutter.

### Features

- Native UI with dark theme
- Dual transport: REST API + WebSocket
- JWT login screen
- Voice input (native speech recognition)
- Text input
- Real-time command/response history
- Connection status indicator
- Server URL configuration

### Build from source

```bash
cd mobile/voxcontrol_mobile
flutter pub get
flutter run          # debug on connected device
flutter build apk    # Android release
flutter build ios    # iOS release
```

### Architecture

The Flutter app uses Provider for state management:

```
lib/
├── main.dart                 # App entry + MaterialApp
├── models/
│   └── command.dart          # Command data model
├── services/
│   ├── api_service.dart      # REST API + JWT auth
│   └── websocket_service.dart  # WebSocket real-time connection
├── providers/
│   └── app_provider.dart     # Central state management
└── screens/
    ├── home_screen.dart      # Main control screen
    ├── login_screen.dart     # JWT authentication
    └── settings_screen.dart  # Server URL configuration
```

---

## Multiple Clients

The server supports multiple phones/tablets connected simultaneously. All can send commands and all receive responses.

---

## Known Limitations

1. **Microphone requires HTTPS**: without SSL certificate, the text field is the only option
2. **Same Wi-Fi network**: does not work over the internet (for security)
3. **Latency**: depends on local Wi-Fi quality (~100-500ms typical)
4. **Web Speech API**: voice recognition on the phone uses the browser API, which may require internet (Google Speech) even if the PC uses Whisper offline
5. **iOS Safari**: may have additional restrictions for Web Speech API
