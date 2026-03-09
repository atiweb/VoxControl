"""
Internationalization (i18n) module for VoxControl.
Supports: pt (Portuguese), es (Spanish), en (English).
"""

_current_lang = "pt"


def set_language(lang_code: str):
    """Set the current language. Accepts codes like 'pt-BR', 'es-ES', 'en-US'."""
    global _current_lang
    _current_lang = lang_code.split("-")[0].lower()
    if _current_lang not in STRINGS:
        _current_lang = "en"


def get_language() -> str:
    """Get the current language code (2-letter)."""
    return _current_lang


def t(key: str, **kwargs) -> str:
    """Get translated string for the current language."""
    lang_strings = STRINGS.get(_current_lang, STRINGS["en"])
    template = lang_strings.get(key, STRINGS["en"].get(key, key))
    return template.format(**kwargs) if kwargs else template


# ---- Language metadata ----

SUPPORTED_LANGUAGES = ["pt", "es", "en"]

LANGUAGE_NAMES = {
    "pt": "Portugues",
    "es": "Espanol",
    "en": "English",
}

WHISPER_LANG_MAP = {
    "pt": "pt",
    "es": "es",
    "en": "en",
}

# ---- Default wake words per language ----

DEFAULT_WAKE_WORDS = {
    "pt": {
        "word": "computador",
        "aliases": ["computado", "ei computador", "oi computador"],
    },
    "es": {
        "word": "computadora",
        "aliases": ["computador", "oye computadora", "hola computadora"],
    },
    "en": {
        "word": "computer",
        "aliases": ["hey computer", "hi computer", "ok computer"],
    },
}

# ---- TTS voice search patterns per language ----

VOICE_PATTERNS = {
    "pt": {
        "lang_ids": ["pt", "portugu"],
        "female_names": ["female", "woman", "maria", "ana", "lucia", "fernanda"],
    },
    "es": {
        "lang_ids": ["es", "spanish", "espanol"],
        "female_names": ["female", "woman", "elena", "maria", "carmen", "lucia", "sabina"],
    },
    "en": {
        "lang_ids": ["en", "english"],
        "female_names": ["female", "woman", "zira", "hazel", "susan", "jenny"],
    },
}

# Web Speech API language codes
SPEECH_RECOGNITION_LANG = {
    "pt": "pt-BR",
    "es": "es-ES",
    "en": "en-US",
}

# ---- Confirmation/cancel words per language ----

CONFIRM_WORDS = {
    "pt": ["sim", "pode", "confirma", "ok", "isso", "certo", "vai", "execute", "confirmo", "e isso"],
    "es": ["si", "dale", "confirma", "ok", "eso", "correcto", "hazlo", "ejecuta", "confirmo", "adelante"],
    "en": ["yes", "confirm", "ok", "sure", "do it", "go ahead", "correct", "right", "proceed", "yeah"],
}

CANCEL_WORDS = {
    "pt": ["nao", "cancela", "para", "desiste", "errado", "outro", "nevermind"],
    "es": ["no", "cancela", "para", "desiste", "equivocado", "otro", "olvidalo"],
    "en": ["no", "cancel", "stop", "abort", "wrong", "other", "nevermind", "don't"],
}

# ---- Folder aliases per language ----

FOLDER_ALIASES_I18N = {
    "pt": {
        "documentos": "%USERPROFILE%\\Documents",
        "downloads": "%USERPROFILE%\\Downloads",
        "desktop": "%USERPROFILE%\\Desktop",
        "area de trabalho": "%USERPROFILE%\\Desktop",
        "imagens": "%USERPROFILE%\\Pictures",
        "musicas": "%USERPROFILE%\\Music",
        "videos": "%USERPROFILE%\\Videos",
        "disco c": "C:\\",
        "raiz": "C:\\",
    },
    "es": {
        "documentos": "%USERPROFILE%\\Documents",
        "descargas": "%USERPROFILE%\\Downloads",
        "escritorio": "%USERPROFILE%\\Desktop",
        "imagenes": "%USERPROFILE%\\Pictures",
        "musica": "%USERPROFILE%\\Music",
        "videos": "%USERPROFILE%\\Videos",
        "disco c": "C:\\",
        "raiz": "C:\\",
    },
    "en": {
        "documents": "%USERPROFILE%\\Documents",
        "downloads": "%USERPROFILE%\\Downloads",
        "desktop": "%USERPROFILE%\\Desktop",
        "pictures": "%USERPROFILE%\\Pictures",
        "music": "%USERPROFILE%\\Music",
        "videos": "%USERPROFILE%\\Videos",
        "c drive": "C:\\",
        "root": "C:\\",
    },
}

