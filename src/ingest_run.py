"""
Script principal de ingestão: lê data/catalog/documents.json, processa
cada documento ativo (extração -> limpeza -> chunking) e indexa no
vector store.

Uso:
    python -m src.ingest_run
"""
from __future__ import annotations

import json
from pathlib import Path

from src.catalog.schema import Catalogo
from src.embeddings.local_provider import LocalEmbeddingProvider
from src.ingestion.chunking import dividir_em_chunks
from src.ingestion.loaders import carregar_documento
from src.vectorstore.chroma_store import ChromaVectorStore

DATA_DIR = Path("data")
CATALOGO_PATH = DATA_DIR / "catalog" / "documents.json"


def carregar_catalogo() -> Catalogo:
    dados = json.loads(CATALOGO_PATH.read_text(encoding="utf-8"))
    return Catalogo(**dados)


def main():
    catalogo = carregar_catalogo()
    embedding_provider = LocalEmbeddingProvider()  # troque por OCIEmbeddingProvider() quando tiver credenciais
    vector_store = ChromaVectorStore(embedding_provider=embedding_provider)

    total_chunks = 0
    for doc in catalogo.ativos():
        caminho = doc.caminho_absoluto(DATA_DIR)
        print(f"Processando {doc.id} — {doc.titulo} ({caminho})")
        texto = carregar_documento(caminho)
        chunks = dividir_em_chunks(
            texto,
            documento_id=doc.id,
            metadata={"titulo": doc.titulo, "categoria": doc.categoria.value, "owner": doc.owner},
        )
        vector_store.indexar_chunks(chunks)
        total_chunks += len(chunks)
        print(f"  -> {len(chunks)} chunks indexados")

    print(f"\nIngestão concluída: {len(catalogo.ativos())} documentos, {total_chunks} chunks no total.")


if __name__ == "__main__":
    main()
