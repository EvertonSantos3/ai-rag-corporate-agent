# Arquitetura — NexusBank Agente IA

## 1. Visão geral

O NexusBank Agente IA é um sistema de perguntas e respostas corporativo baseado em **Retrieval-Augmented Generation (RAG)**, desenvolvido para o desafio Alura Agentes. A base de conhecimento simula a documentação interna de uma instituição financeira fictícia, a NexusBank.

O objetivo é responder perguntas em linguagem natural utilizando exclusivamente o conteúdo indexado da base documental, evitando respostas fundamentadas em conhecimento externo ao modelo. Quando a base não contém evidência suficiente para responder, o sistema recorre a uma resposta de fallback em vez de gerar uma resposta especulativa.

O pipeline combina busca semântica (embeddings + ChromaDB) com geração de texto via API da Groq, além de uma camada de observabilidade que registra cada execução para fins de auditoria.

## 2. Arquitetura do sistema

```
Documentos
   │
   ▼
Ingestão (loaders)
   │
   ▼
Chunking
   │
   ▼
Embeddings (locais)
   │
   ▼
ChromaDB (persistência local)
   │
   ▼
Retriever ──── pergunta do usuário
   │
   ▼
Contexto (top_k=5, threshold≤0.8)
   │
   ├── contexto suficiente ──► LLM (Groq) ──► Resposta + Fontes
   │
   └── contexto insuficiente ──► Fallback
   │
   ▼
Observabilidade (log JSONL)
```

## 3. Organização dos dados

A base documental é dividida em cinco categorias: **Atendimento, Privacidade, Segurança, Tarifas, Transações**.

O catálogo (`data/catalog/documents.json`) centraliza os metadados de cada documento:

| Campo | Descrição |
|---|---|
| `document_id` | Identificador único do documento |
| `titulo` | Título do documento |
| `categoria` | Uma das cinco categorias da base |
| `responsavel` | Área responsável pelo conteúdo |
| `versao` | Versão do documento |
| `caminho` | Caminho do arquivo em `data/documents/` |

Durante a ingestão, cada documento é dividido em **chunks**, que preservam os metadados de origem (`document_id`, `categoria`, `titulo`, `chunk_indice`). Isso permite rastrear, a partir de qualquer trecho recuperado, o documento e a categoria de origem.

## 4. Pipeline de ingestão

O fluxo de ingestão (`src/ingestion/`) segue as etapas:

1. **Loaders** (`loaders.py`) — leitura dos documentos originais (Markdown, CSV, JSON e outros formatos suportados).
2. **Normalização** — limpeza básica do texto extraído.
3. **Chunking** (`chunking.py`) — divisão do texto em blocos menores, respeitando um tamanho máximo e preservando os metadados do documento original.
4. **Embeddings** — geração do vetor de cada chunk.
5. **Indexação** — inserção dos vetores e metadados no ChromaDB.

O chunking existe por dois motivos: limitar a quantidade de texto enviada ao modelo de geração e aumentar a precisão da recuperação semântica, já que blocos menores tendem a ser mais específicos.

## 5. Embeddings e busca vetorial

Os embeddings são gerados **localmente** (`src/embeddings/`), o que reduz a dependência de serviços externos durante a indexação.

O **ChromaDB** (`src/vectorstore/chroma_store.py`) atua como vector store, com persistência em `data/chroma_db/`. Esse diretório é gerado em tempo de execução e **não é versionado** no Git.

A busca compara a pergunta (também convertida em embedding) contra os vetores indexados, retornando os resultados mais próximos por distância — quanto **menor a distância, maior a similaridade**.

## 6. Recuperação (Retriever)

O `Retriever` (`src/rag/retriever.py`) implementa a lógica de busca semântica:

| Parâmetro | Valor |
|---|---|
| `top_k` | 5 |
| `limiar_distancia` | 0.8 |

Regras de filtragem:

- Resultados com distância **≤ 0.8** são considerados relevantes.
- Resultados com distância **> 0.8** são descartados.
- É possível filtrar a busca por `categoria`; quando nenhuma categoria é informada, a busca considera toda a base.
- Se **nenhum** resultado passar pelo threshold, `tem_contexto_suficiente = False` e a etapa de geração não é chamada — o sistema segue direto para o fallback.

## 7. Geração de respostas

Quando há contexto suficiente, o `ResponseGenerator` (`src/rag/generator.py`) monta um prompt contendo:

- instruções de comportamento do agente;
- o contexto recuperado (chunks aprovados pelo Retriever);
- a pergunta do usuário;
- instrução explícita para responder **somente** com base no contexto, sem utilizar conhecimento externo do modelo.

A geração é feita via `GroqLLMProvider` (`src/llm/groq_provider.py`), que implementa a interface definida em `src/llm/base.py`. Quando `tem_contexto_suficiente = False`, o generator retorna a mensagem de fallback sem acionar o provider de LLM.

