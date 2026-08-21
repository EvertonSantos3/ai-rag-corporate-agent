"""
Interface de chat NexusBank (etapa 6 do desafio) — tema escuro/neon.

Elementos exigidos pelo desafio, já presentes aqui:
  - indicação clara de que é um agente de IA;
  - exibição das fontes usadas em cada resposta;
  - botão de feedback (positivo/negativo) por resposta;
  - histórico de conversa dentro da sessão.

Rodar com: streamlit run src/interface/app.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Quando o Streamlit executa este arquivo diretamente (em vez de "python -m"),
# ele só adiciona a pasta deste arquivo ao sys.path, não a raiz do projeto.
# Isso garante que "from src.xxx import yyy" funcione de qualquer jeito que
# o script for chamado.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
from dotenv import load_dotenv

# Carrega variáveis de .env para o ambiente (só tem efeito localmente — no
# Streamlit Community Cloud não existe .env, as variáveis vêm de st.secrets).
load_dotenv()

from src.catalog.schema import Catalogo
from src.embeddings.local_provider import LocalEmbeddingProvider
from src.ingest_run import ingerir_catalogo
from src.llm.groq_provider import GroqLLMProvider
from src.observability.logger import registrar_execucao
from src.rag.generator import ResponseGenerator
from src.rag.retriever import Retriever
from src.vectorstore.chroma_store import ChromaVectorStore

st.set_page_config(page_title="NexusBank | Agente IA", page_icon="◆", layout="centered")

# ---------------------------------------------------------------------------
# Identidade visual: fundo azul-marinho quase preto + acento neon violeta.
# Único elemento de assinatura: o logo de "nós conectados" no cabeçalho.
# ---------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&display=swap');

:root {
    --bg: #0B0E14;
    --surface: #131722;
    --border: #232838;
    --text: #E8EAF0;
    --text-dim: #8B93A7;
    --accent: #7C5CFF;
    --accent-glow: rgba(124, 92, 255, 0.35);
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: radial-gradient(ellipse 80% 50% at 50% -10%, #171227 0%, var(--bg) 60%);
    color: var(--text);
}

/* Cabeçalho com o logo "nexus" */
.nx-header { display: flex; align-items: center; gap: 14px; margin-bottom: 4px; }
.nx-header h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 1.65rem;
    margin: 0;
    letter-spacing: -0.01em;
    color: var(--text);
}
.nx-header .nx-tag {
    color: var(--accent);
    font-family: 'Space Grotesk', sans-serif;
}
.nx-caption {
    color: var(--text-dim);
    font-size: 0.88rem;
    border-left: 2px solid var(--accent);
    padding-left: 10px;
    margin: 10px 0 22px 0;
    line-height: 1.5;
}

/* Balões de chat */
[data-testid="stChatMessage"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
}

/* Barra de entrada inteira (o Streamlit usa um container fixo na base da tela
   com fundo claro por padrão — sem isso, só o textarea ficava escuro e o
   resto da barra continuava branco, quebrando o contraste) */
[data-testid="stBottomBlockContainer"],
[data-testid="stChatInputContainer"],
.stChatFloatingInputContainer {
    background: var(--bg) !important;
}

/* Caixa de entrada */
[data-testid="stChatInput"] {
    background: var(--surface) !important;
    border-radius: 12px;
}
[data-testid="stChatInput"] textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    caret-color: var(--accent);
}
[data-testid="stChatInput"] textarea::placeholder {
    color: var(--text-dim) !important;
    opacity: 1 !important;
}
[data-testid="stChatInput"]:focus-within {
    box-shadow: 0 0 0 2px var(--accent-glow);
    border-radius: 12px;
}

/* Botões de feedback */
.stButton button {
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text);
    transition: border-color 0.15s ease;
}
.stButton button:hover {
    border-color: var(--accent);
    color: var(--accent);
}

/* Expander de fontes */
[data-testid="stExpander"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
}

/* Selectbox de categoria */
[data-testid="stSelectbox"] { color: var(--text); }
[data-testid="stSelectbox"] label { color: var(--text) !important; }
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: var(--surface) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}

/* Texto solto do Streamlit (labels, markdown simples) */
.stMarkdown, .stMarkdown p, label { color: var(--text) !important; }

/* Foco visível para acessibilidade (não removido) */
*:focus-visible { outline: 2px solid var(--accent) !important; outline-offset: 2px; }
</style>
"""

