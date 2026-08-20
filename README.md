# AI RAG Corporate Agent

Agente de IA corporativo baseado em RAG (Retrieval-Augmented Generation), desenvolvido
para o desafio **Alura Agentes**. Responde perguntas de colaboradores com base em
documentos internos de uma fintech, cobrindo 5 domínios: Atendimento, Privacidade,
Segurança, Tarifas e Transações.

## Arquitetura

```
data/
  catalog/documents.json   # metadados dos documentos (id, categoria, owner, versão...)
  documents/<categoria>/   # arquivos originais (pdf, docx, xlsx, md, csv, json, html...)
src/
  catalog/schema.py        # schema Pydantic do catálogo
  ingestion/loaders.py      # extração de texto por formato
  ingestion/chunking.py     # limpeza + divisão em chunks
  embeddings/               # interface + implementações (local / OCI)
  llm/                       # interface + implementações (mock / OCI)
  vectorstore/chroma_store.py
  rag/retriever.py          # busca semântica + filtro por metadados
  rag/generator.py          # prompt com citação de fonte + fallback anti-alucinação
  interface/app.py          # chat web em Streamlit
  ingest_run.py             # script de ingestão end-to-end
```

Ver `docs/architecture.md` para mais detalhes da modelagem de dados.

## Como rodar localmente

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. Indexar os documentos de exemplo
python -m src.ingest_run

# 2. Subir a interface de chat
streamlit run src/interface/app.py
```

Por padrão, o projeto roda com **embeddings locais** (`sentence-transformers`) e um
**LLM mock** — assim dá para testar o pipeline inteiro sem depender de nenhuma conta
de nuvem. Para usar o OCI Generative AI (LLM + embeddings), configure `.env` (veja
`.env.example`) e troque os providers em `src/ingest_run.py` e `src/interface/app.py`
por `OCIEmbeddingProvider` e `OCILLMProvider`.

## Deploy

Requisito do desafio: deploy na OCI usando ao menos 1 serviço Oracle Cloud. Este
projeto usa o **OCI Generative AI** para LLM e embeddings. Ver `docs/architecture.md`
para o plano de deploy completo (Docker, OCIR, Compute/Container Instances).

## Status

🚧 Em desenvolvimento — challenge Alura Agentes.
