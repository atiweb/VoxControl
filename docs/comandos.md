# Command Reference

Complete catalog of all 80+ actions supported by VoxControl.
Each action can be activated by voice in Portuguese, Spanish, or English (via AI) or via offline keyword matching.

Commands can be issued via:
- **Voice** (microphone or push-to-talk)
- **Text input** (CLI `--text` mode, desktop GUI command panel, or mobile app)
- **Remote** (mobile web interface, Flutter app, or REST API)

---

## How It Works

1. You speak a command in your configured language
2. Whisper transcribes speech to text
3. AI (Claude/OpenAI) interprets the intent and maps it to an action
4. The dispatcher executes the action on Windows

Example (English):
```
You say: "search Google for how much does an iPhone cost"
AI interprets: browser.search {query: "how much does an iPhone cost", engine: "google"}
System executes: opens Google with the search
```

Example (Portuguese):
```
You say: "pesquisa no Google quanto custa um iPhone"
AI interprets: browser.search {query: "quanto custa um iPhone", engine: "google"}
```

Example (Spanish):
```
You say: "buscar en Google cuanto cuesta un iPhone"
AI interprets: browser.search {query: "cuanto cuesta un iPhone", engine: "google"}
```

---

## 1. System (system.)

Windows OS control.

| Action | Parameters | Description |
|--------|-----------|-------------|
| `system.open_app` | app: application name | Opens any installed application |
| `system.close_app` | app: name (or null = current window) | Closes application or active window |
| `system.switch_window` | direction: "next" or "prev" / app: name | Alt+Tab or focuses specific app |
| `system.minimize` | -- | Minimizes current window (Win+Down) |
| `system.maximize` | -- | Maximizes current window (Win+Up) |
| `system.restore` | -- | Restores window to original size |
| `system.show_desktop` | -- | Shows desktop (Win+D) |
| `system.lock_screen` | -- | Locks screen (Win+L) |
| `system.shutdown` | -- | Shuts down PC in 30 seconds |
| `system.restart` | -- | Restarts PC in 30 seconds |
| `system.sleep` | -- | Sleep mode |
| `system.screenshot` | region: "full" or "window", save_to_desktop: bool | Screen capture |
| `system.volume_up` | amount: 1-10 | Increases volume |
| `system.volume_down` | amount: 1-10 | Decreases volume |
| `system.volume_mute` | -- | Mutes/unmutes |
| `system.volume_set` | level: 0-100 | Sets absolute volume |
| `system.brightness_up` | -- | Increases brightness |
| `system.brightness_down` | -- | Decreases brightness |
| `system.do_not_disturb` | enabled: true/false | Do not disturb mode |
| `system.task_manager` | -- | Opens Task Manager |
| `system.settings` | page: string (optional) | Opens Windows Settings |
| `system.clipboard_history` | -- | Clipboard history (Win+V) |
| `system.virtual_desktop_new` | -- | Creates new virtual desktop |
| `system.virtual_desktop_switch` | index: number | Switches virtual desktops |

### Recognized Applications

The `system.open_app` action recognizes these names in any language:

| Name (PT / ES / EN) | Executable |
|----------------------|-----------|
| calculadora / calculadora / calculator | calc.exe |
| bloco de notas / bloc de notas / notepad, text editor | notepad.exe |
| explorador / explorador / file explorer | explorer.exe |
| cmd | cmd.exe |
| powershell | powershell.exe |
| word | winword.exe |
| excel | excel.exe |
| powerpoint | powerpnt.exe |
| outlook | outlook.exe |
| teams | ms-teams: |
| zoom | zoom.exe |
| spotify | spotify.exe |
| chrome, google chrome | chrome.exe |
| edge | msedge.exe |
| firefox | firefox.exe |
| discord | discord.exe |
| vscode, visual studio code | code.exe |
| paint | mspaint.exe |
| configuracoes / configuracion / settings | ms-settings: |
| gerenciador de tarefas / administrador de tareas / task manager | taskmgr.exe |
| ferramenta de recorte / recortes / snipping tool | snippingtool.exe |

### Examples by Language

**Portuguese:**
```
"abrir calculadora"
"fechar janela"
"minimizar"
"tirar print da tela"
"aumentar volume"
"bloquear tela"
```

**Spanish:**
```
"abrir calculadora"
"cerrar ventana"
"minimizar"
"captura de pantalla"
"subir volumen"
"bloquear pantalla"
```

