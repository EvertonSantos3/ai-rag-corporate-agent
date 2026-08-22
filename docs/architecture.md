# Arquitetura — NexusBank AI RAG

## 1. Visão geral

O NexusBank AI RAG é um agente de inteligência artificial corporativo baseado em Retrieval-Augmented Generation (RAG).

O sistema utiliza documentos internos estruturados em um catálogo, realiza ingestão e divisão dos documentos em chunks, gera embeddings locais, persiste os vetores em ChromaDB e recupera trechos semanticamente relevantes para fornecer contexto a um modelo de linguagem.

A aplicação possui uma interface de chat construída com Streamlit e registra as execuções em formato JSON Lines para permitir auditoria básica das interações.

O princípio central do sistema é:

> A resposta deve ser baseada exclusivamente no contexto recuperado da base de conhecimento. Quando não houver contexto suficiente, o agente deve utilizar um fallback em vez de inventar uma resposta.

---

## 2. Arquitetura em alto nível

```text
                    ┌──────────────────────────┐
                    │ data/catalog/             │
                    │ documents.json             │
                    │ Catálogo de documentos    │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │       Ingestion           │
                    │                          │
                    │ loaders → limpeza →       │
                    │ chunking                  │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ EmbeddingProvider         │
                    │                          │
                    │ Sentence Transformers     │
                    │ local / offline           │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ ChromaVectorStore         │
                    │                          │
                    │ ChromaDB                  │
                    │ cosine similarity         │
                    └────────────┬─────────────┘
                                 │
                                 │
Pergunta ────────────────────────┤
                                 ▼
                    ┌──────────────────────────┐
                    │ Retriever                │
                    │                          │
                    │ busca semântica           │
                    │ filtro por categoria     │
                    │ limiar de distância      │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ ResponseGenerator         │
                    │                          │
                    │ contexto + pergunta       │
                    │ fallback                  │
                    │ fontes                    │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ LLMProvider               │
                    │                          │
                    │ Groq / Anthropic          │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ Streamlit UI              │
                    │                          │
                    │ chat + fontes + feedback │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ Observability             │
                    │ logs/execucoes.jsonl     │
                    └──────────────────────────┘
3. Organização do projeto
ai-rag-corporate-agent/
├── data/
│   ├── catalog/
│   │   └── documents.json
│   ├── documents/
│   │   ├── atendimento/
│   │   ├── privacidade/
│   │   ├── seguranca/
│   │   ├── tarifas/
│   │   └── transacoes/
│   └── chroma_db/
│
├── docs/
│   └── architecture.md
│
├── src/
│   ├── catalog/
│   │   └── schema.py
│   ├── embeddings/
│   │   ├── base.py
│   │   └── local_provider.py
│   ├── ingestion/
│   │   ├── chunking.py
│   │   └── loaders.py
│   ├── interface/
│   │   └── app.py
│   ├── llm/
│   │   ├── base.py
│   │   ├── groq_provider.py
│   │   └── anthropic_provider.py
│   ├── observability/
│   │   └── logger.py
│   ├── rag/
│   │   ├── retriever.py
│   │   └── generator.py
│   ├── vectorstore/
│   │   └── chroma_store.py
│   └── ingest_run.py
│
└── tests/
4. Catálogo de documentos

O catálogo está localizado em:

data/catalog/documents.json

Ele funciona como fonte de metadados para os documentos utilizados pelo pipeline de ingestão.

Cada documento possui:

id
titulo
categoria
owner
versao
data_atualizacao
caminho_arquivo
formato
ativo

O modelo correspondente está implementado em:

src/catalog/schema.py
Categorias

Atualmente existem cinco categorias:

atendimento
privacidade
seguranca
tarifas
transacoes

O catálogo atual contém 20 documentos ativos.

O campo ativo determina quais documentos são considerados durante a ingestão.

5. Ingestão

O processo de ingestão é implementado em:

src/ingest_run.py

Fluxo:

documents.json
    ↓
Catalogo
    ↓
documentos ativos
    ↓
carregar_documento()
    ↓
limpeza e chunking
    ↓
embeddings
    ↓
ChromaDB

A função principal é:

ingerir_catalogo(vector_store)

Ela percorre os documentos ativos, carrega o conteúdo, cria os chunks e os envia ao vector store.

6. Loaders

Os loaders estão em:

src/ingestion/loaders.py

O sistema possui suporte aos seguintes formatos:

Markdown
CSV
JSON
HTML
PDF
DOCX
XLSX
PPTX

O ponto de entrada é:

carregar_documento(caminho)

A implementação seleciona o loader com base na extensão do arquivo.

Dependências específicas de alguns formatos são importadas sob demanda para manter o carregamento das dependências isolado.

7. Chunking

A divisão de documentos está implementada em:

src/ingestion/chunking.py

O processo:

normaliza espaços;
reduz linhas em branco excessivas;
tenta preservar parágrafos;
utiliza tamanho máximo de 800 caracteres;
utiliza sobreposição de 100 caracteres quando ocorre divisão por tamanho.

Cada chunk possui:

texto
indice
documento_id
metadata

Os metadados são preservados durante o processo para permitir rastreabilidade posteriormente.

8. Embeddings

A interface está definida em:

src/embeddings/base.py

através de:

EmbeddingProvider

A implementação atual utiliza:

src/embeddings/local_provider.py

com:

paraphrase-multilingual-MiniLM-L12-v2

O modelo funciona localmente e permite desenvolvimento sem dependência de serviço externo de embeddings.

A abstração EmbeddingProvider permite substituir a implementação sem acoplar diretamente o restante do pipeline ao modelo utilizado.

9. Vector Store

O vector store está implementado em:

src/vectorstore/chroma_store.py

A implementação utiliza ChromaDB persistente.

O índice é armazenado em:

data/chroma_db/

A coleção utiliza distância cosseno para comparação semântica.

Cada chunk indexado recebe:

documento_id
chunk_indice

além dos metadados provenientes do catálogo.

Os identificadores dos chunks seguem o padrão:

documento_id::indice

O armazenamento é local e não depende de um serviço de nuvem.

10. Recuperação

A camada de recuperação está implementada em:

src/rag/retriever.py

O Retriever utiliza o vector store para realizar busca semântica.

Configuração padrão:

top_k = 5
limiar de distância = 0.6

Também existe filtro opcional por categoria.

Como a métrica utilizada é distância, valores menores representam maior similaridade.

Os candidatos acima do limiar configurado são considerados pouco relevantes.

Quando nenhum candidato atende ao limiar, o sistema mantém os candidatos recuperados, mas sinaliza que não existe contexto suficiente para geração através de:

tem_contexto_suficiente = False

Essa sinalização é utilizada pela camada de geração para ativar o fallback.

11. Geração de respostas

A geração está implementada em:

src/rag/generator.py

A interface de LLM é:

src/llm/base.py

através de:

LLMProvider

Implementações disponíveis:

src/llm/groq_provider.py
src/llm/anthropic_provider.py

A implementação utilizada atualmente pela interface Streamlit é o provider da Groq.

O prompt instrui o modelo a:

utilizar somente o contexto recuperado;
não utilizar conhecimento externo;
informar quando o contexto não for suficiente;
citar as fontes utilizadas.
12. Fallback

Quando não existe contexto considerado suficiente, o sistema não envia a pergunta para geração normal.

Ele retorna uma mensagem de fallback:

Não encontrei essa informação nos documentos disponíveis.
Recomendo entrar em contato com a área responsável para mais detalhes.

O objeto de resposta também registra:

teve_fallback = True

Isso permite que a ocorrência seja registrada na camada de observabilidade.

13. Rastreabilidade das fontes

Cada chunk preserva informações do documento original.

As respostas possuem uma lista de fontes contendo:

documento
categoria

A interface Streamlit apresenta essas fontes em um expander associado à resposta.

O objetivo é permitir que o usuário identifique de quais documentos o contexto utilizado foi recuperado.

14. Interface

A interface está implementada em:

src/interface/app.py

e utiliza Streamlit.

A interface disponibiliza:

identificação explícita de que o usuário está conversando com um agente de IA;
campo de perguntas;
filtro opcional por categoria;
histórico da conversa durante a sessão;
exibição das fontes;
controles de feedback positivo/negativo;
painel lateral com registros de execução.

O pipeline é inicializado com st.cache_resource.

Caso o vector store esteja vazio, a aplicação realiza a ingestão automaticamente.

15. Observabilidade

A observabilidade básica está implementada em:

src/observability/logger.py

As execuções são registradas em:

logs/execucoes.jsonl

Cada linha representa uma execução e contém:

timestamp
pergunta
resposta
fontes
teve_fallback

O formato JSON Lines permite processamento posterior por ferramentas de análise de dados.

Os arquivos de log são considerados dados de runtime e não devem ser versionados no Git.

16. Configuração e segredos

Segredos locais são mantidos fora do controle de versão através de:

.env

O arquivo de exemplo é:

.env.example

A aplicação carrega variáveis locais através de python-dotenv.

No Streamlit Community Cloud, os segredos são configurados através de st.secrets.

A chave da Groq utilizada pelo provider é:

GROQ_API_KEY

Nenhuma chave real deve ser armazenada no repositório.

17. Estado persistente e arquivos gerados

O diretório:

data/chroma_db/

contém o índice vetorial gerado pelo ChromaDB.

Esse conteúdo é considerado estado/runtime e não deve ser versionado.

Da mesma forma:

logs/*.jsonl

representa registros gerados durante a execução e permanece fora do Git.

Os documentos-fonte e o catálogo, por outro lado, fazem parte da base de conhecimento do projeto e permanecem versionados.

18. Limitações e pontos de evolução

A arquitetura atual é adequada para desenvolvimento e demonstração, mas existem pontos que devem ser avaliados antes de um cenário de produção.

Sincronização do índice

A aplicação atualmente verifica se o vector store está vazio para decidir se deve executar a ingestão automática.

Essa estratégia não detecta, por si só:

documentos modificados;
documentos removidos;
documentos desativados;
alterações de versão;
alterações de metadados.

Uma estratégia futura deverá reconciliar o catálogo com o conteúdo efetivamente presente no vector store.

Documentos desativados

O catálogo suporta o campo ativo, mas a ingestão atual apenas deixa de processar documentos inativos.

É necessário garantir que chunks anteriormente indexados sejam removidos ou invalidados quando um documento deixar de ser ativo.

Observabilidade

O logging atual registra a pergunta, resposta, fontes e fallback.

Para ambientes de produção, podem ser adicionados:

duração da requisição;
modelo utilizado;
quantidade de chunks recuperados;
distâncias dos resultados;
identificador da execução;
erros;
versão da base de conhecimento.
Segurança contra prompt injection

O conteúdo recuperado dos documentos é inserido no contexto enviado ao LLM.

O sistema deverá ser avaliado contra instruções maliciosas presentes nos próprios documentos, além de entradas maliciosas fornecidas pelo usuário.

Caminhos de arquivos

Alguns caminhos são relativos ao diretório de execução.

Uma futura camada de configuração poderá centralizar a resolução dos caminhos da aplicação.

Feedback

A interface disponibiliza controles de feedback positivo e negativo, porém a persistência e utilização analítica desses eventos ainda precisam ser avaliadas.

19. Fluxo completo de uma consulta
Usuário
   │
   ▼
Streamlit
   │
   ▼
Pergunta + categoria opcional
   │
   ▼
Retriever
   │
   ▼
Embedding da pergunta
   │
   ▼
ChromaDB
   │
   ▼
Top-K chunks
   │
   ▼
Filtro por distância
   │
   ├── contexto insuficiente ──► Fallback
   │
   └── contexto suficiente
                │
                ▼
        ResponseGenerator
                │
                ▼
          Prompt + contexto
                │
                ▼
             LLMProvider
                │
                ▼
             Resposta
                │
        ┌───────┴────────┐
        ▼                ▼
      Fontes          Logger
20. Princípios arquiteturais

O projeto adota os seguintes princípios:

Separação de responsabilidades
Catálogo, ingestão, embeddings, armazenamento, recuperação, geração e interface são mantidos em módulos distintos.
Abstração de provedores
Embeddings e LLMs possuem interfaces que permitem substituir implementações.
Rastreabilidade
Os metadados do documento acompanham os chunks até a recuperação e apresentação das fontes.
Resposta fundamentada em contexto
O agente deve utilizar o contexto recuperado como base para suas respostas.
Fallback explícito
Ausência de contexto suficiente deve resultar em uma resposta controlada, e não em geração baseada em conhecimento externo.
Segregação de runtime
Índices vetoriais e logs gerados durante a execução não devem ser versionados.
Configuração externa de segredos
Chaves de API devem permanecer fora do código-fonte e do controle de versão.
