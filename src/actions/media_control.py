"""
Controle de mídia: reprodução, Spotify, YouTube.
"""

import logging
import subprocess
import webbrowser

import pyautogui

logger = logging.getLogger(__name__)


class MediaControl:
    """Controla reprodução de mídia."""

    def execute(self, action: str, params: dict) -> str:
        sub = action.replace("media.", "")
        method = getattr(self, f"_{sub.replace('.', '_')}", None)
        if method is None:
            return f"Ação de mídia desconhecida: {action}"
        try:
            return method(params)
        except Exception as e:
            logger.error(f"Erro em {action}: {e}")
            return f"Erro: {e}"

    def _play_pause(self, params: dict) -> str:
        pyautogui.press("playpause")
        return "Play/Pause."

    def _next(self, params: dict) -> str:
        pyautogui.press("nexttrack")
        return "Próxima faixa."

    def _previous(self, params: dict) -> str:
        pyautogui.press("prevtrack")
        return "Faixa anterior."

    def _stop(self, params: dict) -> str:
        pyautogui.press("stop")
        return "Reprodução parada."

    def _shuffle(self, params: dict) -> str:
        # Ctrl+S no Spotify
        pyautogui.hotkey("ctrl", "s")
        return "Modo aleatório alternado."

    def _repeat(self, params: dict) -> str:
        # Ctrl+R no Spotify
        pyautogui.hotkey("ctrl", "r")
        return "Modo repetição alternado."

    def _open_spotify(self, params: dict) -> str:
        query = params.get("query")
        try:
            if query:
                import urllib.parse
                encoded = urllib.parse.quote(query)
                webbrowser.open(f"spotify:search:{encoded}")
            else:
                subprocess.Popen("spotify.exe", shell=True)
        except Exception:
            webbrowser.open("https://open.spotify.com")
        return f"Spotify aberto{' com busca: ' + query if query else ''}."

    def _open_youtube(self, params: dict) -> str:
        query = params.get("query")
        if query:
            import urllib.parse
            encoded = urllib.parse.quote(query)
            webbrowser.open(f"https://www.youtube.com/results?search_query={encoded}")
            return f"YouTube pesquisando: {query}."
        else:
            webbrowser.open("https://www.youtube.com")
            return "YouTube aberto."