**English:**
```
"open calculator"
"close window"
"minimize"
"take screenshot"
"volume up"
"lock screen"
```

---

## 2. Browser (browser.)

Chrome, Edge and Firefox control.

| Action | Parameters | Description |
|--------|-----------|-------------|
| `browser.open` | browser: "chrome", "edge", "firefox" | Opens browser |
| `browser.open_url` | url: web address | Navigates to URL |
| `browser.search` | query: text, engine: "google", "bing", "youtube" | Web search |
| `browser.new_tab` | -- | New tab (Ctrl+T) |
| `browser.close_tab` | -- | Close tab (Ctrl+W) |
| `browser.reopen_tab` | -- | Reopen closed tab (Ctrl+Shift+T) |
| `browser.next_tab` | -- | Next tab (Ctrl+Tab) |
| `browser.prev_tab` | -- | Previous tab (Ctrl+Shift+Tab) |
| `browser.go_back` | -- | Go back (Alt+Left) |
| `browser.go_forward` | -- | Go forward (Alt+Right) |
| `browser.refresh` | -- | Reload (F5) |
| `browser.scroll_up` | amount: int | Scroll up |
| `browser.scroll_down` | amount: int | Scroll down |
| `browser.scroll_top` | -- | Go to top (Ctrl+Home) |
| `browser.scroll_bottom` | -- | Go to bottom (Ctrl+End) |
| `browser.zoom_in` | -- | Zoom in (Ctrl++) |
| `browser.zoom_out` | -- | Zoom out (Ctrl+-) |
| `browser.zoom_reset` | -- | Reset zoom (Ctrl+0) |
| `browser.bookmark` | -- | Add bookmark (Ctrl+D) |
| `browser.find` | text: search text | Find on page (Ctrl+F) |
| `browser.reading_mode` | -- | Reading mode (F9) |
| `browser.download` | -- | Open downloads (Ctrl+J) |
| `browser.fullscreen` | -- | Fullscreen (F11) |
| `browser.history` | -- | History (Ctrl+H) |
| `browser.incognito` | url: address (optional) | Incognito window (Ctrl+Shift+N) |

### Examples

**Portuguese:**
```
"pesquisar no Google previsao do tempo"
"abrir o site da Netflix"
"nova aba"
"fechar aba"
"voltar"
"tela cheia"
```

**Spanish:**
```
"buscar en Google el clima"
"abrir la pagina de Netflix"
"nueva pestana"
"cerrar pestana"
"volver"
"pantalla completa"
```

**English:**
```
"search Google for weather forecast"
"open Netflix website"
"new tab"
"close tab"
"go back"
"fullscreen"
```

---

## 3. WhatsApp (whatsapp.)

WhatsApp Web control (requires WhatsApp Web open in browser).

| Action | Parameters | Description |
|--------|-----------|-------------|
| `whatsapp.open` | -- | Opens web.whatsapp.com |
| `whatsapp.open_chat` | contact: contact name | Opens conversation with contact |
| `whatsapp.send_message` | contact: name, message: text | Sends message |
| `whatsapp.new_group` | -- | Starts creating a new group |
| `whatsapp.search` | query: text | Searches contacts/messages |
| `whatsapp.attach_file` | -- | Opens attachment menu |
| `whatsapp.voice_note` | -- | Starts voice recording |
| `whatsapp.read_last` | contact: name (optional) | Opens last message |
| `whatsapp.mark_read` | -- | Marks conversation as read |
| `whatsapp.archive_chat` | contact: name | Archives conversation |
| `whatsapp.mute_chat` | contact: name, duration: duration | Mutes conversation |

### Examples

**Portuguese:**
```
"abrir WhatsApp"
"abrir chat com a Maria"
"enviar mensagem para o Joao: oi, tudo bem?"
```

**Spanish:**
```
"abrir WhatsApp"
"abrir chat con Maria"
"enviar mensaje a Juan: hola, como estas?"
```

**English:**
```
"open WhatsApp"
"open chat with Maria"
"send message to John: hi, how are you?"
```

---

## 4. Microsoft Word (office.word.)