# ---- Offline parser: search and type prefixes per language ----

SEARCH_PREFIXES = {
    "pt": ["pesquisar", "pesquisa", "buscar", "busca", "procurar", "google"],
    "es": ["buscar", "busca", "busqueda", "google", "investigar"],
    "en": ["search for", "look up", "search", "google", "find"],
}

TYPE_PREFIXES = {
    "pt": ["digitar", "digita", "escrever", "escreve", "escreva"],
    "es": ["escribir", "escribe", "escriba", "teclear", "digitar"],
    "en": ["type", "write", "enter text"],
}

# ---- Offline parser rules per language ----

OFFLINE_RULES = {
    "pt": [
        # Sistema
        (["abrir calculadora", "abre calculadora"], "system.open_app", {"app": "calc"}, "Abrindo a calculadora."),
        (["abrir bloco de notas", "abre bloco de notas", "abrir notepad"], "system.open_app", {"app": "notepad"}, "Abrindo o bloco de notas."),
        (["abrir explorador", "abrir pasta", "abrir arquivos"], "system.open_app", {"app": "explorer"}, "Abrindo o explorador de arquivos."),
        (["minimizar", "minimiza"], "system.minimize", {}, "Janela minimizada."),
        (["maximizar", "maximiza"], "system.maximize", {}, "Janela maximizada."),
        (["area de trabalho", "mostrar area de trabalho"], "system.show_desktop", {}, "Mostrando a area de trabalho."),
        (["bloquear tela", "bloquear computador"], "system.lock_screen", {}, "Bloqueando a tela."),
        (["tirar print", "captura de tela", "screenshot"], "system.screenshot", {"region": "full", "save_to_desktop": True}, "Captura de tela realizada."),
        (["aumentar volume"], "system.volume_up", {"amount": 3}, "Volume aumentado."),
        (["diminuir volume", "baixar volume"], "system.volume_down", {"amount": 3}, "Volume diminuido."),
        (["silenciar", "mudo", "mutar"], "system.volume_mute", {}, "Volume silenciado."),
        # Navegador
        (["abrir chrome", "abrir google chrome"], "browser.open", {"browser": "chrome"}, "Abrindo o Chrome."),
        (["abrir edge"], "browser.open", {"browser": "edge"}, "Abrindo o Edge."),
        (["nova aba", "nova guia"], "browser.new_tab", {}, "Nova aba aberta."),
        (["fechar aba", "fechar guia"], "browser.close_tab", {}, "Aba fechada."),
        (["voltar", "pagina anterior"], "browser.go_back", {}, "Voltando."),
        (["avancar", "proxima pagina"], "browser.go_forward", {}, "Avancando."),
        (["recarregar", "atualizar pagina", "f5"], "browser.refresh", {}, "Pagina recarregada."),
        (["rolar para baixo", "descer"], "browser.scroll_down", {"amount": 3}, "Rolando para baixo."),
        (["rolar para cima", "subir"], "browser.scroll_up", {"amount": 3}, "Rolando para cima."),
        # WhatsApp
        (["abrir whatsapp", "whatsapp"], "whatsapp.open", {}, "Abrindo o WhatsApp."),
        # Office
        (["abrir word", "microsoft word"], "system.open_app", {"app": "word"}, "Abrindo o Word."),
        (["abrir excel", "microsoft excel"], "system.open_app", {"app": "excel"}, "Abrindo o Excel."),
        (["abrir powerpoint", "power point"], "system.open_app", {"app": "powerpnt"}, "Abrindo o PowerPoint."),
        (["salvar", "salva"], "keyboard.save", {}, "Salvando."),
        (["desfazer", "ctrl z"], "keyboard.undo", {}, "Acao desfeita."),
        (["refazer", "ctrl y"], "keyboard.redo", {}, "Acao refeita."),
        (["copiar", "copia"], "keyboard.copy", {}, "Copiado."),
        (["colar", "cola"], "keyboard.paste", {}, "Colado."),
        (["recortar", "cortar"], "keyboard.cut", {}, "Recortado."),
        (["selecionar tudo"], "keyboard.select_all", {}, "Tudo selecionado."),
        # Midia
        (["pausar", "parar musica", "play pause"], "media.play_pause", {}, "Play/Pause."),
        (["proxima musica", "proxima faixa"], "media.next", {}, "Proxima musica."),
        (["musica anterior", "faixa anterior"], "media.previous", {}, "Musica anterior."),
    ],
    "es": [
        # Sistema
        (["abrir calculadora", "abre calculadora"], "system.open_app", {"app": "calc"}, "Abriendo la calculadora."),
        (["abrir bloc de notas", "abrir notepad"], "system.open_app", {"app": "notepad"}, "Abriendo el bloc de notas."),
        (["abrir explorador", "abrir carpetas", "abrir archivos"], "system.open_app", {"app": "explorer"}, "Abriendo el explorador de archivos."),
        (["minimizar"], "system.minimize", {}, "Ventana minimizada."),
        (["maximizar"], "system.maximize", {}, "Ventana maximizada."),
        (["escritorio", "mostrar escritorio"], "system.show_desktop", {}, "Mostrando el escritorio."),
        (["bloquear pantalla", "bloquear computadora"], "system.lock_screen", {}, "Bloqueando la pantalla."),
        (["captura de pantalla", "screenshot", "pantallazo"], "system.screenshot", {"region": "full", "save_to_desktop": True}, "Captura de pantalla realizada."),
        (["subir volumen", "aumentar volumen"], "system.volume_up", {"amount": 3}, "Volumen aumentado."),
        (["bajar volumen", "disminuir volumen"], "system.volume_down", {"amount": 3}, "Volumen disminuido."),
        (["silenciar", "mudo", "mutear"], "system.volume_mute", {}, "Volumen silenciado."),
        # Navegador
        (["abrir chrome", "abrir google chrome"], "browser.open", {"browser": "chrome"}, "Abriendo Chrome."),
        (["abrir edge"], "browser.open", {"browser": "edge"}, "Abriendo Edge."),
        (["nueva pestana"], "browser.new_tab", {}, "Nueva pestana abierta."),
        (["cerrar pestana"], "browser.close_tab", {}, "Pestana cerrada."),
        (["volver", "pagina anterior", "atras"], "browser.go_back", {}, "Volviendo."),
        (["avanzar", "siguiente pagina"], "browser.go_forward", {}, "Avanzando."),
        (["recargar", "actualizar pagina"], "browser.refresh", {}, "Pagina recargada."),
        (["bajar", "desplazar abajo"], "browser.scroll_down", {"amount": 3}, "Desplazando hacia abajo."),
        (["subir", "desplazar arriba"], "browser.scroll_up", {"amount": 3}, "Desplazando hacia arriba."),
        # WhatsApp
        (["abrir whatsapp", "whatsapp"], "whatsapp.open", {}, "Abriendo WhatsApp."),
        # Office
        (["abrir word", "microsoft word"], "system.open_app", {"app": "word"}, "Abriendo Word."),
        (["abrir excel", "microsoft excel"], "system.open_app", {"app": "excel"}, "Abriendo Excel."),
        (["abrir powerpoint", "power point"], "system.open_app", {"app": "powerpnt"}, "Abriendo PowerPoint."),
        (["guardar", "salvar"], "keyboard.save", {}, "Guardando."),
        (["deshacer"], "keyboard.undo", {}, "Accion deshecha."),
        (["rehacer"], "keyboard.redo", {}, "Accion rehecha."),
        (["copiar", "copia"], "keyboard.copy", {}, "Copiado."),
        (["pegar"], "keyboard.paste", {}, "Pegado."),
        (["cortar"], "keyboard.cut", {}, "Cortado."),
        (["seleccionar todo"], "keyboard.select_all", {}, "Todo seleccionado."),
        # Media
        (["pausar", "parar musica", "play pause"], "media.play_pause", {}, "Play/Pausa."),
        (["siguiente cancion", "siguiente pista"], "media.next", {}, "Siguiente cancion."),
        (["cancion anterior", "pista anterior"], "media.previous", {}, "Cancion anterior."),
    ],
    "en": [
        # System
        (["open calculator", "calculator"], "system.open_app", {"app": "calc"}, "Opening calculator."),
        (["open notepad", "open text editor", "notepad"], "system.open_app", {"app": "notepad"}, "Opening notepad."),
        (["open explorer", "open file explorer", "open files"], "system.open_app", {"app": "explorer"}, "Opening file explorer."),
        (["minimize", "minimize window"], "system.minimize", {}, "Window minimized."),
        (["maximize", "maximize window"], "system.maximize", {}, "Window maximized."),
        (["show desktop", "desktop"], "system.show_desktop", {}, "Showing desktop."),
        (["lock screen", "lock computer"], "system.lock_screen", {}, "Locking screen."),
        (["take screenshot", "screenshot", "screen capture", "print screen"], "system.screenshot", {"region": "full", "save_to_desktop": True}, "Screenshot taken."),
        (["volume up", "increase volume", "raise volume"], "system.volume_up", {"amount": 3}, "Volume increased."),
        (["volume down", "decrease volume", "lower volume"], "system.volume_down", {"amount": 3}, "Volume decreased."),
        (["mute", "silence", "mute volume"], "system.volume_mute", {}, "Volume muted."),
        # Browser
        (["open chrome", "open google chrome"], "browser.open", {"browser": "chrome"}, "Opening Chrome."),
        (["open edge", "open microsoft edge"], "browser.open", {"browser": "edge"}, "Opening Edge."),
        (["new tab"], "browser.new_tab", {}, "New tab opened."),
        (["close tab"], "browser.close_tab", {}, "Tab closed."),
        (["go back", "back", "previous page"], "browser.go_back", {}, "Going back."),
        (["go forward", "forward", "next page"], "browser.go_forward", {}, "Going forward."),
        (["reload", "refresh", "refresh page"], "browser.refresh", {}, "Page refreshed."),
        (["scroll down"], "browser.scroll_down", {"amount": 3}, "Scrolling down."),
        (["scroll up"], "browser.scroll_up", {"amount": 3}, "Scrolling up."),
        # WhatsApp
        (["open whatsapp", "whatsapp"], "whatsapp.open", {}, "Opening WhatsApp."),
        # Office
        (["open word", "microsoft word"], "system.open_app", {"app": "word"}, "Opening Word."),
        (["open excel", "microsoft excel"], "system.open_app", {"app": "excel"}, "Opening Excel."),
        (["open powerpoint", "power point"], "system.open_app", {"app": "powerpnt"}, "Opening PowerPoint."),
        (["save"], "keyboard.save", {}, "Saving."),
        (["undo"], "keyboard.undo", {}, "Action undone."),
        (["redo"], "keyboard.redo", {}, "Action redone."),
        (["copy"], "keyboard.copy", {}, "Copied."),
        (["paste"], "keyboard.paste", {}, "Pasted."),
        (["cut"], "keyboard.cut", {}, "Cut."),
        (["select all"], "keyboard.select_all", {}, "All selected."),
        # Media
        (["pause", "stop music", "play pause"], "media.play_pause", {}, "Play/Pause."),
        (["next song", "next track"], "media.next", {}, "Next song."),
        (["previous song", "previous track"], "media.previous", {}, "Previous song."),
    ],
}

