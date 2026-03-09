"""
Servidor FastAPI + WebSocket para controle remoto via celular.
O celular se conecta via Wi-Fi local e envia comandos de voz ou texto.
"""

import asyncio
import json
import logging
import os
import socket
from typing import Optional, TYPE_CHECKING

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

if TYPE_CHECKING:
    from ..core.engine import VoiceEngine

from ..i18n import t, get_language, SPEECH_RECOGNITION_LANG, STRINGS

logger = logging.getLogger(__name__)

app = FastAPI(title="VoxControl - Remote API", version="1.1.0")

# Engine injetada em runtime
_engine: Optional["VoiceEngine"] = None
_connections: set = set()
_server_lang: str = "pt"


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


# ------------------------------------------------------------------ ENDPOINTS

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serves the mobile interface."""
    static_path = Path(__file__).parent / "static" / "index.html"
    if static_path.exists():
        return HTMLResponse(static_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>VoxControl</h1><p>Mobile interface not found.</p>")


@app.get("/status")
async def status():
    return JSONResponse({
        "status": "online",
        "engine_ready": _engine is not None,
        "connected_clients": len(_connections),
        "language": _server_lang,
    })


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket for real-time bidirectional communication.
    Protocol:
      Client -> Server: {"type": "text", "data": "open chrome"}
      Client -> Server: {"type": "audio_b64", "data": "<base64 PCM 16kHz>"}
      Server -> Client: {"type": "response", "data": "Chrome opened."}
      Server -> Client: {"type": "config", "data": {...}}
      Server -> Client: {"type": "status", "data": "connected"}
    """
    await websocket.accept()
    _connections.add(websocket)
    logger.info(f"Client connected: {websocket.client}")

    # Send config (language strings) first, then status
    client_strings = _get_client_strings()
    await websocket.send_text(json.dumps({"type": "config", "data": client_strings}))
    await websocket.send_text(json.dumps({"type": "status", "data": "connected"}))

    try:
        while True:
            raw = await websocket.receive_text()
            message = json.loads(raw)
            msg_type = message.get("type", "text")
            data = message.get("data", "")

            response = None

            if msg_type == "text":
                if _engine:
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(None, _engine.process_text, data)
                else:
                    response = t("engine_not_ready")

            elif msg_type == "audio_b64":
                import base64
                import numpy as np
                audio_bytes = base64.b64decode(data)
                audio = np.frombuffer(audio_bytes, dtype=np.float32)
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
        _connections.discard(websocket)


async def broadcast(message: str):
    """Sends message to all connected clients."""
    disconnected = set()
    for ws in _connections:
        try:
            await ws.send_text(json.dumps({"type": "broadcast", "data": message}))
        except Exception:
            disconnected.add(ws)
    _connections -= disconnected


def start_server(config: dict, engine: "VoiceEngine", lang: str = "pt"):
    """Starts the server in a separate thread."""
    import threading
    import uvicorn

    set_engine(engine)
    set_server_lang(lang)

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