| Action | Parameters | Description |
|--------|-----------|-------------|
| `office.word.open` | file: path (optional) | Opens Word or document |
| `office.word.new` | -- | New document |
| `office.word.save` | -- | Save (Ctrl+S) |
| `office.word.save_as` | filename: name (optional) | Save As (Ctrl+Shift+S) |
| `office.word.close` | -- | Close document (Ctrl+W) |
| `office.word.print` | -- | Print (Ctrl+P) |
| `office.word.bold` | -- | Bold (Ctrl+B) |
| `office.word.italic` | -- | Italic (Ctrl+I) |
| `office.word.underline` | -- | Underline (Ctrl+U) |
| `office.word.align` | alignment: "left", "center", "right", "justify" | Alignment |
| `office.word.font_size` | size: number | Font size |
| `office.word.heading` | level: 1, 2, or 3 | Heading (Ctrl+Alt+1/2/3) |
| `office.word.bullet_list` | -- | Bullet list |
| `office.word.numbered_list` | -- | Numbered list |
| `office.word.insert_table` | rows: number, cols: number | Insert table |
| `office.word.insert_image` | -- | Opens image insertion dialog |
| `office.word.find_replace` | find: text, replace: text | Find and replace |
| `office.word.spell_check` | -- | Spell check (F7) |
| `office.word.word_count` | -- | Word count |
| `office.word.new_page` | -- | Insert page break (Ctrl+Enter) |

### Examples

```
PT: "abrir Word" / "negrito" / "centralizar texto" / "inserir tabela 3 por 4"
ES: "abrir Word" / "negrita" / "centrar texto" / "insertar tabla 3 por 4"
EN: "open Word" / "bold" / "center text" / "insert 3 by 4 table"
```

---

## 5. Microsoft Excel (office.excel.)

| Action | Parameters | Description |
|--------|-----------|-------------|
| `office.excel.open` | file: path (optional) | Opens Excel or file |
| `office.excel.new` | -- | New spreadsheet |
| `office.excel.save` | -- | Save |
| `office.excel.goto_cell` | cell: reference (e.g., "B5") | Navigate to cell |
| `office.excel.insert_formula` | formula: string | Insert formula |
| `office.excel.auto_sum` | -- | AutoSum (Alt+=) |
| `office.excel.create_chart` | type: "bar", "line", "pie", "column" | Create chart |
| `office.excel.filter` | -- | Toggle filter (Ctrl+Shift+L) |
| `office.excel.sort` | order: "asc" or "desc" | Sort data |
| `office.excel.freeze_panes` | -- | Freeze panes |
| `office.excel.new_sheet` | name: name (optional) | New sheet |
| `office.excel.delete_sheet` | -- | Delete current sheet |
| `office.excel.find_replace` | find: text, replace: text | Find and replace |
| `office.excel.pivot_table` | -- | Insert pivot table |

### Examples

```
PT: "abrir Excel" / "ir para celula B5" / "autoSoma" / "criar grafico de barras"
ES: "abrir Excel" / "ir a celda B5" / "autosuma" / "crear grafico de barras"
EN: "open Excel" / "go to cell B5" / "auto sum" / "create bar chart"
```

---

## 6. Microsoft PowerPoint (office.ppt.)

| Action | Parameters | Description |
|--------|-----------|-------------|
| `office.ppt.open` | file: path (optional) | Opens PowerPoint or file |
| `office.ppt.new` | -- | New presentation |
| `office.ppt.save` | -- | Save |
| `office.ppt.new_slide` | layout: type (optional) | Add slide (Ctrl+M) |
| `office.ppt.delete_slide` | -- | Delete current slide |
| `office.ppt.next_slide` | -- | Next slide (PageDown) |
| `office.ppt.prev_slide` | -- | Previous slide (PageUp) |
| `office.ppt.start_slideshow` | -- | Start slideshow (F5) |
| `office.ppt.end_slideshow` | -- | End slideshow (Esc) |
| `office.ppt.insert_image` | -- | Insert image |
| `office.ppt.duplicate_slide` | -- | Duplicate slide (Ctrl+D) |

### Examples

```
PT: "abrir PowerPoint" / "novo slide" / "iniciar apresentacao" / "proximo slide"
ES: "abrir PowerPoint" / "nueva diapositiva" / "iniciar presentacion" / "siguiente"
EN: "open PowerPoint" / "new slide" / "start slideshow" / "next slide"
```

---

## 7. Files and Folders (files.)

