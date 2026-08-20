"""
Embeddings locais via sentence-transformers — roda 100% offline, sem
custo e sem depender de nenhuma conta de nuvem. Útil para desenvolver
e testar o pipeline hoje, antes da conta OCI estar ativa.

Modelo sugerido: 'paraphrase-multilingual-MiniLM-L12-v2' (multilíngue,
funciona bem com português, e é leve o suficiente para rodar em CPU).
"""
from __future__ import annotations

from .base import EmbeddingProvider


class LocalEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            raise ImportError(
                "sentence-transformers é necessário: "
                "pip install sentence-transformers --break-system-packages"
            ) from e
        self._model = SentenceTransformer(model_name)

    def embed_textos(self, textos: list[str]) -> list[list[float]]:
        vetores = self._model.encode(textos, convert_to_numpy=True, show_progress_bar=False)
        return vetores.tolist()
