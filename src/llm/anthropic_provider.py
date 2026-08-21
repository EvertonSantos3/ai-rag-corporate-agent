"""
Geração via API da Anthropic (Claude).

Requer:
  pip install anthropic --break-system-packages

Variável de ambiente esperada: ANTHROPIC_API_KEY
  - Localmente: coloque em um arquivo .env (ver .env.example) e carregue com python-dotenv,
    ou exporte no terminal: export ANTHROPIC_API_KEY=sk-ant-...
  - No Streamlit Community Cloud: configure em "Settings > Secrets" do app, no formato:
      ANTHROPIC_API_KEY = "sk-ant-..."
"""
from __future__ import annotations

import os

from .base import LLMProvider


class ClaudeLLMProvider(LLMProvider):
    def __init__(self, model: str = "claude-sonnet-4-5", api_key: str | None = None, max_tokens: int = 1024):
        try:
            import anthropic
        except ImportError as e:
            raise ImportError("anthropic é necessário: pip install anthropic --break-system-packages") from e

        chave = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not chave:
            # Fallback para quando a app roda no Streamlit Community Cloud,
            # onde segredos ficam em st.secrets em vez de variáveis de ambiente.
            try:
                import streamlit as st

                chave = st.secrets.get("ANTHROPIC_API_KEY")
            except Exception:
                pass
        if not chave:
            raise ValueError(
                "ANTHROPIC_API_KEY não encontrada. Configure no .env (local) ou em "
                "Settings > Secrets do app (Streamlit Community Cloud)."
            )

        self._client = anthropic.Anthropic(api_key=chave)
        self._model = model
        self._max_tokens = max_tokens

    def gerar_resposta(self, prompt: str) -> str:
        resposta = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return resposta.content[0].text