| Action | Parameters | Description |
|--------|-----------|-------------|
| `files.open_explorer` | path: path (optional) | Opens File Explorer |
| `files.open_folder` | path: path or alias | Opens specific folder |
| `files.open_file` | path or name: file name | Opens file |
| `files.new_folder` | name: name, path: where (optional) | Creates folder |
| `files.rename` | name: new name | Renames selected file/folder (F2) |
| `files.delete` | -- | Sends to recycle bin (Delete) |
| `files.copy` | -- | Copy (Ctrl+C) |
| `files.cut` | -- | Cut (Ctrl+X) |
| `files.paste` | -- | Paste (Ctrl+V) |
| `files.search` | query: text, path: where (optional) | Search file |
| `files.compress` | -- | Compress to ZIP |
| `files.extract` | -- | Extract compressed file |
| `files.properties` | -- | Properties (Alt+Enter) |
| `files.sort_by` | field: "name", "date", "size", "type" | Sort files |

### Folder Aliases

You can use friendly names instead of full paths. Aliases are available in all languages:

| Portuguese | Spanish | English | Path |
|-----------|---------|---------|------|
| documentos | documentos | documents | %USERPROFILE%\Documents |
| downloads | descargas | downloads | %USERPROFILE%\Downloads |
| desktop, area de trabalho | escritorio | desktop | %USERPROFILE%\Desktop |
| imagens | imagenes | pictures | %USERPROFILE%\Pictures |
| musicas | musica | music | %USERPROFILE%\Music |
| videos | videos | videos | %USERPROFILE%\Videos |
| disco c, raiz | disco c, raiz | c drive, root | C:\ |

### Examples

**Portuguese:**
```
"abrir pasta downloads"
"abrir meus documentos"
"criar pasta chamada projetos"
```

**Spanish:**
```
"abrir carpeta descargas"
"abrir mis documentos"
"crear carpeta llamada proyectos"
```

**English:**
```
"open downloads folder"
"open my documents"
"create folder called projects"
```

---

## 8. Media (media.)

| Action | Parameters | Description |
|--------|-----------|-------------|
| `media.play_pause` | -- | Toggle play/pause (media key) |
| `media.next` | -- | Next track |
| `media.previous` | -- | Previous track |
| `media.stop` | -- | Stop playback |
| `media.shuffle` | -- | Toggle shuffle mode |
| `media.repeat` | -- | Toggle repeat mode |
| `media.open_spotify` | query: search (optional) | Opens Spotify |
| `media.open_youtube` | query: search (optional) | Opens YouTube |

### Examples

```
PT: "pausar musica" / "proxima faixa" / "abrir Spotify"
ES: "pausar musica" / "siguiente cancion" / "abrir Spotify"
EN: "pause music" / "next track" / "open Spotify"
```

---

## 9. Keyboard and Mouse (keyboard. / mouse.)

### Keyboard

| Action | Parameters | Description |
|--------|-----------|-------------|
| `keyboard.type` | text: text | Types text |
| `keyboard.press` | key: key name | Presses key |
| `keyboard.hotkey` | keys: list of keys | Keyboard shortcut |
| `keyboard.select_all` | -- | Ctrl+A |
| `keyboard.copy` | -- | Ctrl+C |
| `keyboard.paste` | -- | Ctrl+V |
| `keyboard.cut` | -- | Ctrl+X |
| `keyboard.undo` | -- | Ctrl+Z |
| `keyboard.redo` | -- | Ctrl+Y |
| `keyboard.delete` | -- | Delete |
| `keyboard.enter` | -- | Enter |
| `keyboard.escape` | -- | Escape |
| `keyboard.tab` | -- | Tab |
| `keyboard.find` | -- | Ctrl+F |
| `keyboard.save` | -- | Ctrl+S |
| `keyboard.new` | -- | Ctrl+N |
| `keyboard.close` | -- | Ctrl+W |
| `keyboard.zoom_in` | -- | Ctrl++ |
| `keyboard.zoom_out` | -- | Ctrl+- |

### Mouse

| Action | Parameters | Description |
|--------|-----------|-------------|
| `mouse.click` | button: "left"/"right"/"middle", x/y: coords (optional) | Click |
| `mouse.double_click` | x/y: coords (optional) | Double click |
| `mouse.scroll` | direction: "up"/"down"/"left"/"right", amount: int | Scroll |
| `mouse.move` | x: int, y: int | Move cursor |

### Recognized Keys

enter, escape, esc, tab, backspace, delete, home, end, pageup, pagedown,
up, down, left, right, f1 to f12, print screen, windows, win, space

