"""
Controle do sistema de arquivos e Explorador do Windows.
"""

import logging
import os
import subprocess
import time
from pathlib import Path

import pyautogui

from ..i18n import get_language, FOLDER_ALIASES_I18N

logger = logging.getLogger(__name__)


def _get_folder_aliases() -> dict:
    """Returns folder aliases for all supported languages (merged)."""
    merged = {}
    for lang_aliases in FOLDER_ALIASES_I18N.values():
        merged.update(lang_aliases)
    return merged


class FileControl:
    """Controla arquivos, pastas e o Explorador do Windows."""

    def execute(self, action: str, params: dict) -> str:
        sub = action.replace("files.", "")
        method = getattr(self, f"_{sub.replace('.', '_')}", None)
        if method is None:
            return f"Ação de arquivos desconhecida: {action}"
        try:
            return method(params)
        except Exception as e:
            logger.error(f"Erro em {action}: {e}")
            return f"Erro ao executar {action}: {e}"

    def _resolve_path(self, path: str) -> str:
        """Resolve aliases and environment variables."""
        lower = path.lower()
        aliases = _get_folder_aliases()
        if lower in aliases:
            path = aliases[lower]
        return os.path.expandvars(path)

    def _open_explorer(self, params: dict) -> str:
        path = params.get("path")
        if path:
            resolved = self._resolve_path(path)
            subprocess.Popen(f'explorer "{resolved}"', shell=True)
            return f"Explorador aberto em {resolved}."
        else:
            subprocess.Popen("explorer.exe", shell=True)
            return "Explorador de arquivos aberto."

    def _open_folder(self, params: dict) -> str:
        path = params.get("path", "")
        resolved = self._resolve_path(path)
        subprocess.Popen(f'explorer "{resolved}"', shell=True)
        return f"Pasta '{resolved}' aberta."

    def _open_file(self, params: dict) -> str:
        path = params.get("path")
        name = params.get("name")
        if path:
            resolved = self._resolve_path(path)
            os.startfile(resolved)
            return f"Arquivo '{resolved}' aberto."
        elif name:
            # Pesquisa o arquivo
            pyautogui.hotkey("win", "s")
            time.sleep(0.4)
            pyautogui.write(name, interval=0.05)
            return f"Pesquisando arquivo '{name}'."
        return "Caminho do arquivo não especificado."

    def _new_folder(self, params: dict) -> str:
        name = params.get("name", "Nova Pasta")
        path = params.get("path")
        if path:
            resolved = self._resolve_path(path)
            folder = Path(resolved) / name
            folder.mkdir(parents=True, exist_ok=True)
            return f"Pasta '{name}' criada em '{resolved}'."
        else:
            # Criar no explorador aberto
            pyautogui.hotkey("ctrl", "shift", "n")
            time.sleep(0.4)
            pyautogui.hotkey("ctrl", "a")
            pyautogui.write(name, interval=0.05)
            pyautogui.press("enter")
            return f"Pasta '{name}' criada."

    def _rename(self, params: dict) -> str:
        name = params.get("name", "")
        pyautogui.press("f2")
        time.sleep(0.3)
        pyautogui.hotkey("ctrl", "a")
        if name:
            pyautogui.write(name, interval=0.05)
        return "Renomeando arquivo."

    def _delete(self, params: dict) -> str:
        pyautogui.press("delete")
        return "Arquivo enviado para a lixeira."

    def _copy(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "c")
        return "Copiado."

    def _cut(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "x")
        return "Recortado."

    def _paste(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "v")
        return "Colado."

    def _search(self, params: dict) -> str:
        query = params.get("query", "")
        path = params.get("path")
        if path:
            resolved = self._resolve_path(path)
            subprocess.Popen(f'explorer "search-ms:query={query}&crumb=location:{resolved}"', shell=True)
        else:
            pyautogui.hotkey("win", "s")
            time.sleep(0.4)
            pyautogui.write(query, interval=0.05)
        return f"Pesquisando '{query}'."

    def _compress(self, params: dict) -> str:
        # Clique direito > Comprimir (via menu de contexto)
        pyautogui.hotkey("shift", "f10")
        time.sleep(0.4)
        # Navegar até "Enviar para" > "Pasta compactada"
        pyautogui.press("s")
        return "Menu de compressão aberto."

    def _extract(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "e")
        return "Extração iniciada."

    def _properties(self, params: dict) -> str:
        pyautogui.hotkey("alt", "enter")
        return "Propriedades abertas."

    def _sort_by(self, params: dict) -> str:
        field = params.get("field", "name")
        # Clique direito para menu de ordenação no explorador
        pyautogui.hotkey("shift", "f10")
        time.sleep(0.3)
        pyautogui.press("o")  # "Ordenar por"
        time.sleep(0.3)
        key_map = {"name": "n", "date": "d", "size": "s", "type": "t"}
        pyautogui.press(key_map.get(field, "n"))
        return f"Arquivos ordenados por {field}."
