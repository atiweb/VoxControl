# -*- mode: python ; coding: utf-8 -*-
"""
VoxControl -- PyInstaller spec file.

Builds a single-folder distribution (--onedir) for performance.
User data (config, logs, models) lives in %APPDATA%/VoxControl.

Build:
  pip install pyinstaller
  pyinstaller VoxControl.spec
"""

import os
import sys
from pathlib import Path

block_cipher = None

# ── Project root (use cwd — build.py sets this to the project dir) ──
ROOT = os.getcwd()

# ── Analysis ────────────────────────────────────────────────────────
a = Analysis(
    [os.path.join(ROOT, "VoxControl.pyw")],
    pathex=[ROOT],
    binaries=[],
    datas=[
        # Bundle default config files (copied to %APPDATA% on first run)
        (os.path.join(ROOT, "config", "settings.yaml"), "config"),
        (os.path.join(ROOT, "config", "custom_commands.yaml"), "config"),
        # Bundle remote web interface
        (os.path.join(ROOT, "src", "remote", "static"), os.path.join("src", "remote", "static")),
    ],
    hiddenimports=[
        # customtkinter needs these
        "customtkinter",
        "darkdetect",
        # Audio
        "sounddevice",
        "numpy",
        # faster-whisper pulls in ctranslate2
        "faster_whisper",
        "ctranslate2",
        # pyttsx3 backends
        "pyttsx3.drivers",
        "pyttsx3.drivers.sapi5",
        # Windows automation
        "pyautogui",
        "pywinauto",
        "pynput",
        "pynput.keyboard._win32",
        "pynput.mouse._win32",
        "win32com.client",
        "win32api",
        "win32gui",
        "comtypes",
        "comtypes.client",
        # API clients
        "anthropic",
        "openai",
        "httpx",
        # Server
        "fastapi",
        "uvicorn",
        "uvicorn.logging",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "websockets",
        "starlette",
        "starlette.routing",
        "starlette.responses",
        "anyio",
        "anyio._backends",
        "anyio._backends._asyncio",
        # Config
        "yaml",
        "dotenv",
        # System tray
        "pystray",
        "pystray._win32",
        "PIL",
        "PIL.Image",
        "PIL.ImageDraw",
        # QR code
        "qrcode",
        # Utils
        "psutil",
        "colorama",
        "rich",
        "click",
        # Vosk (optional, may not be installed)
        # "vosk",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude test / dev dependencies
        "pytest",
        "httpx",  # only used for tests
        "unittest",
        # Reduce size
        "tkinter.test",
        "lib2to3",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# ── PYZ (bytecode archive) ─────────────────────────────────────────
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ── EXE ─────────────────────────────────────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    [],                     # Don't bundle into a single file (onedir)
    exclude_binaries=True,
    name="VoxControl",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # No console window (windowed app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(ROOT, "assets", "icon.ico") if os.path.exists(os.path.join(ROOT, "assets", "icon.ico")) else None,
)

# ── COLLECT (onedir folder) ────────────────────────────────────────
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="VoxControl",
)
