"""
Vector store local com ChromaDB — não depende de nenhuma nuvem, então
pode ser desenvolvido e testado hoje mesmo. Persiste em disco em
./data/chroma_db para não perder o índice entre execuções.
"""
from __future__ import annotations

from pathlib import Path

from src.embeddings.base import EmbeddingProvider
from src.ingestion.chunking import Chunk


class ChromaVectorStore:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        persist_dir: str = "./data/chroma_db",
        collection_name: str = "documentos_corporativos",
    ):
        try:
            import chromadb
        except ImportError as e:
            raise ImportError("chromadb é necessário: pip install chromadb --break-system-packages") from e

        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        self._embedding_provider = embedding_provider
        self._client = chromadb.PersistentClient(path=persist_dir)
        self._collection = self._client.get_or_create_collection(collection_name)

    def indexar_chunks(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return
        textos = [c.texto for c in chunks]
        vetores = self._embedding_provider.embed_textos(textos)
        ids = [f"{c.documento_id}::{c.indice}" for c in chunks]
        metadatas = [{**c.metadata, "documento_id": c.documento_id, "chunk_indice": c.indice} for c in chunks]
        self._collection.upsert(ids=ids, embeddings=vetores, documents=textos, metadatas=metadatas)

    def buscar(self, pergunta: str, top_k: int = 5, filtro_categoria: str | None = None) -> list[dict]:
        vetor_pergunta = self._embedding_provider.embed_texto(pergunta)
        where = {"categoria": filtro_categoria} if filtro_categoria else None
        resultado = self._collection.query(
            query_embeddings=[vetor_pergunta],
            n_results=top_k,
            where=where,
        )
        candidatos = []
        for texto, metadata, distancia in zip(
            resultado["documents"][0], resultado["metadatas"][0], resultado["distances"][0]
        ):
            candidatos.append({"texto": texto, "metadata": metadata, "distancia": distancia})
        return candidatos
