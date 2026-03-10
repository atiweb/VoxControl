"""
Window Focus Manager: finds and activates target windows before action execution.

Solves the core problem with voice control: when VoxControl processes a command,
its own GUI window has focus. Without explicit window targeting, hotkeys like
Win+Up (maximize) affect VoxControl instead of the intended window.

Strategy: focus-first, then act.
"""

import logging
import time
from typing import Optional

import pyautogui

logger = logging.getLogger(__name__)

# Map of common app names to window title patterns
_WINDOW_PATTERNS = {
    "chrome": ["Google Chrome"],
    "google chrome": ["Google Chrome"],
    "edge": ["Microsoft Edge", "Edge"],
    "firefox": ["Mozilla Firefox", "Firefox"],
    "word": ["Word", "Document"],
    "excel": ["Excel"],
    "powerpoint": ["PowerPoint"],
    "powerpnt": ["PowerPoint"],
    "outlook": ["Outlook"],
    "explorer": ["File Explorer", "Explorador de Arquivos", "Explorador"],
    "notepad": ["Notepad", "Bloco de notas", "Bloc de notas"],
    "calc": ["Calculator", "Calculadora"],
    "spotify": ["Spotify"],
    "discord": ["Discord"],
    "vscode": ["Visual Studio Code"],
    "visual studio code": ["Visual Studio Code"],
    "teams": ["Teams", "Microsoft Teams"],
    "whatsapp": ["WhatsApp"],
    "cmd": ["Command Prompt", "Prompt de Comando", "cmd.exe"],
    "powershell": ["PowerShell"],
    "taskmgr": ["Task Manager", "Gerenciador de Tarefas"],
}

# Actions that should NOT trigger focus switching
# (they operate on the system level, not on a specific window)
_SYSTEM_WIDE_ACTIONS = {
    "system.open_app", "system.show_desktop", "system.lock_screen",
    "system.shutdown", "system.restart", "system.sleep",
    "system.screenshot", "system.volume_up", "system.volume_down",
    "system.volume_mute", "system.volume_set", "system.brightness_up",
    "system.brightness_down", "system.do_not_disturb", "system.task_manager",
    "system.settings", "system.clipboard_history",
    "system.virtual_desktop_new", "system.virtual_desktop_switch",
    "browser.open", "browser.open_url", "browser.search",
    "whatsapp.open", "media.open_spotify", "media.open_youtube",
}


def find_and_focus(target_app: Optional[str], action: str) -> bool:
    """
    Find a window matching target_app and bring it to the foreground.

    Returns True if a window was found and focused, False otherwise.
    Skips focus switching for system-wide actions (volume, screenshot, etc.).
    """
    if not target_app:
        return False

    if action in _SYSTEM_WIDE_ACTIONS:
        return False

    target_app = target_app.lower().strip()

    # Get title patterns for this app
    patterns = _WINDOW_PATTERNS.get(target_app, [target_app])

    try:
        from pywinauto import Desktop
        desktop = Desktop(backend="uia")
        all_windows = desktop.windows()

        for pattern in patterns:
            pattern_lower = pattern.lower()
            for win in all_windows:
                try:
                    title = win.window_text().lower()
                    if pattern_lower in title and title:
                        win.set_focus()
                        time.sleep(0.15)  # Let Windows complete the focus switch
                        logger.info(f"Focused window: '{win.window_text()}' (target: {target_app})")
                        return True
                except Exception:
                    continue

        logger.debug(f"No window found for target_app='{target_app}'")
        return False

    except ImportError:
        logger.warning("pywinauto not installed — cannot focus windows")
        return False
    except Exception as e:
        logger.debug(f"Focus manager error: {e}")
        return False


def infer_target_from_action(action: str, params: dict) -> Optional[str]:
    """
    Infer the target app from the action and params when AI doesn't provide one.

    For browser.* actions → infer 'chrome' (or whatever default browser is).
    For office.word.* → infer 'word'.
    For system.minimize/maximize with an app param → use that app.
    """
    # Already has explicit target
    if params.get("target_app"):
        return params["target_app"]

    # Browser actions target the browser
    if action.startswith("browser.") and action not in _SYSTEM_WIDE_ACTIONS:
        return params.get("browser", "chrome")

    # Office actions target the office app
    if action.startswith("office.word"):
        return "word"
    if action.startswith("office.excel"):
        return "excel"
    if action.startswith("office.ppt"):
        return "powerpoint"

    # WhatsApp actions
    if action.startswith("whatsapp.") and action != "whatsapp.open":
        return "whatsapp"

    # System actions with app param (e.g., "minimize chrome")
    if action in ("system.minimize", "system.maximize", "system.restore",
                   "system.close_app", "system.switch_window"):
        return params.get("app")

    return None
