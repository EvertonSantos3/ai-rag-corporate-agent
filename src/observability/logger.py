"""
Registro de execução (etapa 8 do desafio): toda pergunta feita ao agente é
logada em formato JSON Lines (um objeto JSON por linha), com timestamp,
pergunta, fontes usadas e se caiu em fallback — permitindo auditoria e
evidência de uso em produção.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path("logs/execucoes.jsonl")


def registrar_execucao(pergunta: str, resposta_texto: str, fontes: list[dict], teve_fallback: bool) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entrada = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pergunta": pergunta,
        "resposta": resposta_texto,
        "fontes": fontes,
        "teve_fallback": teve_fallback,
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entrada, ensure_ascii=False) + "\n")
