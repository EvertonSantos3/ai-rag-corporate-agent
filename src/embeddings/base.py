"""
Interface de embeddings. O resto do pipeline (vectorstore, retriever)
depende só desta interface — nunca de uma implementação específica.
Isso é o que permite trocar de "local" para "OCI Generative AI" sem
tocar em mais nada.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_textos(self, textos: list[str]) -> list[list[float]]:
        """Recebe uma lista de textos e devolve um vetor por texto."""

    def embed_texto(self, texto: str) -> list[float]:
        return self.embed_textos([texto])[0]
