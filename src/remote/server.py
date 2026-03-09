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

logger = logging.getLogger(__name__)

app = FastAPI(title="VoxControl - Remote API", version="1.0.0")

# Engine injetada em runtime
_engine: Optional["VoiceEngine"] = None
_connections: set = set()


def set_engine(engine: "VoiceEngine"):
    global _engine
    _engine = engine


def get_local_ip() -> str:
    """Obtém o IP local da máquina na rede Wi-Fi."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def generate_qr(url: str) -> str:
    """Gera QR code em ASCII para exibir no terminal."""
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
        return f"(instale qrcode para exibir QR)\nURL: {url}"


# ------------------------------------------------------------------ ENDPOINTS

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve a interface mobile."""
    static_path = Path(__file__).parent / "static" / "index.html"
    if static_path.exists():
        return HTMLResponse(static_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Voz Controle PT</h1><p>Interface mobile não encontrada.</p>")


@app.get("/status")
async def status():
    return JSONResponse({
        "status": "online",
        "engine_ready": _engine is not None,
        "connected_clients": len(_connections),
    })


@app.post("/command")
async def command_http(payload: dict):
    """Endpoint HTTP para enviar comando de texto."""
    text = payload.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Campo 'text' obrigatório.")
    if _engine is None:
        raise HTTPException(status_code=503, detail="Engine não iniciada.")

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _engine.process_text, text)
    return JSONResponse({"command": text, "response": result})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket para comunicação bidirecional em tempo real.
    Protocolo:
      Cliente -> Servidor: {"type": "text", "data": "abrir chrome"}
      Cliente -> Servidor: {"type": "audio_b64", "data": "<base64 PCM 16kHz>"}
      Servidor -> Cliente: {"type": "response", "data": "Chrome aberto."}
      Servidor -> Cliente: {"type": "status", "data": "listening"}
    """
    await websocket.accept()
    _connections.add(websocket)
    logger.info(f"Cliente conectado: {websocket.client}")
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
                    response = "Engine não iniciada."

            elif msg_type == "audio_b64":
                # Áudio em base64 (PCM float32 16kHz)
                import base64
                import numpy as np
                audio_bytes = base64.b64decode(data)
                audio = np.frombuffer(audio_bytes, dtype=np.float32)
                if _engine:
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(None, _engine.process_audio, audio)
                    response = response or "Não entendi. Pode repetir?"
                else:
                    response = "Engine não iniciada."

            elif msg_type == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
                continue

            if response:
                await websocket.send_text(json.dumps({"type": "response", "data": response}))

    except WebSocketDisconnect:
        logger.info(f"Cliente desconectado: {websocket.client}")
    except Exception as e:
        logger.error(f"Erro no WebSocket: {e}")
    finally:
        _connections.discard(websocket)


async def broadcast(message: str):
    """Envia mensagem para todos os clientes conectados."""
    disconnected = set()
    for ws in _connections:
        try:
            await ws.send_text(json.dumps({"type": "broadcast", "data": message}))
        except Exception:
            disconnected.add(ws)
    _connections -= disconnected


def start_server(config: dict, engine: "VoiceEngine"):
    """Inicia o servidor em thread separada."""
    import threading
    import uvicorn

    set_engine(engine)

    host = config.get("host", "0.0.0.0")
    port = config.get("port", 8765)
    ssl_certfile = config.get("ssl_certfile") or os.getenv("SSL_CERTFILE")
    ssl_keyfile = config.get("ssl_keyfile") or os.getenv("SSL_KEYFILE")

    local_ip = get_local_ip()
    scheme = "https" if ssl_certfile else "http"
    url = f"{scheme}://{local_ip}:{port}"

    logger.info(f"Servidor remoto iniciando em {url}")

    if config.get("show_qr", True):
        qr = generate_qr(url)
        print("\n" + "="*50)
        print(f"  CONTROLE REMOTO DISPONÍVEL")
        print(f"  Conecte pelo celular: {url}")
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
