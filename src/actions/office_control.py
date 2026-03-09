"""
Controle do Microsoft Office: Word, Excel, PowerPoint.
Usa win32com para acesso direto via API COM (mais confiável que atalhos).
"""

import logging
import time

import pyautogui

logger = logging.getLogger(__name__)


def _get_com(app_name: str):
    """Obtém ou abre uma instância do aplicativo Office via COM."""
    try:
        import win32com.client as win32
        try:
            return win32.GetActiveObject(app_name)
        except Exception:
            return win32.Dispatch(app_name)
    except ImportError:
        raise RuntimeError("pywin32 não instalado. Execute: pip install pywin32")


class OfficeControl:
    """Controla aplicativos Microsoft Office."""

    def execute(self, action: str, params: dict) -> str:
        parts = action.split(".")  # ["office", "word", "save"]
        if len(parts) < 3:
            return f"Ação Office inválida: {action}"
        app = parts[1]   # "word", "excel", "ppt"
        cmd = parts[2]   # "save", "new", etc.

        method_name = f"_{app}_{cmd.replace('-', '_')}"
        method = getattr(self, method_name, None)
        if method is None:
            # Fallback genérico por teclado
            return self._generic_keyboard(action, params)
        try:
            return method(params)
        except Exception as e:
            logger.error(f"Erro em {action}: {e}")
            return self._generic_keyboard(action, params)

    # ------------------------------------------------------------------ WORD
    def _word_open(self, params: dict) -> str:
        file = params.get("file")
        try:
            word = _get_com("Word.Application")
            word.Visible = True
            if file:
                word.Documents.Open(file)
                return f"Documento '{file}' aberto no Word."
            return "Word aberto."
        except Exception:
            import subprocess
            subprocess.Popen("winword.exe", shell=True)
            return "Word aberto."

    def _word_new(self, params: dict) -> str:
        word = _get_com("Word.Application")
        word.Visible = True
        word.Documents.Add()
        return "Novo documento Word criado."

    def _word_save(self, params: dict) -> str:
        try:
            word = _get_com("Word.Application")
            word.ActiveDocument.Save()
            return "Documento salvo."
        except Exception:
            pyautogui.hotkey("ctrl", "s")
            return "Salvando documento."

    def _word_save_as(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "shift", "s")
        filename = params.get("filename")
        if filename:
            time.sleep(0.8)
            pyautogui.hotkey("ctrl", "a")
            pyautogui.write(filename, interval=0.04)
        return "Diálogo Salvar Como aberto."

    def _word_close(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "w")
        return "Documento fechado."

    def _word_print(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "p")
        return "Diálogo de impressão aberto."

    def _word_bold(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "b")
        return "Negrito alternado."

    def _word_italic(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "i")
        return "Itálico alternado."

    def _word_underline(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "u")
        return "Sublinhado alternado."

    def _word_align(self, params: dict) -> str:
        alignment = params.get("alignment", "left")
        keys = {"left": "l", "center": "e", "right": "r", "justify": "j"}
        key = keys.get(alignment, "l")
        pyautogui.hotkey("ctrl", key)
        return f"Alinhamento {alignment}."

    def _word_font_size(self, params: dict) -> str:
        size = str(params.get("size", 12))
        pyautogui.hotkey("ctrl", "shift", "p")
        time.sleep(0.4)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.write(size, interval=0.05)
        pyautogui.press("enter")
        return f"Tamanho de fonte {size}."

    def _word_heading(self, params: dict) -> str:
        level = params.get("level", 1)
        hotkeys = {1: ("ctrl", "alt", "1"), 2: ("ctrl", "alt", "2"), 3: ("ctrl", "alt", "3")}
        pyautogui.hotkey(*hotkeys.get(level, ("ctrl", "alt", "1")))
        return f"Título nível {level} aplicado."

    def _word_bullet_list(self, params: dict) -> str:
        # Home tab > Paragraph > Bullets
        pyautogui.hotkey("ctrl", "shift", "l")
        return "Lista com marcadores aplicada."

    def _word_numbered_list(self, params: dict) -> str:
        pyautogui.hotkey("alt", "h", "n", "l")
        return "Lista numerada aplicada."

    def _word_insert_table(self, params: dict) -> str:
        rows = params.get("rows", 3)
        cols = params.get("cols", 3)
        try:
            word = _get_com("Word.Application")
            doc = word.ActiveDocument
            rng = doc.Range(doc.Content.End - 1, doc.Content.End - 1)
            doc.Tables.Add(rng, rows, cols)
            return f"Tabela {rows}x{cols} inserida."
        except Exception:
            pyautogui.hotkey("alt", "n", "t")
            return "Menu de inserção de tabela aberto."

    def _word_find_replace(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "h")
        find = params.get("find", "")
        replace = params.get("replace", "")
        if find:
            time.sleep(0.5)
            pyautogui.write(find, interval=0.04)
            pyautogui.press("tab")
            pyautogui.write(replace, interval=0.04)
        return "Localizar e substituir aberto."

    def _word_spell_check(self, params: dict) -> str:
        pyautogui.press("f7")
        return "Verificação ortográfica iniciada."

    def _word_word_count(self, params: dict) -> str:
        pyautogui.hotkey("alt", "r", "w", "c")
        return "Contagem de palavras."

    def _word_new_page(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "enter")
        return "Nova página inserida."

    # ----------------------------------------------------------------- EXCEL
    def _excel_open(self, params: dict) -> str:
        file = params.get("file")
        try:
            excel = _get_com("Excel.Application")
            excel.Visible = True
            if file:
                excel.Workbooks.Open(file)
                return f"Arquivo '{file}' aberto no Excel."
            return "Excel aberto."
        except Exception:
            import subprocess
            subprocess.Popen("excel.exe", shell=True)
            return "Excel aberto."

    def _excel_new(self, params: dict) -> str:
        excel = _get_com("Excel.Application")
        excel.Visible = True
        excel.Workbooks.Add()
        return "Nova planilha criada."

    def _excel_save(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "s")
        return "Planilha salva."

    def _excel_goto_cell(self, params: dict) -> str:
        cell = params.get("cell", "A1")
        pyautogui.hotkey("ctrl", "g")
        time.sleep(0.4)
        pyautogui.write(cell, interval=0.05)
        pyautogui.press("enter")
        return f"Navegando para célula {cell}."

    def _excel_auto_sum(self, params: dict) -> str:
        pyautogui.hotkey("alt", "=")
        return "AutoSoma aplicada."

    def _excel_create_chart(self, params: dict) -> str:
        pyautogui.hotkey("alt", "n", "r")
        return "Assistente de gráfico aberto."

    def _excel_filter(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "shift", "l")
        return "Filtro alternado."

    def _excel_sort(self, params: dict) -> str:
        order = params.get("order", "asc")
        if order == "asc":
            pyautogui.hotkey("alt", "h", "s", "a")
        else:
            pyautogui.hotkey("alt", "h", "s", "d")
        return f"Dados ordenados em {order}."

    def _excel_freeze_panes(self, params: dict) -> str:
        pyautogui.hotkey("alt", "w", "f", "f")
        return "Painéis congelados."

    def _excel_new_sheet(self, params: dict) -> str:
        pyautogui.hotkey("shift", "f11")
        name = params.get("name")
        if name:
            time.sleep(0.3)
            pyautogui.write(name, interval=0.05)
            pyautogui.press("enter")
        return "Nova planilha criada."

    def _excel_find_replace(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "h")
        return "Localizar e substituir aberto."

    def _excel_pivot_table(self, params: dict) -> str:
        pyautogui.hotkey("alt", "n", "v")
        return "Assistente de tabela dinâmica aberto."

    # --------------------------------------------------------------- POWERPOINT
    def _ppt_open(self, params: dict) -> str:
        file = params.get("file")
        try:
            ppt = _get_com("PowerPoint.Application")
            ppt.Visible = True
            if file:
                ppt.Presentations.Open(file)
                return f"Apresentação '{file}' aberta."
            return "PowerPoint aberto."
        except Exception:
            import subprocess
            subprocess.Popen("powerpnt.exe", shell=True)
            return "PowerPoint aberto."

    def _ppt_new(self, params: dict) -> str:
        ppt = _get_com("PowerPoint.Application")
        ppt.Visible = True
        ppt.Presentations.Add()
        return "Nova apresentação criada."

    def _ppt_save(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "s")
        return "Apresentação salva."

    def _ppt_new_slide(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "m")
        return "Novo slide adicionado."

    def _ppt_delete_slide(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "d")
        return "Slide excluído."

    def _ppt_next_slide(self, params: dict) -> str:
        pyautogui.press("pagedown")
        return "Próximo slide."

    def _ppt_prev_slide(self, params: dict) -> str:
        pyautogui.press("pageup")
        return "Slide anterior."

    def _ppt_start_slideshow(self, params: dict) -> str:
        pyautogui.press("f5")
        return "Apresentação iniciada."

    def _ppt_end_slideshow(self, params: dict) -> str:
        pyautogui.press("escape")
        return "Apresentação encerrada."

    def _ppt_insert_image(self, params: dict) -> str:
        pyautogui.hotkey("alt", "n", "p")
        return "Diálogo de inserção de imagem aberto."

    def _ppt_duplicate_slide(self, params: dict) -> str:
        pyautogui.hotkey("ctrl", "d")
        return "Slide duplicado."

    def _generic_keyboard(self, action: str, params: dict) -> str:
        """Fallback genérico para ações não mapeadas."""
        logger.warning(f"Ação Office sem implementação direta: {action}")
        return f"Ação {action} não suportada diretamente."