# ---- All translatable UI strings ----

STRINGS = {
    "pt": {
        # Engine
        "not_sure": "Nao tenho certeza. Quis dizer: {response}? Confirme dizendo 'sim' ou repita o comando.",
        "confirm_prompt": "{response} Confirma?",
        "cancelled": "Tudo bem, comando cancelado.",
        "loading_models": "Carregando modelos...",
        "ready": "Pronto!",
        "shutting_down": "Encerrando...",
        "text_mode_prompt": "Modo texto. Digite um comando (ou 'sair' para encerrar):",
        "hold_f12": "Segure F12 para falar. Ctrl+C para sair.",
        "say_wake_word": "Diga '{wake}' para ativar. Ctrl+C para sair.",
        "exit_words": "sair,exit,quit",
        "ptt_label": "Push-to-Talk: segure F12 para falar",
        "wake_word_label": "Wake word: \"{wake}\"",
        # Remote UI
        "ui_connecting": "Conectando ao computador...",
        "ui_connected": "Conectado ao computador.",
        "ui_disconnected": "Desconectado. Reconectando...",
        "ui_connection_error": "Erro de conexao.",
        "ui_no_connection": "Sem conexao com o computador.",
        "ui_mic_error": "Nao foi possivel acessar o microfone.",
        "ui_hold_to_speak": "Segure o botao para falar",
        "ui_listening": "Ouvindo... solte para enviar",
        "ui_processing": "Processando...",
        "ui_placeholder": "Digite um comando...",
        # Quick commands (data-cmd values)
        "qc_chrome": "abrir chrome",
        "qc_whatsapp": "abrir whatsapp",
        "qc_screenshot": "tirar print",
        "qc_vol_up": "aumentar volume",
        "qc_vol_down": "diminuir volume",
        "qc_minimize": "minimizar",
        "qc_lock": "bloquear tela",
        # Unknown
        "unknown_response": "Nao entendi o comando. Pode repetir?",
        "unknown_response_with_text": "Nao entendi '{text}'. Pode repetir?",
        # Remote server
        "remote_available": "CONTROLE REMOTO DISPONIVEL",
        "remote_connect_msg": "Conecte pelo celular: {url}",
        "engine_not_ready": "Engine nao iniciada.",
        "audio_not_understood": "Nao entendi. Pode repetir?",
        # Dispatcher
        "command_not_understood": "Nao entendi o comando. Pode repetir de outra forma?",
        "done": "Pronto.",
    },
    "es": {
        # Engine
        "not_sure": "No estoy seguro. Quiso decir: {response}? Confirme diciendo 'si' o repita el comando.",
        "confirm_prompt": "{response} Confirma?",
        "cancelled": "Muy bien, comando cancelado.",
        "loading_models": "Cargando modelos...",
        "ready": "Listo!",
        "shutting_down": "Cerrando...",
        "text_mode_prompt": "Modo texto. Escriba un comando (o 'salir' para cerrar):",
        "hold_f12": "Mantenga F12 para hablar. Ctrl+C para salir.",
        "say_wake_word": "Diga '{wake}' para activar. Ctrl+C para salir.",
        "exit_words": "salir,exit,quit",
        "ptt_label": "Push-to-Talk: mantenga F12 para hablar",
        "wake_word_label": "Wake word: \"{wake}\"",
        # Remote UI
        "ui_connecting": "Conectando al computador...",
        "ui_connected": "Conectado al computador.",
        "ui_disconnected": "Desconectado. Reconectando...",
        "ui_connection_error": "Error de conexion.",
        "ui_no_connection": "Sin conexion con el computador.",
        "ui_mic_error": "No se pudo acceder al microfono.",
        "ui_hold_to_speak": "Mantenga el boton para hablar",
        "ui_listening": "Escuchando... suelte para enviar",
        "ui_processing": "Procesando...",
        "ui_placeholder": "Escriba un comando...",
        # Quick commands
        "qc_chrome": "abrir chrome",
        "qc_whatsapp": "abrir whatsapp",
        "qc_screenshot": "captura de pantalla",
        "qc_vol_up": "subir volumen",
        "qc_vol_down": "bajar volumen",
        "qc_minimize": "minimizar",
        "qc_lock": "bloquear pantalla",
        # Unknown
        "unknown_response": "No entendi el comando. Puede repetir?",
        "unknown_response_with_text": "No entendi '{text}'. Puede repetir?",
        # Remote server
        "remote_available": "CONTROL REMOTO DISPONIBLE",
        "remote_connect_msg": "Conecte desde el celular: {url}",
        "engine_not_ready": "Engine no iniciada.",
        "audio_not_understood": "No entendi. Puede repetir?",
        # Dispatcher
        "command_not_understood": "No entendi el comando. Puede repetir de otra forma?",
        "done": "Listo.",
    },
    "en": {
        # Engine
        "not_sure": "I'm not sure. Did you mean: {response}? Confirm by saying 'yes' or repeat the command.",
        "confirm_prompt": "{response} Confirm?",
        "cancelled": "Alright, command cancelled.",
        "loading_models": "Loading models...",
        "ready": "Ready!",
        "shutting_down": "Shutting down...",
        "text_mode_prompt": "Text mode. Type a command (or 'exit' to quit):",
        "hold_f12": "Hold F12 to speak. Ctrl+C to exit.",
        "say_wake_word": "Say '{wake}' to activate. Ctrl+C to exit.",
        "exit_words": "exit,quit,bye",
        "ptt_label": "Push-to-Talk: hold F12 to speak",
        "wake_word_label": "Wake word: \"{wake}\"",
        # Remote UI
        "ui_connecting": "Connecting to computer...",
        "ui_connected": "Connected to computer.",
        "ui_disconnected": "Disconnected. Reconnecting...",
        "ui_connection_error": "Connection error.",
        "ui_no_connection": "No connection to computer.",
        "ui_mic_error": "Could not access microphone.",
        "ui_hold_to_speak": "Hold button to speak",
        "ui_listening": "Listening... release to send",
        "ui_processing": "Processing...",
        "ui_placeholder": "Type a command...",
        # Quick commands
        "qc_chrome": "open chrome",
        "qc_whatsapp": "open whatsapp",
        "qc_screenshot": "take screenshot",
        "qc_vol_up": "volume up",
        "qc_vol_down": "volume down",
        "qc_minimize": "minimize",
        "qc_lock": "lock screen",
        # Unknown
        "unknown_response": "I didn't understand the command. Can you repeat?",
        "unknown_response_with_text": "I didn't understand '{text}'. Can you repeat?",
        # Remote server
        "remote_available": "REMOTE CONTROL AVAILABLE",
        "remote_connect_msg": "Connect from your phone: {url}",
        "engine_not_ready": "Engine not started.",
        "audio_not_understood": "I didn't understand. Can you repeat?",
        # Dispatcher
        "command_not_understood": "I didn't understand the command. Can you try again?",
        "done": "Done.",
    },
}
