"""
Camada de recuperação (etapa 4 do desafio): busca semântica no vector
store, com filtro opcional por metadados e limiar de confiança para
decidir se há contexto suficiente para responder.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.vectorstore.chroma_store import ChromaVectorStore


@dataclass
class ResultadoBusca:
    trechos: list[dict]
    tem_contexto_suficiente: bool


class Retriever:
    def __init__(
        self,
        vector_store: ChromaVectorStore,
        limiar_distancia: float = 0.8,
        top_k: int = 5,
    ):
        self._vector_store = vector_store
        self._limiar_distancia = limiar_distancia
        self._top_k = top_k

    def buscar(
        self,
        pergunta: str,
        categoria: str | None = None,
    ) -> ResultadoBusca:
        candidatos = self._vector_store.buscar(
            pergunta,
            top_k=self._top_k,
            filtro_categoria=categoria,
        )

        # Distância menor = maior similaridade.
        # Apenas resultados dentro do limiar são considerados relevantes.
        relevantes = [
            c
            for c in candidatos
            if c["distancia"] <= self._limiar_distancia
        ]

        return ResultadoBusca(
            trechos=relevantes,
            tem_contexto_suficiente=bool(relevantes),
        )
