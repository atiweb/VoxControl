"""
Interpretador de intenções usando IA (Claude ou OpenAI).
Converte texto em português para ações estruturadas JSON.
"""

import json
import logging
import re
from typing import Optional

from .prompts import SYSTEM_PROMPT, UNKNOWN_RESPONSE, CONFIRMATION_PROMPT

logger = logging.getLogger(__name__)


class IntentParser:
    """Interpreta comandos de voz usando IA (Claude ou OpenAI)."""

    def __init__(self, config: dict):
        self.config = config
        self.backend = config.get("backend", "claude")
        self.fallback = config.get("fallback", "openai")
        self.min_confidence = config.get("min_confidence", 0.6)

        self._claude_client = None
        self._openai_client = None
        self._init_clients()

    def _init_clients(self):
        import os

        if self.backend == "claude" or self.fallback == "claude":
            try:
                import anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if api_key:
                    self._claude_client = anthropic.Anthropic(api_key=api_key)
                    logger.info("Cliente Claude inicializado.")
                else:
                    logger.warning("ANTHROPIC_API_KEY não encontrada.")
            except ImportError:
                logger.warning("anthropic não instalado. pip install anthropic")

        if self.backend == "openai" or self.fallback == "openai":
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self._openai_client = OpenAI(api_key=api_key)
                    logger.info("Cliente OpenAI inicializado.")
                else:
                    logger.warning("OPENAI_API_KEY não encontrada.")
            except ImportError:
                logger.warning("openai não instalado. pip install openai")

    def parse(self, text: str) -> dict:
        """
        Interpreta o texto e retorna uma ação estruturada.
        Tenta o backend primário; se falhar, usa o fallback.
        """
        logger.info(f"Interpretando: '{text}'")

        result = None
        if self.backend != "offline":
            result = self._try_parse(text, self.backend)

        if result is None and self.fallback and self.fallback != self.backend:
            logger.info(f"Tentando fallback: {self.fallback}")
            result = self._try_parse(text, self.fallback)

        if result is None:
            logger.warning("Todos os backends falharam. Usando correspondência offline.")
            result = self._offline_parse(text)

        logger.info(f"Ação interpretada: {result.get('action')} (confiança: {result.get('confidence', 0):.2f})")
        return result

    def _try_parse(self, text: str, backend: str) -> Optional[dict]:
        try:
            if backend == "claude" and self._claude_client:
                return self._parse_claude(text)
            elif backend == "openai" and self._openai_client:
                return self._parse_openai(text)
        except Exception as e:
            logger.error(f"Erro no backend '{backend}': {e}")
        return None

    def _parse_claude(self, text: str) -> Optional[dict]:
        cfg = self.config.get("claude", {})
        response = self._claude_client.messages.create(
            model=cfg.get("model", "claude-haiku-4-5-20251001"),
            max_tokens=cfg.get("max_tokens", 512),
            temperature=cfg.get("temperature", 0.1),
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": text}],
        )
        raw = response.content[0].text.strip()
        return self._parse_json_response(raw)

    def _parse_openai(self, text: str) -> Optional[dict]:
        cfg = self.config.get("openai", {})
        response = self._openai_client.chat.completions.create(
            model=cfg.get("model", "gpt-4o-mini"),
            max_tokens=cfg.get("max_tokens", 512),
            temperature=cfg.get("temperature", 0.1),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
        )
        raw = response.choices[0].message.content.strip()
        return self._parse_json_response(raw)

    def _parse_json_response(self, raw: str) -> Optional[dict]:
        """Extrai e valida JSON da resposta da IA."""
        # Remove blocos de código markdown se presentes
        raw = re.sub(r"```(?:json)?\n?", "", raw).strip()
        try:
            data = json.loads(raw)
            required = {"action", "params", "confidence", "response_text"}
            if not required.issubset(data.keys()):
                logger.warning(f"Resposta JSON incompleta: {data}")
                return None
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}\nResposta: {raw}")
            return None

    def _offline_parse(self, text: str) -> dict:
        """
        Correspondência simples de palavras-chave quando a IA não está disponível.
        Cobertura básica dos comandos mais comuns.
        """
        text_lower = text.lower().strip()

        rules = [
            # Sistema
            (["abrir calculadora", "abre calculadora"], "system.open_app", {"app": "calc"}, "Abrindo a calculadora."),
            (["abrir bloco de notas", "abre bloco de notas", "abrir notepad"], "system.open_app", {"app": "notepad"}, "Abrindo o bloco de notas."),
            (["abrir explorador", "abrir pasta", "abrir arquivos"], "system.open_app", {"app": "explorer"}, "Abrindo o explorador de arquivos."),
            (["minimizar", "minimiza"], "system.minimize", {}, "Janela minimizada."),
            (["maximizar", "maximiza"], "system.maximize", {}, "Janela maximizada."),
            (["área de trabalho", "mostrar área de trabalho"], "system.show_desktop", {}, "Mostrando a área de trabalho."),
            (["bloquear tela", "bloquear computador"], "system.lock_screen", {}, "Bloqueando a tela."),
            (["tirar print", "captura de tela", "screenshot"], "system.screenshot", {"region": "full", "save_to_desktop": True}, "Captura de tela realizada."),
            (["aumentar volume"], "system.volume_up", {"amount": 3}, "Volume aumentado."),
            (["diminuir volume", "baixar volume"], "system.volume_down", {"amount": 3}, "Volume diminuído."),
            (["silenciar", "mudo", "mutar"], "system.volume_mute", {}, "Volume silenciado."),
            # Navegador
            (["abrir chrome", "abrir google chrome"], "browser.open", {"browser": "chrome"}, "Abrindo o Chrome."),
            (["abrir edge"], "browser.open", {"browser": "edge"}, "Abrindo o Edge."),
            (["nova aba", "nova guia"], "browser.new_tab", {}, "Nova aba aberta."),
            (["fechar aba", "fechar guia"], "browser.close_tab", {}, "Aba fechada."),
            (["voltar", "página anterior"], "browser.go_back", {}, "Voltando."),
            (["avançar", "próxima página"], "browser.go_forward", {}, "Avançando."),
            (["recarregar", "atualizar página", "f5"], "browser.refresh", {}, "Página recarregada."),
            (["rolar para baixo", "descer"], "browser.scroll_down", {"amount": 3}, "Rolando para baixo."),
            (["rolar para cima", "subir"], "browser.scroll_up", {"amount": 3}, "Rolando para cima."),
            # WhatsApp
            (["abrir whatsapp", "whatsapp"], "whatsapp.open", {}, "Abrindo o WhatsApp."),
            # Office
            (["abrir word", "microsoft word"], "system.open_app", {"app": "word"}, "Abrindo o Word."),
            (["abrir excel", "microsoft excel"], "system.open_app", {"app": "excel"}, "Abrindo o Excel."),
            (["abrir powerpoint", "power point"], "system.open_app", {"app": "powerpnt"}, "Abrindo o PowerPoint."),
            (["salvar", "salva"], "keyboard.save", {}, "Salvando."),
            (["desfazer", "ctrl z"], "keyboard.undo", {}, "Ação desfeita."),
            (["refazer", "ctrl y"], "keyboard.redo", {}, "Ação refeita."),
            (["copiar", "copia"], "keyboard.copy", {}, "Copiado."),
            (["colar", "cola"], "keyboard.paste", {}, "Colado."),
            (["recortar", "cortar"], "keyboard.cut", {}, "Recortado."),
            (["selecionar tudo"], "keyboard.select_all", {}, "Tudo selecionado."),
            # Mídia
            (["pausar", "parar música", "play pause"], "media.play_pause", {}, "Play/Pause."),
            (["próxima música", "próxima faixa"], "media.next", {}, "Próxima música."),
            (["música anterior", "faixa anterior"], "media.previous", {}, "Música anterior."),
        ]

        for triggers, action, params, response in rules:
            if any(t in text_lower for t in triggers):
                return {
                    "action": action,
                    "params": params,
                    "confidence": 0.85,
                    "response_text": response,
                    "requires_confirmation": False,
                }

        # Pesquisa web genérica
        for prefix in ["pesquisar", "pesquisa", "buscar", "busca", "procurar", "google"]:
            if text_lower.startswith(prefix):
                query = text[len(prefix):].strip()
                if query:
                    return {
                        "action": "browser.search",
                        "params": {"query": query, "engine": "google"},
                        "confidence": 0.80,
                        "response_text": f"Pesquisando por {query}.",
                        "requires_confirmation": False,
                    }

        # Digitar texto
        for prefix in ["digitar", "digita", "escrever", "escreve", "escreva"]:
            if text_lower.startswith(prefix):
                type_text = text[len(prefix):].strip()
                if type_text:
                    return {
                        "action": "keyboard.type",
                        "params": {"text": type_text},
                        "confidence": 0.85,
                        "response_text": f"Digitando: {type_text}",
                        "requires_confirmation": False,
                    }

        return {**UNKNOWN_RESPONSE, "response_text": f"Não entendi '{text}'. Pode repetir?"}

    def check_confirmation(self, original_command: str, action_desc: str, user_response: str) -> bool:
        """Verifica se a resposta do usuário é uma confirmação."""
        confirm_words = ["sim", "pode", "confirma", "ok", "isso", "certo", "vai", "execute", "confirmo", "é isso"]
        cancel_words = ["não", "cancela", "para", "desiste", "errado", "outro", "nevermind"]

        response_lower = user_response.lower()

        if any(w in response_lower for w in confirm_words):
            return True
        if any(w in response_lower for w in cancel_words):
            return False

        # Usa IA para casos ambíguos
        if self._claude_client or self._openai_client:
            prompt = CONFIRMATION_PROMPT.format(
                original_command=original_command,
                action_description=action_desc,
                confirmation_text=user_response,
            )
            try:
                result = self._try_parse(prompt, self.backend) or self._try_parse(prompt, self.fallback)
                if result and isinstance(result, str):
                    return "confirm" in result.lower()
            except Exception:
                pass

        return False
