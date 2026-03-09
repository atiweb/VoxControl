"""
Controle de teclado e mouse via pyautogui.
"""

import logging
import time

import pyautogui

logger = logging.getLogger(__name__)

# Mapa de nomes amigáveis para teclas pyautogui
KEY_MAP = {
    "enter": "enter",
    "escape": "escape",
    "esc": "escape",
    "tab": "tab",
    "backspace": "backspace",
    "delete": "delete",
    "home": "home",
    "end": "end",
    "pageup": "pageup",
    "pagedown": "pagedown",
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
    "f1": "f1", "f2": "f2", "f3": "f3", "f4": "f4",
    "f5": "f5", "f6": "f6", "f7": "f7", "f8": "f8",
    "f9": "f9", "f10": "f10", "f11": "f11", "f12": "f12",
    "print screen": "printscreen",
    "windows": "win",
    "win": "win",
    "space": "space",
    "espaço": "space",
}

MODIFIER_MAP = {
    "ctrl": "ctrl",
    "control": "ctrl",
    "controle": "ctrl",
    "alt": "alt",
    "shift": "shift",
    "win": "win",
    "windows": "win",
}


class KeyboardControl:
    """Controla teclado e mouse."""

    def execute(self, action: str, params: dict) -> str:
        # Suporta "keyboard.xxx" e "mouse.xxx"
        if action.startswith("mouse."):
            sub = action.replace("mouse.", "")
            method = getattr(self, f"_mouse_{sub.replace('.', '_')}", None)
        else:
            sub = action.replace("keyboard.", "")
            method = getattr(self, f"_{sub.replace('.', '_')}", None)

        if method is None:
            return f"Ação de teclado/mouse desconhecida: {action}"
        try:
            return method(params)
        except Exception as e:
            logger.error(f"Erro em {action}: {e}")
            return f"Erro: {e}"

    def _type(self, params: dict) -> str:
        text = params.get("text", "")
        if not text:
            return "Texto não especificado."
        pyautogui.write(text, interval=0.03)
        return f"Texto digitado."

    def _press(self, params: dict) -> str:
        key = params.get("key", "").lower()
        mapped = KEY_MAP.get(key, key)
        pyautogui.press(mapped)
        return f"Tecla {key} pressionada."

    def _hotkey(self, params: dict) -> str:
        keys = params.get("keys", [])
        if not keys:
            return "Teclas não especificadas."
        mapped = [MODIFIER_MAP.get(k.lower(), KEY_MAP.get(k.lower(), k.lower())) for k in keys]
        pyautogui.hotkey(*mapped)
        return f"Atalho {'+'.join(keys)} executado."

    def _select_all(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "a")
        return "Tudo selecionado."

    def _copy(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "c")
        return "Copiado."

    def _paste(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "v")
        return "Colado."

    def _cut(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "x")
        return "Recortado."

    def _undo(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "z")
        return "Desfeito."

    def _redo(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "y")
        return "Refeito."

    def _delete(self, params: dict) -> str:
        pyautogui.press("delete")
        return "Deletado."

    def _enter(self, params: dict) -> str:
        pyautogui.press("enter")
        return "Enter pressionado."

    def _escape(self, params: dict) -> str:
        pyautogui.press("escape")
        return "Escape pressionado."

    def _tab(self, params: dict) -> str:
        pyautogui.press("tab")
        return "Tab pressionado."

    def _find(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "f")
        return "Busca aberta."

    def _save(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "s")
        return "Salvo."

    def _new(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "n")
        return "Novo criado."

    def _close(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "w")
        return "Fechado."

    def _zoom_in(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "+")
        return "Zoom aumentado."

    def _zoom_out(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "-")
        return "Zoom diminuído."

    # ------------------------------------------------------------------ MOUSE
    def _mouse_click(self, params: dict) -> str:
        button = params.get("button", "left")
        x = params.get("x")
        y = params.get("y")
        btn_map = {"left": "left", "right": "right", "middle": "middle"}
        btn = btn_map.get(button, "left")
        if x is not None and y is not None:
            pyautogui.click(x, y, button=btn)
        else:
            pyautogui.click(button=btn)
        return f"Clique {button}."

    def _mouse_double_click(self, params: dict) -> str:
        x = params.get("x")
        y = params.get("y")
        if x is not None and y is not None:
            pyautogui.doubleClick(x, y)
        else:
            pyautogui.doubleClick()
        return "Duplo clique."

    def _mouse_scroll(self, params: dict) -> str:
        direction = params.get("direction", "down")
        amount = params.get("amount", 3)
        clicks = amount if direction in ("up", "right") else -amount
        if direction in ("left", "right"):
            pyautogui.hscroll(clicks)
        else:
            pyautogui.scroll(clicks)
        return f"Scroll {direction}."

    def _mouse_move(self, params: dict) -> str:
        x = params.get("x", 0)
        y = params.get("y", 0)
        pyautogui.moveTo(x, y, duration=0.3)
        return f"Mouse movido para ({x}, {y})."
