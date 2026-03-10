"""
Controle do WhatsApp Web via automação do navegador.
"""

import logging
import time
import webbrowser

import pyautogui

logger = logging.getLogger(__name__)

WHATSAPP_URL = "https://web.whatsapp.com"


def _type_unicode(text: str, interval: float = 0.0):
    """Type text supporting Unicode (accented chars, emojis) via clipboard."""
    try:
        import pyperclip
        old = pyperclip.paste()
        pyperclip.copy(text)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.1)
        pyperclip.copy(old)  # restore clipboard
    except ImportError:
        pyautogui.write(text, interval=interval)


class WhatsAppControl:
    """Controla o WhatsApp Web."""

    def execute(self, action: str, params: dict) -> str:
        sub = action.replace("whatsapp.", "")
        method = getattr(self, f"_{sub.replace('.', '_')}", None)
        if method is None:
            return f"Ação WhatsApp desconhecida: {action}"
        try:
            return method(params)
        except Exception as e:
            logger.error(f"Erro em {action}: {e}")
            return f"Erro ao executar {action}: {e}"

    def _open(self, params: dict) -> str:
        webbrowser.open(WHATSAPP_URL)
        return "WhatsApp Web aberto."

    def _open_chat(self, params: dict) -> str:
        contact = params.get("contact", "")
        if not contact:
            return "Nome do contato não especificado."
        webbrowser.open(WHATSAPP_URL)
        time.sleep(3)  # Aguarda o WhatsApp carregar
        # Usa Ctrl+F para pesquisar contato na barra de pesquisa
        self._focus_search()
        time.sleep(0.5)
        _type_unicode(contact)
        time.sleep(1.5)
        pyautogui.press("enter")
        return f"Abrindo conversa com {contact}."

    def _send_message(self, params: dict) -> str:
        contact = params.get("contact")
        message = params.get("message", "")
        if not message:
            return "Mensagem não especificada."

        if contact:
            self._open_chat({"contact": contact})
            time.sleep(1)

        # Foca na caixa de texto e digita
        self._focus_message_box()
        time.sleep(0.3)
        _type_unicode(message)
        time.sleep(0.3)
        pyautogui.press("enter")

        recipient = f"para {contact}" if contact else ""
        return f"Mensagem enviada {recipient}."

    def _new_group(self, params: dict) -> str:
        webbrowser.open(WHATSAPP_URL)
        time.sleep(3)
        # Clicar no ícone de novo chat/grupo
        pyautogui.hotkey("ctrl", "alt", "n")
        return "Criando novo grupo no WhatsApp."

    def _search(self, params: dict) -> str:
        query = params.get("query", "")
        if not query:
            return "Termo de pesquisa não especificado."
        webbrowser.open(WHATSAPP_URL)
        time.sleep(2)
        self._focus_search()
        _type_unicode(query)
        return f"Pesquisando '{query}' no WhatsApp."

    def _attach_file(self, params: dict) -> str:
        # Clica no ícone de anexo (Alt+A no WhatsApp Web)
        self._focus_message_box()
        time.sleep(0.3)
        pyautogui.hotkey("alt", "a")
        return "Menu de anexo aberto."

    def _voice_note(self, params: dict) -> str:
        self._focus_message_box()
        time.sleep(0.3)
        pyautogui.hotkey("alt", "r")
        return "Gravação de mensagem de voz iniciada. Diga 'parar gravação' quando terminar."

    def _read_last(self, params: dict) -> str:
        contact = params.get("contact")
        if contact:
            self._open_chat({"contact": contact})
        return "Abrindo última mensagem."

    def _mark_read(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "alt", "shift", "u")
        return "Conversa marcada como lida."

    def _archive_chat(self, params: dict) -> str:
        contact = params.get("contact", "")
        self._open_chat({"contact": contact})
        time.sleep(0.5)
        pyautogui.hotkey("ctrl", "e")
        return f"Conversa com {contact} arquivada."

    def _mute_chat(self, params: dict) -> str:
        contact = params.get("contact", "")
        self._open_chat({"contact": contact})
        time.sleep(0.5)
        pyautogui.hotkey("ctrl", "m")
        return f"Conversa com {contact} silenciada."

    def _focus_search(self):
        """Foca na barra de pesquisa do WhatsApp Web."""
        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.5)

    def _focus_message_box(self):
        """Tenta focar na caixa de mensagem."""
        # O WhatsApp Web usa a caixa de texto como elemento principal
        # Um clique no centro inferior da janela geralmente funciona
        screen_w, screen_h = pyautogui.size()
        # Área aproximada da caixa de mensagem (parte inferior central)
        pyautogui.click(screen_w // 2, int(screen_h * 0.93))
        time.sleep(0.2)
