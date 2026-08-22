# NexusBank — Agente de IA Corporativo (RAG)

Agente de IA corporativo baseado em RAG (Retrieval-Augmented Generation), desenvolvido
para o desafio **Alura Agentes**. Responde perguntas de colaboradores da **NexusBank**
(fintech fictícia) com base em documentos internos, cobrindo 5 domínios: Atendimento,
Privacidade, Segurança, Tarifas e Transações.

🔗 **App em produção:** https://ai-rag-corporate-agent-52biqfryljuhd4eccnq7kt.streamlit.app/

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
  embeddings/               # embeddings locais (sentence-transformers) — sem dependência de nuvem
  llm/                       # geração via API da Groq (gratuita, sem cartão de crédito)
  vectorstore/chroma_store.py
  rag/retriever.py          # busca semântica + filtro por metadados
  rag/generator.py          # prompt com citação de fonte + fallback anti-alucinação
  observability/logger.py   # log de execução em JSON Lines (pergunta, resposta, fontes, timestamp)
  interface/app.py          # chat web em Streamlit (identidade visual NexusBank)
  ingest_run.py             # script de ingestão end-to-end
logs/
  execucoes.jsonl           # registro de auditoria de cada pergunta feita ao agente
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

# Configure sua chave da Groq (gratuita, sem cartão): console.groq.com/keys
cp .env.example .env
# edite .env e cole sua GROQ_API_KEY

# 1. Indexar os documentos (não precisa de API key, roda 100% local)
python -m src.ingest_run

# 2. Subir a interface de chat
streamlit run src/interface/app.py
```

## Deploy no Streamlit Community Cloud

1. Repositório precisa estar público no GitHub (requisito do desafio).
2. Acesse [share.streamlit.io](https://share.streamlit.io), conecte sua conta GitHub e
   escolha este repositório.
3. Em "Main file path", informe `src/interface/app.py`.
4. Em **Settings > Secrets**, adicione:
   ```toml
   GROQ_API_KEY = "gsk_..."
   ```
5. Deploy. A primeira execução baixa o modelo de embeddings (~470 MB) e indexa os
   documentos automaticamente — pode levar alguns minutos na primeira vez.

> Nota: como o Streamlit Community Cloud reinicia o container periodicamente, o índice
> vetorial e o log de execuções não persistem entre reinícios (disco efêmero). Para
> este desafio isso não é um problema — a auto-indexação garante que o app volte a
> funcionar sozinho a cada reinício.

## Evidência de execução em nuvem

Vídeo demonstrando o agente respondendo perguntas em produção (Streamlit Community
Cloud) está disponível em [`evidencias/`](./evidencias).

## Registro de execução (auditoria)

Toda pergunta feita ao agente é registrada em `logs/execucoes.jsonl` (formato JSON
Lines), com timestamp, pergunta, resposta, fontes citadas e se caiu em fallback. O
log também pode ser consultado direto na barra lateral do app.

## Checklist do desafio

- [x] Coleta e organização de documentos (5 categorias, 20 arquivos, 125 pontos)
- [x] Processamento e extração de conteúdo (loaders para 8 formatos + chunking)
- [x] Indexação vetorial (ChromaDB local, embeddings multilíngues)
- [x] Camada de recuperação — busca semântica + filtro por categoria
- [x] Geração com citação de fonte obrigatória + fallback anti-alucinação
- [x] Interface simples, identifica-se como IA, exibe fontes, botão de feedback
- [x] Registro de execução (log JSON Lines com timestamp)
- [x] Deploy em nuvem com evidência (imagem/vídeo) — app publicado + vídeo em `evidencias/`

## Status

🚀 App publicado e funcionando — challenge Alura Agentes.