## 8. Controle contra alucinação

O sistema não elimina alucinações — nenhuma técnica isolada oferece essa garantia —, mas **reduz o risco de respostas não fundamentadas** por meio da combinação de:

- recuperação limitada por threshold de distância (0.8), que descarta resultados pouco relevantes;
- ausência de chamada ao LLM quando não há contexto suficiente (fallback);
- instrução explícita no prompt para não utilizar conhecimento externo ao contexto fornecido.

## 9. Fontes e rastreabilidade

Cada chunk recuperado carrega os metadados do documento de origem (`document_id`, `titulo`, `categoria`). O `ResponseGenerator` retorna essas fontes junto com a resposta gerada.

A interface (`src/interface/app.py`) exibe a lista de fontes consultadas, **deduplicadas por documento + categoria** — ou seja, se múltiplos chunks do mesmo documento e categoria forem utilizados, o documento aparece uma única vez na lista de fontes.

> Limitação atual: a atribuição de fontes ocorre em nível de documento, não por afirmação ou sentença específica da resposta.

## 10. Observabilidade

Cada execução é registrada em formato **JSON Lines**, via `src/observability/logger.py`. Cada linha do log contém:

```json
{
  "timestamp": "...",
  "pergunta": "...",
  "resposta": "...",
  "fontes": [],
  "teve_fallback": false
}
```

O arquivo de log é um artefato de runtime e **não é versionado** no Git.

## 11. Segurança e gerenciamento de segredos

- A chave `GROQ_API_KEY` é fornecida via variável de ambiente (`.env` local) ou via Streamlit Secrets em produção — nunca fica hardcoded no código-fonte.
- O repositório disponibiliza `.env.example` como modelo, sem valores reais.
- `.gitignore` exclui do versionamento: `.env`, `data/chroma_db/` e os arquivos de log (`*.jsonl`), além de caches e artefatos temporários do Python.
- A base documental utilizada é fictícia; em um cenário corporativo real, os documentos exigiriam classificação de sensibilidade e controle de acesso antes da indexação.

## 12. Interface

A interface (`src/interface/app.py`) foi construída com **Streamlit** e oferece:

- chat em linguagem natural;
- filtro opcional de busca por categoria;
- exibição das fontes consultadas para cada resposta;
- histórico da conversa na sessão;
- mecanismo de feedback positivo/negativo;
- identificação explícita de que o usuário está interagindo com uma IA.

## 13. Testes

O projeto conta com testes automatizados (`pytest`), organizados por módulo:

| Arquivo | Cobertura |
|---|---|
| `test_loaders.py` | Leitura correta de documentos (Markdown, CSV, JSON) |
| `test_chunking.py` | Tamanho dos chunks e preservação de metadados |
| `test_rag.py` | Recuperação dentro/fora do threshold, geração com contexto, retorno de fontes e comportamento de fallback (incluindo ausência de chamada ao LLM) |
| `test_logger.py` | Geração correta do arquivo JSONL e dos campos de auditoria |

Os testes do `ResponseGenerator` utilizam um provider de LLM simulado, evitando chamadas reais à API da Groq. A suíte está atualmente passando integralmente.

## 14. Deploy

A aplicação é implantada no **Streamlit Community Cloud**, com ponto de entrada:

```
src/interface/app.py
```

A `GROQ_API_KEY` é configurada via Streamlit Secrets no ambiente de produção. Como o armazenamento local do Streamlit Community Cloud é efêmero, a aplicação verifica se a coleção do ChromaDB está vazia na inicialização e, se necessário, reexecuta a ingestão automaticamente.

## 15. Limitações e decisões técnicas

- **Threshold fixo (0.8):** definido empiricamente; poderia ser refinado com um conjunto maior de perguntas avaliadas manualmente.
- **Citações em nível de documento:** ainda não há atribuição granular por chunk ou sentença.
- **Persistência efêmera:** ChromaDB e logs não são persistidos entre reinicializações no Streamlit Community Cloud.
- **Dependência externa:** a geração de respostas depende da disponibilidade da API da Groq.
- **Embeddings locais:** podem exigir download inicial do modelo na primeira execução do ambiente.
- **Sem autenticação:** a aplicação não implementa controle de acesso por usuário.

## 16. Conclusão

O NexusBank Agente IA implementa um pipeline RAG modular — ingestão, chunking, embeddings locais, armazenamento vetorial, recuperação com filtro de relevância, geração condicionada ao contexto e fallback controlado — com observabilidade e rastreabilidade de fontes. As decisões arquiteturais priorizam a separação de responsabilidades entre os módulos (`ingestion`, `embeddings`, `vectorstore`, `rag`, `llm`, `observability`, `interface`), permitindo a evolução independente de cada componente.
