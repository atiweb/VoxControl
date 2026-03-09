# Referencia de Comandos

Catalogo completo de todas as 80+ acoes suportadas pelo VoxControl.
Cada acao pode ser ativada por voz em portugues (via IA) ou por correspondencia offline.

---

## Como funciona

1. Voce fala um comando em portugues
2. O Whisper transcreve a fala para texto
3. A IA (Claude/OpenAI) interpreta a intencao e mapeia para uma acao
4. O dispatcher executa a acao no Windows

Exemplo:
```
Voce diz: "pesquisa no Google quanto custa um iPhone"
IA interpreta: browser.search {query: "quanto custa um iPhone", engine: "google"}
Sistema executa: abre o Google com a pesquisa
```

---

## 1. Sistema (system.)

Controle do sistema operacional Windows.

| Acao | Parametros | O que faz |
|------|-----------|-----------|
| `system.open_app` | app: nome do aplicativo | Abre qualquer aplicativo instalado |
| `system.close_app` | app: nome (ou null = janela atual) | Fecha aplicativo ou janela ativa |
| `system.switch_window` | direction: "next" ou "prev" / app: nome | Alt+Tab ou foca em app especifico |
| `system.minimize` | -- | Minimiza janela atual (Win+Down) |
| `system.maximize` | -- | Maximiza janela atual (Win+Up) |
| `system.restore` | -- | Restaura janela ao tamanho original |
| `system.show_desktop` | -- | Mostra area de trabalho (Win+D) |
| `system.lock_screen` | -- | Bloqueia a tela (Win+L) |
| `system.shutdown` | -- | Desliga o PC em 30 segundos |
| `system.restart` | -- | Reinicia o PC em 30 segundos |
| `system.sleep` | -- | Modo de suspensao |
| `system.screenshot` | region: "full" ou "window", save_to_desktop: bool | Captura de tela |
| `system.volume_up` | amount: 1-10 | Aumenta volume |
| `system.volume_down` | amount: 1-10 | Diminui volume |
| `system.volume_mute` | -- | Silencia/dessilencia |
| `system.volume_set` | level: 0-100 | Define volume absoluto |
| `system.brightness_up` | -- | Aumenta brilho da tela |
| `system.brightness_down` | -- | Diminui brilho da tela |
| `system.do_not_disturb` | enabled: true/false | Modo nao perturbe |
| `system.task_manager` | -- | Abre Gerenciador de Tarefas |
| `system.settings` | page: string (opcional) | Abre Configuracoes do Windows |
| `system.clipboard_history` | -- | Historico da area de transferencia (Win+V) |
| `system.virtual_desktop_new` | -- | Cria nova area de trabalho virtual |
| `system.virtual_desktop_switch` | index: numero | Alterna entre areas virtuais |

### Aplicativos reconhecidos

O `system.open_app` reconhece estes nomes:

| Nome falado | Executavel |
|-------------|-----------|
| calculadora, calc | calc.exe |
| notepad, bloco de notas | notepad.exe |
| explorer | explorer.exe |
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

### Exemplos de uso

```
"abrir calculadora"
"fechar janela"
"alternar janela" ou "trocar janela"
"minimizar"
"tirar print da tela"
"aumentar volume"
"silenciar"
"bloquear tela"
"mostrar area de trabalho"
"abrir configuracoes"
"desligar computador" (pede confirmacao)
```

---

## 2. Navegador (browser.)

Controle de Chrome, Edge e Firefox.

