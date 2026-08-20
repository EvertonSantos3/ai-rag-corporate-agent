"""
Geração e validação de respostas (etapa 5 do desafio).

Regras aplicadas aqui, conforme exigido no card do Trello:
  - responder SOMENTE com base no contexto recuperado;
  - sempre citar a fonte (documento/seção);
  - se não houver contexto suficiente, informar isso claramente em vez
    de inventar uma resposta (fallback).
"""
from __future__ import annotations

from dataclasses import dataclass

from src.llm.base import LLMProvider
from src.rag.retriever import ResultadoBusca

MENSAGEM_FALLBACK = (
    "Não encontrei essa informação nos documentos disponíveis. "
    "Recomendo entrar em contato com a área responsável para mais detalhes."
)

PROMPT_TEMPLATE = """Você é um agente de IA corporativo. Responda à pergunta do colaborador
usando SOMENTE as informações do CONTEXTO abaixo. Não use conhecimento externo.
Se o contexto não for suficiente para responder, diga isso claramente.
Ao final da resposta, cite as fontes usadas no formato [documento - categoria].

CONTEXTO:
{contexto}

PERGUNTA: {pergunta}

RESPOSTA:"""


@dataclass
class RespostaAgente:
    texto: str
    fontes: list[dict]
    teve_fallback: bool


def _montar_contexto(trechos: list[dict]) -> str:
    blocos = []
    for t in trechos:
        meta = t["metadata"]
        origem = f"{meta.get('titulo', meta.get('documento_id'))} - {meta.get('categoria', '?')}"
        blocos.append(f"[{origem}]\n{t['texto']}")
    return "\n\n---\n\n".join(blocos)


class ResponseGenerator:
    def __init__(self, llm_provider: LLMProvider):
        self._llm_provider = llm_provider

    def gerar(self, pergunta: str, resultado_busca: ResultadoBusca) -> RespostaAgente:
        if not resultado_busca.tem_contexto_suficiente:
            return RespostaAgente(texto=MENSAGEM_FALLBACK, fontes=[], teve_fallback=True)

        contexto = _montar_contexto(resultado_busca.trechos)
        prompt = PROMPT_TEMPLATE.format(contexto=contexto, pergunta=pergunta)
        texto_resposta = self._llm_provider.gerar_resposta(prompt)

        fontes = [
            {
                "documento": t["metadata"].get("titulo", t["metadata"].get("documento_id")),
                "categoria": t["metadata"].get("categoria"),
            }
            for t in resultado_busca.trechos
        ]
        return RespostaAgente(texto=texto_resposta, fontes=fontes, teve_fallback=False)