NEXUS_LOGO_SVG = """
<svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <g filter="url(#glow)">
    <line x1="8" y1="10" x2="20" y2="20" stroke="#7C5CFF" stroke-width="1.5"/>
    <line x1="32" y1="10" x2="20" y2="20" stroke="#7C5CFF" stroke-width="1.5"/>
    <line x1="8" y1="30" x2="20" y2="20" stroke="#7C5CFF" stroke-width="1.5"/>
    <line x1="32" y1="30" x2="20" y2="20" stroke="#7C5CFF" stroke-width="1.5"/>
    <circle cx="20" cy="20" r="4.5" fill="#7C5CFF"/>
    <circle cx="8" cy="10" r="2.5" fill="#E8EAF0"/>
    <circle cx="32" cy="10" r="2.5" fill="#E8EAF0"/>
    <circle cx="8" cy="30" r="2.5" fill="#E8EAF0"/>
    <circle cx="32" cy="30" r="2.5" fill="#E8EAF0"/>
  </g>
</svg>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_resource
def montar_pipeline():
    embedding_provider = LocalEmbeddingProvider()
    vector_store = ChromaVectorStore(embedding_provider=embedding_provider)
    if vector_store.count() == 0:
        # Primeira execução (ou container reiniciado sem disco persistente,
        # como no Streamlit Community Cloud): indexa automaticamente.
        with st.spinner("Preparando a base de conhecimento pela primeira vez..."):
            ingerir_catalogo(vector_store, verbose=False)
    retriever = Retriever(vector_store)
    generator = ResponseGenerator(llm_provider=GroqLLMProvider())
    return retriever, generator


def carregar_categorias() -> list[str]:
    dados = json.loads(Path("data/catalog/documents.json").read_text(encoding="utf-8"))
    return sorted({d["categoria"] for d in dados["documentos"]})


st.markdown(
    f'<div class="nx-header">{NEXUS_LOGO_SVG}<h1>Nexus<span class="nx-tag">Bank</span> · Agente IA</h1></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="nx-caption">⚠️ Você está conversando com um <strong>agente de inteligência '
    "artificial</strong>, não uma pessoa. As respostas são baseadas nos documentos internos "
    "indexados da NexusBank.</div>",
    unsafe_allow_html=True,
)

categoria_filtro = st.selectbox("Filtrar por categoria (opcional)", ["Todas"] + carregar_categorias())

if "historico" not in st.session_state:
    st.session_state.historico = []

try:
    retriever, generator = montar_pipeline()
except ValueError as e:
    st.error(f"⚠️ {e}")
    st.stop()

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

pergunta = st.chat_input("Pergunte algo sobre a NexusBank...")
if pergunta:
    categoria = None if categoria_filtro == "Todas" else categoria_filtro
    resultado_busca = retriever.buscar(pergunta, categoria=categoria)
    resposta = generator.gerar(pergunta, resultado_busca)
    registrar_execucao(pergunta, resposta.texto, resposta.fontes, resposta.teve_fallback)
    st.session_state.historico.append({"pergunta": pergunta, "resposta": resposta})
    st.rerun()

with st.sidebar:
    st.markdown("#### 📋 Log de execuções")
    st.caption("Registro de auditoria (etapa 8 do desafio)")
    from src.observability.logger import LOG_PATH

    if LOG_PATH.exists():
        linhas = LOG_PATH.read_text(encoding="utf-8").strip().splitlines()
        st.write(f"{len(linhas)} execuções registradas")
        with st.expander("Ver últimas 10"):
            for linha in linhas[-10:]:
                st.json(json.loads(linha), expanded=False)
    else:
        st.caption("Nenhuma execução registrada ainda.")
