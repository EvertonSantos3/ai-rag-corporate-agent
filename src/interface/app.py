"""
Interface de chat simples em Streamlit (etapa 6 do desafio).

Elementos exigidos pelo desafio, já presentes aqui:
  - indicação clara de que é um agente de IA;
  - exibição das fontes usadas em cada resposta;
  - botão de feedback (positivo/negativo) por resposta;
  - histórico de conversa dentro da sessão.

Rodar com: streamlit run src/interface/app.py
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from src.catalog.schema import Catalogo
from src.embeddings.local_provider import LocalEmbeddingProvider
from src.llm.mock_provider import MockLLMProvider
from src.rag.generator import ResponseGenerator
from src.rag.retriever import Retriever
from src.vectorstore.chroma_store import ChromaVectorStore

st.set_page_config(page_title="Agente Corporativo (RAG)", page_icon="🤖")


@st.cache_resource
def montar_pipeline():
    # Troque LocalEmbeddingProvider -> OCIEmbeddingProvider e
    # MockLLMProvider -> OCILLMProvider quando a conta OCI estiver pronta.
    embedding_provider = LocalEmbeddingProvider()
    vector_store = ChromaVectorStore(embedding_provider=embedding_provider)
    retriever = Retriever(vector_store)
    generator = ResponseGenerator(llm_provider=MockLLMProvider())
    return retriever, generator


def carregar_categorias() -> list[str]:
    dados = json.loads(Path("data/catalog/documents.json").read_text(encoding="utf-8"))
    return sorted({d["categoria"] for d in dados["documentos"]})


st.title("🤖 Agente Corporativo")
st.caption(
    "⚠️ Você está conversando com um **agente de inteligência artificial**, "
    "não uma pessoa. As respostas são baseadas nos documentos internos indexados."
)

categoria_filtro = st.selectbox("Filtrar por categoria (opcional)", ["Todas"] + carregar_categorias())

if "historico" not in st.session_state:
    st.session_state.historico = []

retriever, generator = montar_pipeline()

for i, item in enumerate(st.session_state.historico):
    with st.chat_message("user"):
        st.write(item["pergunta"])
    with st.chat_message("assistant"):
        st.write(item["resposta"].texto)
        if item["resposta"].fontes:
            with st.expander("📎 Fontes"):
                for f in item["resposta"].fontes:
                    st.write(f"- {f['documento']} ({f['categoria']})")
        col1, col2 = st.columns(2)
        col1.button("👍", key=f"up_{i}")
        col2.button("👎", key=f"down_{i}")

pergunta = st.chat_input("Digite sua pergunta...")
if pergunta:
    categoria = None if categoria_filtro == "Todas" else categoria_filtro
    resultado_busca = retriever.buscar(pergunta, categoria=categoria)
    resposta = generator.gerar(pergunta, resultado_busca)
    st.session_state.historico.append({"pergunta": pergunta, "resposta": resposta})
    st.rerun()
