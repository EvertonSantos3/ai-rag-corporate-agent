"""
Geração via API da Groq — inferência gratuita, sem necessidade de cartão
de crédito (30 requisições/min, 14.400/dia no free tier).

Requer:
  pip install groq --break-system-packages

Variável de ambiente esperada: GROQ_API_KEY
  - Crie sua chave gratuita em https://console.groq.com/keys
  - Localmente: coloque em .env (ver .env.example)
  - No Streamlit Community Cloud: configure em "Settings > Secrets", no formato:
      GROQ_API_KEY = "gsk_..."
"""
from __future__ import annotations

import os

from .base import LLMProvider


class GroqLLMProvider(LLMProvider):
    def __init__(self, model: str = "openai/gpt-oss-20b", api_key: str | None = None, max_tokens: int = 1024):
        try:
            from groq import Groq
        except ImportError as e:
            raise ImportError("groq é necessário: pip install groq --break-system-packages") from e

        chave = api_key or os.environ.get("GROQ_API_KEY")
        if not chave:
            # Fallback para quando a app roda no Streamlit Community Cloud,
            # onde segredos ficam em st.secrets em vez de variáveis de ambiente.
            try:
                import streamlit as st

                chave = st.secrets.get("GROQ_API_KEY")
            except Exception:
                pass
        if not chave:
            raise ValueError(
                "GROQ_API_KEY não encontrada. Crie uma chave grátis em "
                "console.groq.com/keys e configure no .env (local) ou em "
                "Settings > Secrets do app (Streamlit Community Cloud)."
            )

        self._client = Groq(api_key=chave)
        self._model = model
        self._max_tokens = max_tokens

    def gerar_resposta(self, prompt: str) -> str:
        resposta = self._client.chat.completions.create(
            model=self._model,
            max_tokens=self._max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return resposta.choices[0].message.content
