"""
Servidor FastAPI + WebSocket para controle remoto via celular.
API REST con autenticacion JWT + WebSocket autenticado.
"""

import asyncio
import base64
import json
import logging
import os
import socket
from typing import Optional, TYPE_CHECKING

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from ..core.engine import VoiceEngine

from ..i18n import t, get_language, SPEECH_RECOGNITION_LANG, STRINGS
from ..auth.auth import AuthManager
from ..auth.middleware import RateLimiter, RateLimitMiddleware
from ..validation import sanitize_text_input

logger = logging.getLogger(__name__)

app = FastAPI(
    title="VoxControl API",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url=None,
)

# CORS for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restricted in production via config
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

# Engine & state injected at runtime
_engine: Optional["VoiceEngine"] = None
_auth: Optional[AuthManager] = None
_rate_limiter: Optional[RateLimiter] = None
_connections: dict[WebSocket, str] = {}  # ws -> username
_server_lang: str = "pt"
_auth_required: bool = True
_middleware_added: bool = False


def set_engine(engine: "VoiceEngine"):
    global _engine
    _engine = engine


def set_server_lang(lang: str):
    global _server_lang
    _server_lang = lang


def get_local_ip() -> str:
    """Gets the local IP address on the Wi-Fi network."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def generate_qr(url: str) -> str:
    """Generates an ASCII QR code for terminal display."""
    try:
        import qrcode
        qr = qrcode.QRCode(border=1)
        qr.add_data(url)
        qr.make(fit=True)
        import io
        f = io.StringIO()
        qr.print_ascii(out=f)
        return f.getvalue()
    except ImportError:
        return f"(install qrcode to display QR)\nURL: {url}"


def _get_client_strings() -> dict:
    """Returns UI strings for the remote client based on current language."""
    lang = _server_lang
    lang_strings = STRINGS.get(lang, STRINGS.get("en", {}))
    return {
        "language": SPEECH_RECOGNITION_LANG.get(lang, "en-US"),
        "connecting": lang_strings.get("ui_connecting", "Connecting..."),
        "connected": lang_strings.get("ui_connected", "Connected."),
        "disconnected": lang_strings.get("ui_disconnected", "Disconnected. Reconnecting..."),
        "connection_error": lang_strings.get("ui_connection_error", "Connection error."),
        "no_connection": lang_strings.get("ui_no_connection", "No connection."),
        "mic_error": lang_strings.get("ui_mic_error", "Could not access microphone."),
        "hold_to_speak": lang_strings.get("ui_hold_to_speak", "Hold button to speak"),
        "listening": lang_strings.get("ui_listening", "Listening..."),
        "processing": lang_strings.get("ui_processing", "Processing..."),
        "placeholder": lang_strings.get("ui_placeholder", "Type a command..."),
        # Quick command data-cmd values
        "qc_chrome": lang_strings.get("qc_chrome", "open chrome"),
        "qc_whatsapp": lang_strings.get("qc_whatsapp", "open whatsapp"),
        "qc_screenshot": lang_strings.get("qc_screenshot", "take screenshot"),
        "qc_vol_up": lang_strings.get("qc_vol_up", "volume up"),
        "qc_vol_down": lang_strings.get("qc_vol_down", "volume down"),
        "qc_minimize": lang_strings.get("qc_minimize", "minimize"),
        "qc_lock": lang_strings.get("qc_lock", "lock screen"),
    }


def _verify_token(credentials: Optional[HTTPAuthorizationCredentials]) -> str:
    """Verify JWT token and return username."""
    if not _auth_required:
        return "local"
    if not credentials or not _auth:
        raise HTTPException(status_code=401, detail="Authentication required")
    username = _auth.validate_token(credentials.credentials)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return username


# ---- Pydantic models for API ----

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)

class CommandRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)

class AudioRequest(BaseModel):
    audio_b64: str = Field(..., min_length=1)


# ------------------------------------------------------------------ ENDPOINTS

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serves the mobile interface."""
    from ..paths import get_bundled_resource, is_frozen
    if is_frozen():
        static_path = get_bundled_resource("src/remote/static") / "index.html"
    else:
        static_path = Path(__file__).parent / "static" / "index.html"
    if static_path.exists():
        return HTMLResponse(static_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>VoxControl</h1><p>Mobile interface not found.</p>")


# ---- AUTH API ----

@app.get("/api/auth/status")
async def auth_status():
    """Check if auth is required and if users exist."""
    return {
        "auth_required": _auth_required,
        "has_users": _auth.has_users() if _auth else False,
        "version": "2.0.0",
    }


@app.post("/api/auth/register")
async def register(req: RegisterRequest):
    """Register the first user (only works when no users exist)."""
    if not _auth:
        raise HTTPException(status_code=500, detail="Auth not initialized")
    if _auth.has_users():
        raise HTTPException(status_code=403, detail="Registration closed. Users already exist.")
    if not _auth.create_user(req.username, req.password):
        raise HTTPException(status_code=400, detail="Failed to create user")
    token = _auth.authenticate(req.username, req.password)
    return {"token": token, "username": req.username}


@app.post("/api/auth/login")
async def login(req: LoginRequest):
    """Authenticate and get a JWT token."""
    if not _auth:
        raise HTTPException(status_code=500, detail="Auth not initialized")
    token = _auth.authenticate(req.username, req.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": token, "username": req.username}


# ---- COMMAND API ----

@app.get("/api/status")
async def api_status(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Get server status (authenticated)."""
    username = _verify_token(credentials)
    return {
        "status": "online",
        "engine_ready": _engine is not None,
        "connected_clients": len(_connections),
        "language": _server_lang,
        "user": username,
        "strings": _get_client_strings(),
    }


@app.post("/api/command")
async def api_command(req: CommandRequest, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Send a text command via REST API."""
    username = _verify_token(credentials)
    text = sanitize_text_input(req.text)
    if not text:
        raise HTTPException(status_code=400, detail="Empty command")

    if not _engine:
        raise HTTPException(status_code=503, detail="Engine not ready")

    logger.info(f"REST command from '{username}': {text}")
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, _engine.process_text, text)
    return {"response": response}


@app.post("/api/audio")
async def api_audio(req: AudioRequest, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Send base64-encoded audio via REST API."""
    username = _verify_token(credentials)
    if not _engine:
        raise HTTPException(status_code=503, detail="Engine not ready")

    try:
        import numpy as np
        audio_bytes = base64.b64decode(req.audio_b64)
        audio = np.frombuffer(audio_bytes, dtype=np.float32)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid audio data")

    logger.info(f"REST audio from '{username}'")
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, _engine.process_audio, audio)
    return {"response": response or t("audio_not_understood")}


@app.get("/api/actions")
async def api_actions(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Get list of available actions."""
    _verify_token(credentials)
    from ..validation import VALID_ACTIONS
    actions = []
    for prefix, subs in VALID_ACTIONS.items():
        for sub in sorted(subs):
            actions.append(f"{prefix}.{sub}")
    return {"actions": sorted(actions)}


# ---- WEBSOCKET (authenticated) ----

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = Query(None)):
    """
    WebSocket for real-time bidirectional communication.
    Authentication via query param: /ws?token=<jwt>
    Or via first message: {"type": "auth", "token": "<jwt>"}
    """
    await websocket.accept()
    username = None

    # Try query param auth first
    if token and _auth:
        username = _auth.validate_token(token)
    elif not _auth_required:
        username = "local"

    # If not authenticated yet, wait for auth message
    if not username and _auth_required:
        try:
            raw = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
            message = json.loads(raw)
            if message.get("type") == "auth" and _auth:
                username = _auth.validate_token(message.get("token", ""))
            if not username:
                await websocket.send_text(json.dumps({"type": "error", "data": "Authentication failed"}))
                await websocket.close(code=4001, reason="Authentication failed")
                return
        except asyncio.TimeoutError:
            await websocket.close(code=4001, reason="Authentication timeout")
            return

    _connections[websocket] = username or "anonymous"
    logger.info(f"Client connected: {websocket.client} (user: {username})")

    # Send config (language strings) first, then status
    client_strings = _get_client_strings()
    await websocket.send_text(json.dumps({"type": "config", "data": client_strings}))
    await websocket.send_text(json.dumps({"type": "status", "data": "connected", "user": username}))

    try:
        while True:
            raw = await websocket.receive_text()
            message = json.loads(raw)
            msg_type = message.get("type", "text")
            data = message.get("data", "")

            response = None

            if msg_type == "text":
                data = sanitize_text_input(data)
                if not data:
                    continue
                if _engine:
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(None, _engine.process_text, data)
                else:
                    response = t("engine_not_ready")

            elif msg_type == "audio_b64":
                import numpy as np
                try:
                    audio_bytes = base64.b64decode(data)
                    audio = np.frombuffer(audio_bytes, dtype=np.float32)
                except Exception:
                    response = "Invalid audio data"
                    await websocket.send_text(json.dumps({"type": "error", "data": response}))
                    continue

                if _engine:
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(None, _engine.process_audio, audio)
                    response = response or t("audio_not_understood")
                else:
                    response = t("engine_not_ready")

            elif msg_type == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
                continue

            if response:
                await websocket.send_text(json.dumps({"type": "response", "data": response}))

    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {websocket.client}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        _connections.pop(websocket, None)


async def broadcast(message: str):
    """Sends message to all connected clients."""
    disconnected = []
    for ws in _connections:
        try:
            await ws.send_text(json.dumps({"type": "broadcast", "data": message}))
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        _connections.pop(ws, None)


def start_server(config: dict, engine: "VoiceEngine", lang: str = "pt"):
    """Starts the server in a separate thread with auth and rate limiting."""
    import threading
    import uvicorn

    global _auth, _rate_limiter, _auth_required, _middleware_added

    set_engine(engine)
    set_server_lang(lang)

    # Initialize auth
    auth_config = config.get("auth", {})
    _auth_required = auth_config.get("enabled", True)
    if _auth_required:
        _auth = AuthManager(auth_config)
        logger.info(f"Auth enabled. Users exist: {_auth.has_users()}")
    else:
        logger.warning("Auth DISABLED — any device on the network can send commands.")

    # Initialize rate limiter
    rate_config = config.get("rate_limit", {})
    _rate_limiter = RateLimiter(
        max_requests=rate_config.get("max_requests", 60),
        window_seconds=rate_config.get("window_seconds", 60),
    )
    if not _middleware_added:
        app.add_middleware(RateLimitMiddleware, rate_limiter=_rate_limiter)
        _middleware_added = True

    host = config.get("host", "0.0.0.0")
    port = config.get("port", 8765)
    ssl_certfile = config.get("ssl_certfile") or os.getenv("SSL_CERTFILE")
    ssl_keyfile = config.get("ssl_keyfile") or os.getenv("SSL_KEYFILE")

    local_ip = get_local_ip()
    scheme = "https" if ssl_certfile else "http"
    url = f"{scheme}://{local_ip}:{port}"

    logger.info(f"Remote server starting at {url}")

    if config.get("show_qr", True):
        qr = generate_qr(url)
        print("\n" + "="*50)
        print(f"  {t('remote_available')}")
        print(f"  {t('remote_connect_msg', url=url)}")
        if _auth_required and _auth and not _auth.has_users():
            print(f"  First-time setup: register at {url}/api/docs")
        print("="*50)
        print(qr)
        print("="*50 + "\n")

    uvicorn_config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="warning",
        ssl_certfile=ssl_certfile if ssl_certfile else None,
        ssl_keyfile=ssl_keyfile if ssl_keyfile else None,
    )
    server = uvicorn.Server(uvicorn_config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    return thread
