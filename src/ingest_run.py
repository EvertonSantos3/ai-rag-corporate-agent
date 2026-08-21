"""
Script principal de ingestão: lê data/catalog/documents.json, processa
cada documento ativo (extração -> limpeza -> chunking) e indexa no
vector store.

A função ingerir_catalogo() também é reutilizada pelo app.py para
auto-indexar na primeira execução (útil em ambientes como o Streamlit
Community Cloud, onde o disco não persiste entre reinícios).

Uso via linha de comando:
    python -m src.ingest_run
"""
from __future__ import annotations

import json
from pathlib import Path

from src.catalog.schema import Catalogo
from src.embeddings.base import EmbeddingProvider
from src.ingestion.chunking import dividir_em_chunks
from src.ingestion.loaders import carregar_documento
from src.vectorstore.chroma_store import ChromaVectorStore

DATA_DIR = Path("data")
CATALOGO_PATH = DATA_DIR / "catalog" / "documents.json"


def carregar_catalogo() -> Catalogo:
    dados = json.loads(CATALOGO_PATH.read_text(encoding="utf-8"))
    return Catalogo(**dados)


def ingerir_catalogo(vector_store: ChromaVectorStore, verbose: bool = True) -> int:
    """Processa e indexa todos os documentos ativos do catálogo. Retorna o total de chunks indexados."""
    catalogo = carregar_catalogo()
    total_chunks = 0
    for doc in catalogo.ativos():
        caminho = doc.caminho_absoluto(DATA_DIR)
        if verbose:
            print(f"Processando {doc.id} — {doc.titulo} ({caminho})")
        texto = carregar_documento(caminho)
        chunks = dividir_em_chunks(
            texto,
            documento_id=doc.id,
            metadata={"titulo": doc.titulo, "categoria": doc.categoria.value, "owner": doc.owner},
        )
        vector_store.indexar_chunks(chunks)
        total_chunks += len(chunks)
        if verbose:
            print(f"  -> {len(chunks)} chunks indexados")
    return total_chunks


def main():
    from src.embeddings.local_provider import LocalEmbeddingProvider

    embedding_provider: EmbeddingProvider = LocalEmbeddingProvider()
    vector_store = ChromaVectorStore(embedding_provider=embedding_provider)
    total_chunks = ingerir_catalogo(vector_store)
    catalogo = carregar_catalogo()
    print(f"\nIngestão concluída: {len(catalogo.ativos())} documentos, {total_chunks} chunks no total.")


if __name__ == "__main__":
    main()
