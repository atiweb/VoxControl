"""
Controle de navegadores: Chrome, Edge, Firefox.
Usa pyautogui para interação via teclado/mouse.
"""

import logging
import subprocess
import time

import pyautogui

logger = logging.getLogger(__name__)


class BrowserControl:
    """Controla navegadores web."""

    BROWSER_EXECUTABLES = {
        "chrome": ["chrome.exe", r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                   r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"],
        "edge": ["msedge.exe", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"],
        "firefox": ["firefox.exe", r"C:\Program Files\Mozilla Firefox\firefox.exe",
                    r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"],
    }

    SEARCH_ENGINES = {
        "google": "https://www.google.com/search?q=",
        "bing": "https://www.bing.com/search?q=",
        "youtube": "https://www.youtube.com/results?search_query=",
        "duckduckgo": "https://duckduckgo.com/?q=",
    }

    def __init__(self, config: dict):
        self.config = config
        self.default_browser = config.get("default", "chrome")

    def execute(self, action: str, params: dict) -> str:
        sub = action.replace("browser.", "")
        method = getattr(self, f"_{sub.replace('.', '_')}", None)
        if method is None:
            return f"Ação de navegador desconhecida: {action}"
        try:
            return method(params)
        except Exception as e:
            logger.error(f"Erro em {action}: {e}")
            return f"Erro ao executar {action}: {e}"

    def _open(self, params: dict) -> str:
        browser = params.get("browser") or self.default_browser
        executables = self.BROWSER_EXECUTABLES.get(browser, [f"{browser}.exe"])
        for exe in executables:
            try:
                subprocess.Popen(exe)
                return f"{browser.title()} aberto."
            except FileNotFoundError:
                continue
        # Fallback via shell
        subprocess.Popen(executables[0], shell=True)
        return f"Abrindo {browser}."

    def _open_url(self, params: dict) -> str:
        url = params.get("url", "")
        if not url:
            return "URL não especificada."
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        import webbrowser
        webbrowser.open(url)
        return f"Abrindo {url}."

    def _search(self, params: dict) -> str:
        query = params.get("query", "")
        engine = params.get("engine", "google") or "google"
        if not query:
            return "Termo de pesquisa não especificado."
        base_url = self.SEARCH_ENGINES.get(engine, self.SEARCH_ENGINES["google"])
        import urllib.parse
        url = base_url + urllib.parse.quote(query)
        import webbrowser
        webbrowser.open(url)
        return f"Pesquisando '{query}' no {engine.title()}."

    def _new_tab(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "t")
        return "Nova aba aberta."

    def _close_tab(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "w")
        return "Aba fechada."

    def _reopen_tab(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "shift", "t")
        return "Aba reaberta."

    def _next_tab(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "tab")
        return "Próxima aba."

    def _prev_tab(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "shift", "tab")
        return "Aba anterior."

    def _go_back(self, params: dict) -> str:
        pyautogui.hotkey("alt", "left")
        return "Voltando."

    def _go_forward(self, params: dict) -> str:
        pyautogui.hotkey("alt", "right")
        return "Avançando."

    def _refresh(self, params: dict) -> str:
        pyautogui.press("f5")
        return "Página recarregada."

    def _scroll_up(self, params: dict) -> str:
        amount = params.get("amount", 3)
        pyautogui.scroll(amount * 100)
        return "Rolando para cima."

    def _scroll_down(self, params: dict) -> str:
        amount = params.get("amount", 3)
        pyautogui.scroll(-amount * 100)
        return "Rolando para baixo."

    def _scroll_top(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "home")
        return "Topo da página."

    def _scroll_bottom(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "end")
        return "Final da página."

    def _zoom_in(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "+")
        return "Zoom aumentado."

    def _zoom_out(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "-")
        return "Zoom diminuído."

    def _zoom_reset(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "0")
        return "Zoom redefinido."

    def _bookmark(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "d")
        time.sleep(0.3)
        pyautogui.press("enter")
        return "Página adicionada aos favoritos."

    def _find(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "f")
        text = params.get("text", "")
        if text:
            time.sleep(0.3)
            pyautogui.write(text, interval=0.05)
        return f"Buscando '{text}' na página."

    def _reading_mode(self, params: dict) -> str:
        pyautogui.press("f9")  # Edge reader mode
        return "Modo leitura ativado."

    def _download(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "j")
        return "Downloads abertos."

    def _fullscreen(self, params: dict) -> str:
        pyautogui.press("f11")
        return "Tela cheia alternada."

    def _history(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "h")
        return "Histórico aberto."

    def _incognito(self, params: dict) -> str:
        url = params.get("url")
        # Chrome/Edge: Ctrl+Shift+N  | Firefox: Ctrl+Shift+P
        pyautogui.hotkey("ctrl", "shift", "n")
        if url:
            time.sleep(0.8)
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            pyautogui.hotkey("ctrl", "l")
            time.sleep(0.3)
            pyautogui.write(url, interval=0.03)
            pyautogui.press("enter")
        return "Janela anônima aberta."