| Acao | Parametros | O que faz |
|------|-----------|-----------|
| `browser.open` | browser: "chrome", "edge", "firefox" | Abre navegador |
| `browser.open_url` | url: endereco web | Navega para URL |
| `browser.search` | query: texto, engine: "google", "bing", "youtube" | Pesquisa web |
| `browser.new_tab` | -- | Nova aba (Ctrl+T) |
| `browser.close_tab` | -- | Fecha aba (Ctrl+W) |
| `browser.reopen_tab` | -- | Reabre aba fechada (Ctrl+Shift+T) |
| `browser.next_tab` | -- | Proxima aba (Ctrl+Tab) |
| `browser.prev_tab` | -- | Aba anterior (Ctrl+Shift+Tab) |
| `browser.go_back` | -- | Voltar (Alt+Left) |
| `browser.go_forward` | -- | Avancar (Alt+Right) |
| `browser.refresh` | -- | Recarregar (F5) |
| `browser.scroll_up` | amount: int | Rolar para cima |
| `browser.scroll_down` | amount: int | Rolar para baixo |
| `browser.scroll_top` | -- | Ir ao topo (Ctrl+Home) |
| `browser.scroll_bottom` | -- | Ir ao final (Ctrl+End) |
| `browser.zoom_in` | -- | Aumentar zoom (Ctrl++) |
| `browser.zoom_out` | -- | Diminuir zoom (Ctrl+-) |
| `browser.zoom_reset` | -- | Resetar zoom (Ctrl+0) |
| `browser.bookmark` | -- | Adicionar favorito (Ctrl+D) |
| `browser.find` | text: texto para buscar | Buscar na pagina (Ctrl+F) |
| `browser.reading_mode` | -- | Modo leitura (F9) |
| `browser.download` | -- | Abrir downloads (Ctrl+J) |
| `browser.fullscreen` | -- | Tela cheia (F11) |
| `browser.history` | -- | Historico (Ctrl+H) |
| `browser.incognito` | url: endereco (opcional) | Janela anonima (Ctrl+Shift+N) |

### Exemplos

```
"pesquisar no Google previsao do tempo"
"pesquisar no YouTube tutoriais de Python"
"abrir o site da Netflix"
"nova aba"
"fechar aba"
"voltar"
"rolar para baixo"
"tela cheia"
"buscar 'preco' nesta pagina"
"abrir janela anonima"
```

---

## 3. WhatsApp (whatsapp.)

Controle do WhatsApp Web (requer WhatsApp Web aberto no navegador).

| Acao | Parametros | O que faz |
|------|-----------|-----------|
| `whatsapp.open` | -- | Abre web.whatsapp.com |
| `whatsapp.open_chat` | contact: nome do contato | Abre conversa com contato |
| `whatsapp.send_message` | contact: nome, message: texto | Envia mensagem |
| `whatsapp.new_group` | -- | Inicia criacao de novo grupo |
| `whatsapp.search` | query: texto | Pesquisa contatos/mensagens |
| `whatsapp.attach_file` | -- | Abre menu de anexo |
| `whatsapp.voice_note` | -- | Inicia gravacao de audio |
| `whatsapp.read_last` | contact: nome (opcional) | Abre ultima mensagem |
| `whatsapp.mark_read` | -- | Marca conversa como lida |
| `whatsapp.archive_chat` | contact: nome | Arquiva conversa |
| `whatsapp.mute_chat` | contact: nome, duration: duracao | Silencia conversa |

### Exemplos

```
"abrir WhatsApp"
"abrir chat com a Maria"
"enviar mensagem para o Joao: oi, tudo bem?"
"pesquisar Carlos no WhatsApp"
"mandar audio" (inicia gravacao de voz)
"arquivar conversa com Pedro"
```

---

## 4. Microsoft Word (office.word.)

| Acao | Parametros | O que faz |
|------|-----------|-----------|
| `office.word.open` | file: caminho (opcional) | Abre Word ou documento |
| `office.word.new` | -- | Novo documento |
| `office.word.save` | -- | Salvar (Ctrl+S) |
| `office.word.save_as` | filename: nome (opcional) | Salvar Como (Ctrl+Shift+S) |
| `office.word.close` | -- | Fechar documento (Ctrl+W) |
| `office.word.print` | -- | Imprimir (Ctrl+P) |
| `office.word.bold` | -- | Negrito (Ctrl+B) |
| `office.word.italic` | -- | Italico (Ctrl+I) |
| `office.word.underline` | -- | Sublinhado (Ctrl+U) |
| `office.word.align` | alignment: "left", "center", "right", "justify" | Alinhamento |
| `office.word.font_size` | size: numero | Tamanho da fonte |
| `office.word.heading` | level: 1, 2 ou 3 | Titulo (Ctrl+Alt+1/2/3) |
| `office.word.bullet_list` | -- | Lista com marcadores |
| `office.word.numbered_list` | -- | Lista numerada |
| `office.word.insert_table` | rows: numero, cols: numero | Insere tabela |
| `office.word.insert_image` | -- | Abre dialogo de insercao de imagem |
| `office.word.find_replace` | find: texto, replace: texto | Localizar e substituir |
| `office.word.spell_check` | -- | Verificacao ortografica (F7) |
| `office.word.word_count` | -- | Contagem de palavras |
| `office.word.new_page` | -- | Insere quebra de pagina (Ctrl+Enter) |

