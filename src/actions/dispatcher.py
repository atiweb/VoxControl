"""
Dispatcher: recebe a intencao interpretada pela IA e executa a acao correta.
"""

import logging
from typing import Optional

from .system_control import SystemControl
from .browser_control import BrowserControl
from .whatsapp_control import WhatsAppControl
from .office_control import OfficeControl
from .file_control import FileControl
from .media_control import MediaControl
from .keyboard_control import KeyboardControl
from ..i18n import t
from ..validation import validate_action

logger = logging.getLogger(__name__)


class ActionDispatcher:
    """Roteia intenções para os handlers corretos."""

    def __init__(self, config: dict):
        self.config = config
        self._system = SystemControl()
        self._browser = BrowserControl(config.get("browser", {}))
        self._whatsapp = WhatsAppControl()
        self._office = OfficeControl()
        self._files = FileControl()
        self._media = MediaControl()
        self._keyboard = KeyboardControl()
        self._custom_commands = self._load_custom_commands(config)

    def _load_custom_commands(self, config: dict) -> list:
        import yaml
        import os
        path = config.get("custom_commands_path", "config/custom_commands.yaml")
        if not os.path.exists(path):
            return []
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data.get("custom_commands", [])
        except Exception as e:
            logger.warning(f"Erro ao carregar comandos personalizados: {e}")
            return []

    def dispatch(self, intent: dict) -> str:
        """
        Executa a ação baseada na intenção interpretada.
        Retorna texto de resposta para o usuário.
        """
        action = intent.get("action", "unknown")
        params = intent.get("params", {})
        response_text = intent.get("response_text", "")

        if action == "unknown":
            return t("command_not_understood")

        # Validate action against whitelist
        if not validate_action(action):
            logger.warning(f"Blocked invalid action: '{action}'")
            return t("command_not_understood")

        # Verificar comandos personalizados primeiro
        custom_result = self._check_custom_command(action, params)
        if custom_result is not None:
            return custom_result

        # Rotear para o handler correto
        try:
            result = self._route(action, params)
            return result or response_text or t("done")
        except Exception as e:
            logger.error(f"Erro ao executar '{action}': {e}", exc_info=True)
            return f"Erro ao executar o comando: {e}"

    def _route(self, action: str, params: dict) -> Optional[str]:
        """Roteia a ação para o handler correto."""
        prefix = action.split(".")[0]

        routes = {
            "system": self._system.execute,
            "browser": self._browser.execute,
            "whatsapp": self._whatsapp.execute,
            "office": self._office.execute,
            "files": self._files.execute,
            "media": self._media.execute,
            "keyboard": self._keyboard.execute,
            "mouse": self._keyboard.execute,
        }

        handler = routes.get(prefix)
        if handler is None:
            logger.warning(f"Nenhum handler para o prefixo: '{prefix}' (ação: '{action}')")
            return f"Ação '{action}' não suportada."

        return handler(action, params)

    def _check_custom_command(self, action: str, params: dict) -> Optional[str]:
        """Verifica se a ação corresponde a um comando personalizado."""
        for cmd in self._custom_commands:
            if cmd.get("action") == action:
                merged_params = {**cmd.get("params", {}), **params}
                return self._route(action, merged_params)
        return None

    def get_available_actions(self) -> list:
        """Lista todas as ações disponíveis."""
        return [
            # Sistema
            "system.open_app", "system.close_app", "system.switch_window",
            "system.minimize", "system.maximize", "system.restore",
            "system.show_desktop", "system.lock_screen", "system.shutdown",
            "system.restart", "system.sleep", "system.screenshot",
            "system.volume_up", "system.volume_down", "system.volume_mute",
            "system.volume_set", "system.brightness_up", "system.brightness_down",
            "system.do_not_disturb", "system.task_manager", "system.settings",
            "system.clipboard_history", "system.virtual_desktop_new",
            "system.virtual_desktop_switch",
            # Navegador
            "browser.open", "browser.open_url", "browser.search",
            "browser.new_tab", "browser.close_tab", "browser.reopen_tab",
            "browser.next_tab", "browser.prev_tab", "browser.go_back",
            "browser.go_forward", "browser.refresh", "browser.scroll_up",
            "browser.scroll_down", "browser.scroll_top", "browser.scroll_bottom",
            "browser.zoom_in", "browser.zoom_out", "browser.zoom_reset",
            "browser.bookmark", "browser.find", "browser.download",
            "browser.fullscreen", "browser.history", "browser.incognito",
            # WhatsApp
            "whatsapp.open", "whatsapp.open_chat", "whatsapp.send_message",
            "whatsapp.search", "whatsapp.attach_file", "whatsapp.voice_note",
            "whatsapp.mark_read", "whatsapp.archive_chat", "whatsapp.mute_chat",
            # Office
            "office.word.open", "office.word.new", "office.word.save",
            "office.word.bold", "office.word.italic", "office.word.underline",
            "office.excel.open", "office.excel.new", "office.excel.save",
            "office.excel.auto_sum", "office.excel.create_chart",
            "office.ppt.open", "office.ppt.new", "office.ppt.save",
            "office.ppt.new_slide", "office.ppt.start_slideshow",
            # Arquivos
            "files.open_explorer", "files.open_folder", "files.open_file",
            "files.new_folder", "files.rename", "files.delete",
            "files.copy", "files.cut", "files.paste", "files.search",
            # Mídia
            "media.play_pause", "media.next", "media.previous", "media.stop",
            "media.open_spotify", "media.open_youtube",
            # Teclado/Mouse
            "keyboard.type", "keyboard.press", "keyboard.hotkey",
            "keyboard.copy", "keyboard.paste", "keyboard.undo", "keyboard.redo",
            "mouse.click", "mouse.double_click", "mouse.scroll",
        ]