### Recognized Modifiers

ctrl, control, alt, shift, win, windows

### Examples

```
PT: "digitar ola mundo" / "copiar" / "colar" / "desfazer" / "selecionar tudo"
ES: "escribir hola mundo" / "copiar" / "pegar" / "deshacer" / "seleccionar todo"
EN: "type hello world" / "copy" / "paste" / "undo" / "select all"
```

---

## Offline Mode Rules

When no AI API is available, the system uses keyword matching. The following commands work offline, organized by language:

### Portuguese (PT)

**System:**
- "abrir calculadora", "abrir bloco de notas", "abrir explorador"
- "minimizar", "maximizar", "area de trabalho"
- "bloquear tela", "bloquear computador"
- "tirar print", "captura de tela", "screenshot"
- "aumentar volume", "diminuir volume", "baixar volume", "silenciar", "mudo"

**Browser:**
- "abrir chrome", "abrir google chrome", "abrir edge"
- "nova aba", "nova guia", "fechar aba", "fechar guia"
- "voltar", "pagina anterior", "avancar", "proxima pagina"
- "recarregar", "atualizar pagina", "f5"
- "rolar para baixo", "descer", "rolar para cima", "subir"

**Office:**
- "abrir word", "abrir excel", "abrir powerpoint"
- "salvar", "salva", "desfazer", "copiar", "colar", "recortar"
- "selecionar tudo"

**Media:**
- "pausar", "parar musica", "play pause"
- "proxima musica", "proxima faixa"
- "musica anterior", "faixa anterior"

**Search prefixes:** "pesquisar ...", "buscar ...", "procurar ...", "google ..."
**Type prefixes:** "digitar ...", "escrever ...", "escreva ..."

### Spanish (ES)

**System:**
- "abrir calculadora", "abrir bloc de notas", "abrir explorador"
- "minimizar", "maximizar", "escritorio", "mostrar escritorio"
- "bloquear pantalla", "bloquear computadora"
- "captura de pantalla", "screenshot", "pantallazo"
- "subir volumen", "aumentar volumen", "bajar volumen", "silenciar", "mutear"

**Browser:**
- "abrir chrome", "abrir google chrome", "abrir edge"
- "nueva pestana", "cerrar pestana"
- "volver", "pagina anterior", "atras"
- "avanzar", "siguiente pagina"
- "recargar", "actualizar pagina"
- "bajar", "desplazar abajo", "subir", "desplazar arriba"

**Office:**
- "abrir word", "abrir excel", "abrir powerpoint"
- "guardar", "deshacer", "rehacer", "copiar", "pegar", "cortar"
- "seleccionar todo"

**Media:**
- "pausar", "parar musica", "play pause"
- "siguiente cancion", "siguiente pista"
- "cancion anterior", "pista anterior"

**Search prefixes:** "buscar ...", "busqueda ...", "google ...", "investigar ..."
**Type prefixes:** "escribir ...", "escribe ...", "teclear ...", "digitar ..."

### English (EN)

**System:**
- "open calculator", "open notepad", "open text editor", "open file explorer"
- "minimize", "maximize", "show desktop"
- "lock screen", "lock computer"
- "take screenshot", "screenshot", "screen capture", "print screen"
- "volume up", "increase volume", "volume down", "decrease volume", "mute"

**Browser:**
- "open chrome", "open google chrome", "open edge"
- "new tab", "close tab"
- "go back", "back", "previous page"
- "go forward", "forward", "next page"
- "reload", "refresh", "refresh page"
- "scroll down", "scroll up"

**Office:**
- "open word", "open excel", "open powerpoint"
- "save", "undo", "redo", "copy", "paste", "cut"
- "select all"

**Media:**
- "pause", "stop music", "play pause"
- "next song", "next track"
- "previous song", "previous track"

**Search prefixes:** "search for ...", "look up ...", "search ...", "google ...", "find ..."
**Type prefixes:** "type ...", "write ...", "enter text ..."

---

## Language Flag

Use the `--lang` flag to switch language at startup:

```bash
python -m src.main --lang en     # English
python -m src.main --lang es     # Spanish
python -m src.main --lang pt     # Portuguese (default)
```

This automatically adjusts:
- AI system prompt language
- Offline rule matching
- Wake word
- TTS voice selection
- Speech recognition language
- Remote mobile UI language
