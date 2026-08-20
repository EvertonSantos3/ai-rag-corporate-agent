"""
Limpeza de texto e divisão em chunks (etapa 2 do desafio).

Usa divisão por tamanho fixo com sobreposição, respeitando limites de
parágrafo quando possível para não cortar uma ideia no meio.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


def limpar_texto(texto: str) -> str:
    """Remove ruídos comuns: espaços duplicados, linhas em branco excessivas."""
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    return texto.strip()


@dataclass
class Chunk:
    texto: str
    indice: int
    documento_id: str
    metadata: dict = field(default_factory=dict)


def dividir_em_chunks(
    texto: str,
    documento_id: str,
    metadata: dict | None = None,
    tamanho_maximo: int = 800,
    sobreposicao: int = 100,
) -> list[Chunk]:
    """
    Divide o texto em chunks de até `tamanho_maximo` caracteres, com
    `sobreposicao` caracteres compartilhados entre chunks consecutivos.

    Tenta cortar em quebras de parágrafo (\n\n) antes de cortar no meio
    de uma frase, quando o parágrafo cabe dentro do tamanho máximo.
    """
    metadata = metadata or {}
    texto = limpar_texto(texto)
    paragrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]

    chunks: list[str] = []
    buffer = ""

    for paragrafo in paragrafos:
        candidato = f"{buffer}\n\n{paragrafo}".strip() if buffer else paragrafo
        if len(candidato) <= tamanho_maximo:
            buffer = candidato
        else:
            if buffer:
                chunks.append(buffer)
            if len(paragrafo) <= tamanho_maximo:
                buffer = paragrafo
            else:
                # parágrafo maior que o limite: corta por tamanho fixo
                for i in range(0, len(paragrafo), tamanho_maximo - sobreposicao):
                    chunks.append(paragrafo[i : i + tamanho_maximo])
                buffer = ""
    if buffer:
        chunks.append(buffer)

    return [
        Chunk(texto=c, indice=i, documento_id=documento_id, metadata=metadata)
        for i, c in enumerate(chunks)
    ]
