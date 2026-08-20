"""
Geração via OCI Generative AI (modelo Cohere Command R+ por padrão).

Requer as mesmas credenciais/instalação descritas em embeddings/oci_provider.py.
"""
from __future__ import annotations

import os

from .base import LLMProvider


class OCILLMProvider(LLMProvider):
    def __init__(
        self,
        model_id: str = "cohere.command-r-plus",
        service_endpoint: str | None = None,
        compartment_id: str | None = None,
        temperatura: float = 0.2,
    ):
        try:
            from langchain_oci import ChatOCIGenAI
        except ImportError as e:
            raise ImportError(
                "langchain-oci é necessário: pip install langchain-oci oci --break-system-packages"
            ) from e

        self._client = ChatOCIGenAI(
            model_id=model_id,
            service_endpoint=service_endpoint or os.environ["OCI_SERVICE_ENDPOINT"],
            compartment_id=compartment_id or os.environ["OCI_COMPARTMENT_ID"],
            model_kwargs={"temperature": temperatura},
        )

    def gerar_resposta(self, prompt: str) -> str:
        resposta = self._client.invoke(prompt)
        return resposta.content