### Exemplos

```
"abrir Word"
"novo documento"
"negrito"
"centralizar texto"
"tamanho da fonte 14"
"titulo nivel 2"
"inserir tabela 3 por 4"
"verificar ortografia"
"salvar documento"
"nova pagina"
```

---

## 5. Microsoft Excel (office.excel.)

| Acao | Parametros | O que faz |
|------|-----------|-----------|
| `office.excel.open` | file: caminho (opcional) | Abre Excel ou arquivo |
| `office.excel.new` | -- | Nova planilha |
| `office.excel.save` | -- | Salvar |
| `office.excel.goto_cell` | cell: referencia (ex: "B5") | Navega para celula |
| `office.excel.insert_formula` | formula: string | Insere formula |
| `office.excel.auto_sum` | -- | AutoSoma (Alt+=) |
| `office.excel.create_chart` | type: "bar", "line", "pie", "column" | Cria grafico |
| `office.excel.filter` | -- | Alterna filtro (Ctrl+Shift+L) |
| `office.excel.sort` | order: "asc" ou "desc" | Ordena dados |
| `office.excel.freeze_panes` | -- | Congela paineis |
| `office.excel.new_sheet` | name: nome (opcional) | Nova aba/planilha |
| `office.excel.delete_sheet` | -- | Exclui aba atual |
| `office.excel.find_replace` | find: texto, replace: texto | Localizar e substituir |
| `office.excel.pivot_table` | -- | Insere tabela dinamica |

### Exemplos

```
"abrir Excel"
"ir para celula B5"
"autoSoma"
"criar grafico de barras"
"filtrar dados"
"ordenar crescente"
"congelar paineis"
"nova planilha chamada Vendas"
"tabela dinamica"
```

---

## 6. Microsoft PowerPoint (office.ppt.)

| Acao | Parametros | O que faz |
|------|-----------|-----------|
| `office.ppt.open` | file: caminho (opcional) | Abre PowerPoint ou arquivo |
| `office.ppt.new` | -- | Nova apresentacao |
| `office.ppt.save` | -- | Salvar |
| `office.ppt.new_slide` | layout: tipo (opcional) | Adiciona slide (Ctrl+M) |
| `office.ppt.delete_slide` | -- | Exclui slide atual |
| `office.ppt.next_slide` | -- | Proximo slide (PageDown) |
| `office.ppt.prev_slide` | -- | Slide anterior (PageUp) |
| `office.ppt.start_slideshow` | -- | Inicia apresentacao (F5) |
| `office.ppt.end_slideshow` | -- | Encerra apresentacao (Esc) |
| `office.ppt.insert_image` | -- | Inserir imagem |
| `office.ppt.duplicate_slide` | -- | Duplica slide (Ctrl+D) |

### Exemplos

```
"abrir PowerPoint"
"novo slide"
"iniciar apresentacao"
"proximo slide"
"slide anterior"
"encerrar apresentacao"
"duplicar slide"
```

---

## 7. Arquivos e Pastas (files.)

| Acao | Parametros | O que faz |
|------|-----------|-----------|
| `files.open_explorer` | path: caminho (opcional) | Abre Explorador de Arquivos |
| `files.open_folder` | path: caminho ou alias | Abre pasta especifica |
| `files.open_file` | path ou name: nome do arquivo | Abre arquivo |
| `files.new_folder` | name: nome, path: onde (opcional) | Cria pasta |
| `files.rename` | name: novo nome | Renomeia arquivo/pasta selecionado (F2) |
| `files.delete` | -- | Envia para lixeira (Delete) |
| `files.copy` | -- | Copiar (Ctrl+C) |
| `files.cut` | -- | Recortar (Ctrl+X) |
| `files.paste` | -- | Colar (Ctrl+V) |
| `files.search` | query: texto, path: onde (opcional) | Pesquisa arquivo |
| `files.compress` | -- | Compactar em ZIP |
| `files.extract` | -- | Extrair arquivo compactado |
| `files.properties` | -- | Propriedades (Alt+Enter) |
| `files.sort_by` | field: "name", "date", "size", "type" | Ordena arquivos |

