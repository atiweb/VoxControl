"""
Controle do sistema operacional Windows.
"""

import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

import pyautogui

logger = logging.getLogger(__name__)


class SystemControl:
    """Controla o sistema operacional Windows."""

    APP_MAP = {
        # Common / language-neutral
        "calc": "calc.exe",
        "notepad": "notepad.exe",
        "explorer": "explorer.exe",
        "cmd": "cmd.exe",
        "powershell": "powershell.exe",
        "word": "winword.exe",
        "excel": "excel.exe",
        "powerpoint": "powerpnt.exe",
        "powerpnt": "powerpnt.exe",
        "outlook": "outlook.exe",
        "teams": "ms-teams:",
        "zoom": "zoom.exe",
        "spotify": "spotify.exe",
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",
        "edge": "msedge.exe",
        "firefox": "firefox.exe",
        "discord": "discord.exe",
        "vscode": "code.exe",
        "visual studio code": "code.exe",
        "paint": "mspaint.exe",
        "taskmgr": "taskmgr.exe",
        "regedit": "regedit.exe",
        "snippingtool": "snippingtool.exe",
        "snip": "snippingtool.exe",
        # Portuguese
        "calculadora": "calc.exe",
        "bloco de notas": "notepad.exe",
        "gerenciador de tarefas": "taskmgr.exe",
        # Spanish
        "bloc de notas": "notepad.exe",
        "administrador de tareas": "taskmgr.exe",
        "configuracion": "ms-settings:",
        # English
        "calculator": "calc.exe",
        "text editor": "notepad.exe",
        "file explorer": "explorer.exe",
        "task manager": "taskmgr.exe",
        "settings": "ms-settings:",
        "snipping tool": "snippingtool.exe",
    }

    def execute(self, action: str, params: dict) -> str:
        sub = action.replace("system.", "")
        method = getattr(self, f"_{sub.replace('.', '_')}", None)
        if method is None:
            return f"Ação de sistema desconhecida: {action}"
        try:
            return method(params)
        except Exception as e:
            logger.error(f"Erro em {action}: {e}")
            return f"Erro ao executar {action}: {e}"

    def _open_app(self, params: dict) -> str:
        app = params.get("app", "").lower()
        executable = self.APP_MAP.get(app, app)

        # Tentar via URI scheme (ms-settings:, ms-teams:, etc.)
        if ":" in executable and not executable.endswith(".exe"):
            os.startfile(executable)
            return f"Abrindo {app}."

        # Tentar com subprocess
        try:
            subprocess.Popen(executable, shell=True)
            return f"{app.title()} aberto."
        except Exception:
            # Fallback: pesquisar no menu iniciar via Win+S
            pyautogui.hotkey("win", "s")
            time.sleep(0.4)
            pyautogui.write(app, interval=0.05)
            time.sleep(0.5)
            pyautogui.press("enter")
            return f"Pesquisando {app} no menu iniciar."

    def _close_app(self, params: dict) -> str:
        app = params.get("app")
        if app:
            subprocess.run(f"taskkill /f /im {self.APP_MAP.get(app.lower(), app)}", shell=True, capture_output=True)
            return f"{app} fechado."
        else:
            pyautogui.hotkey("alt", "f4")
            return "Janela fechada."

    def _switch_window(self, params: dict) -> str:
        app = params.get("app")
        direction = params.get("direction", "next")
        if app:
            import pywinauto
            try:
                from pywinauto import Desktop
                wins = [w for w in Desktop(backend="uia").windows() if app.lower() in w.window_text().lower()]
                if wins:
                    wins[0].set_focus()
                    return f"Focado em {app}."
            except Exception:
                pass
        if direction == "prev":
            pyautogui.hotkey("alt", "shift", "tab")
        else:
            pyautogui.hotkey("alt", "tab")
        return "Janela alternada."

    def _minimize(self, params: dict) -> str:
        app = params.get("app")
        if app:
            self._switch_window({"app": app})
        pyautogui.hotkey("win", "down")
        return f"{'%s minimizado.' % app.title() if app else 'Janela minimizada.'}"

    def _maximize(self, params: dict) -> str:
        app = params.get("app")
        if app:
            self._switch_window({"app": app})
        pyautogui.hotkey("win", "up")
        return f"{'%s maximizado.' % app.title() if app else 'Janela maximizada.'}"

    def _restore(self, params: dict) -> str:
        app = params.get("app")
        if app:
            self._switch_window({"app": app})
        pyautogui.hotkey("win", "down")
        return "Janela restaurada."

    def _show_desktop(self, params: dict) -> str:
        pyautogui.hotkey("win", "d")
        return "Área de trabalho exibida."

    def _lock_screen(self, params: dict) -> str:
        pyautogui.hotkey("win", "l")
        return "Tela bloqueada."

    def _shutdown(self, params: dict) -> str:
        subprocess.run("shutdown /s /t 30", shell=True)
        return "Computador será desligado em 30 segundos."

    def _restart(self, params: dict) -> str:
        subprocess.run("shutdown /r /t 30", shell=True)
        return "Computador será reiniciado em 30 segundos."

    def _sleep(self, params: dict) -> str:
        subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
        return "Entrando em modo de suspensão."

    def _screenshot(self, params: dict) -> str:
        region = params.get("region", "full")
        save_to_desktop = params.get("save_to_desktop", True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"

        if save_to_desktop:
            desktop = Path.home() / "Desktop"
            filepath = desktop / filename
        else:
            filepath = Path.cwd() / filename

        if region == "window":
            pyautogui.hotkey("alt", "print screen")
            time.sleep(0.3)
            # Salvar via clipboard
            import subprocess
            pyautogui.hotkey("ctrl", "v")
        else:
            screenshot = pyautogui.screenshot()
            screenshot.save(str(filepath))

        return f"Screenshot salvo em {filepath}."

    def _volume_up(self, params: dict) -> str:
        amount = params.get("amount", 3)
        for _ in range(amount):
            pyautogui.press("volumeup")
        return f"Volume aumentado."

    def _volume_down(self, params: dict) -> str:
        amount = params.get("amount", 3)
        for _ in range(amount):
            pyautogui.press("volumedown")
        return "Volume diminuído."

    def _volume_mute(self, params: dict) -> str:
        pyautogui.press("volumemute")
        return "Volume silenciado."

    def _volume_set(self, params: dict) -> str:
        level = params.get("level", 50)
        # Via PowerShell
        ps_cmd = f"[audio]::Volume = {level / 100.0}"
        subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
        return f"Volume definido para {level}%."

    def _brightness_up(self, params: dict) -> str:
        ps_cmd = "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,[math]::min(100,((Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness + 10)))"
        subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
        return "Brilho aumentado."

    def _brightness_down(self, params: dict) -> str:
        ps_cmd = "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,[math]::max(0,((Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness - 10)))"
        subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
        return "Brilho diminuído."

    def _do_not_disturb(self, params: dict) -> str:
        enabled = params.get("enabled", True)
        # Toggle Focus Assist via PowerShell
        state = 1 if enabled else 0
        ps_cmd = f"Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Notifications\\Settings' -Name 'NOC_GLOBAL_SETTING_ALLOW_TOASTS_ABOVE_LOCK' -Value {state}"
        subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
        status = "ativado" if enabled else "desativado"
        return f"Modo não perturbe {status}."

    def _task_manager(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "shift", "esc")
        return "Gerenciador de tarefas aberto."

    def _settings(self, params: dict) -> str:
        page = params.get("page", "")
        if page:
            os.startfile(f"ms-settings:{page}")
        else:
            pyautogui.hotkey("win", "i")
        return "Configurações abertas."

    def _clipboard_history(self, params: dict) -> str:
        pyautogui.hotkey("win", "v")
        return "Histórico da área de transferência aberto."

    def _virtual_desktop_new(self, params: dict) -> str:
        pyautogui.hotkey("win", "ctrl", "d")
        return "Nova área de trabalho virtual criada."

    def _virtual_desktop_switch(self, params: dict) -> str:
        index = params.get("index", 1)
        # Win + Ctrl + Left/Right para navegar
        pyautogui.hotkey("win", "ctrl", "left")
        return f"Área de trabalho virtual alternada."
