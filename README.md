# NexusBank — Agente de IA Corporativo (RAG)

Agente de IA corporativo baseado em RAG (Retrieval-Augmented Generation), desenvolvido
para o desafio **Alura Agentes**. Responde perguntas de colaboradores da **NexusBank**
(fintech fictícia) com base em documentos internos, cobrindo 5 domínios: Atendimento,
Privacidade, Segurança, Tarifas e Transações.

Base de conhecimento: **20 documentos, 125 pontos de conteúdo** (25 por categoria).

## Arquitetura

```
data/
  catalog/documents.json   # metadados dos documentos (id, categoria, owner, versão...)
  documents/<categoria>/   # arquivos originais (4 arquivos .md por categoria)
src/
  catalog/schema.py        # schema Pydantic do catálogo
  ingestion/loaders.py      # extração de texto por formato (pdf, docx, xlsx, pptx, md, csv, json, html)
  ingestion/chunking.py     # limpeza + divisão em chunks
  embeddings/               # interface + implementações (local / OCI)
  llm/                       # interface + implementações (mock / OCI)
  vectorstore/chroma_store.py
  rag/retriever.py          # busca semântica + filtro por metadados
  rag/generator.py          # prompt com citação de fonte + fallback anti-alucinação
  interface/app.py          # chat web em Streamlit (identidade visual NexusBank)
  ingest_run.py             # script de ingestão end-to-end
```

Ver `docs/architecture.md` para mais detalhes da modelagem de dados.

## Identidade visual

Tema escuro/neon: fundo azul-marinho quase preto (`#0B0E14`) com acento violeta-elétrico
(`#7C5CFF`), tipografia Space Grotesk (títulos) + Inter (corpo), e um logo de "nós
conectados" no cabeçalho — representando a metáfora do agente conectando perguntas aos
documentos certos (o próprio conceito de "Nexus").

## Como rodar localmente

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. Indexar os documentos
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