### Aliases de pastas

Voce pode usar nomes amigaveis ao inves de caminhos completos:

| Nome | Caminho real |
|------|-------------|
| documentos | %USERPROFILE%\Documents |
| downloads | %USERPROFILE%\Downloads |
| desktop, area de trabalho | %USERPROFILE%\Desktop |
| imagens | %USERPROFILE%\Pictures |
| musicas | %USERPROFILE%\Music |
| videos | %USERPROFILE%\Videos |
| disco c, raiz | C:\ |

### Exemplos

```
"abrir pasta downloads"
"abrir meus documentos"
"criar pasta chamada projetos"
"pesquisar relatorio"
"renomear para novo-nome"
"ordenar por data"
```

---

## 8. Midia (media.)

| Acao | Parametros | O que faz |
|------|-----------|-----------|
| `media.play_pause` | -- | Alterna play/pausa (tecla de midia) |
| `media.next` | -- | Proxima faixa |
| `media.previous` | -- | Faixa anterior |
| `media.stop` | -- | Para reproducao |
| `media.shuffle` | -- | Alterna modo aleatorio |
| `media.repeat` | -- | Alterna modo repeticao |
| `media.open_spotify` | query: busca (opcional) | Abre Spotify |
| `media.open_youtube` | query: busca (opcional) | Abre YouTube |

### Exemplos

```
"pausar musica"
"proxima faixa"
"abrir Spotify"
"abrir Spotify com rock brasileiro"
"abrir YouTube"
"pesquisar no YouTube lo-fi beats"
```

---

## 9. Teclado e Mouse (keyboard. / mouse.)

### Teclado

| Acao | Parametros | O que faz |
|------|-----------|-----------|
| `keyboard.type` | text: texto | Digita texto |
| `keyboard.press` | key: nome da tecla | Pressiona tecla |
| `keyboard.hotkey` | keys: lista de teclas | Atalho de teclado |
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

| Acao | Parametros | O que faz |
|------|-----------|-----------|
| `mouse.click` | button: "left"/"right"/"middle", x/y: coordenadas (opcional) | Clique |
| `mouse.double_click` | x/y: coordenadas (opcional) | Duplo clique |
| `mouse.scroll` | direction: "up"/"down"/"left"/"right", amount: int | Rolar |
| `mouse.move` | x: int, y: int | Mover cursor |

### Teclas reconhecidas

enter, escape, esc, tab, backspace, delete, home, end, pageup, pagedown,
up, down, left, right, f1 a f12, print screen, windows, win, space, espaco

### Modificadores reconhecidos

ctrl, control, controle, alt, shift, win, windows

### Exemplos

```
"digitar ola mundo"
"copiar"
"colar"
"desfazer"
"refazer"
"selecionar tudo"
"salvar"
"ctrl z"
"clicar"
"duplo clique"
"rolar para baixo"
```

---

## Regras do modo offline

Quando nao ha API de IA disponivel, o sistema usa correspondencia de palavras-chave.
Os seguintes comandos funcionam offline:

### Sistema
- "abrir calculadora", "abrir bloco de notas", "abrir explorador"
- "minimizar", "maximizar", "area de trabalho"
- "bloquear tela", "bloquear computador"
- "tirar print", "captura de tela", "screenshot"
- "aumentar volume", "diminuir volume", "baixar volume", "silenciar", "mudo"

### Navegador
- "abrir chrome", "abrir google chrome", "abrir edge"
- "nova aba", "nova guia", "fechar aba", "fechar guia"
- "voltar", "pagina anterior", "avancar", "proxima pagina"
- "recarregar", "atualizar pagina", "f5"
- "rolar para baixo", "descer", "rolar para cima", "subir"

### Office
- "abrir word", "abrir excel", "abrir powerpoint"
- "salvar", "salva", "desfazer", "copiar", "colar", "recortar"
- "selecionar tudo"

### Midia
- "pausar", "parar musica", "play pause"
- "proxima musica", "proxima faixa"
- "musica anterior", "faixa anterior"

### Pesquisa (prefixos)
- "pesquisar ...", "buscar ...", "procurar ...", "google ..."

### Digitacao (prefixos)
- "digitar ...", "escrever ...", "escreva ..."
