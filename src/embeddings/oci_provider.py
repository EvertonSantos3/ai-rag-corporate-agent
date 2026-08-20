"""
Embeddings via OCI Generative AI (cohere.embed-multilingual-v3.0).

Requer:
  pip install langchain-oci oci --break-system-packages
  oci setup config   (gera ~/.oci/config com suas credenciais)

Variáveis de ambiente esperadas (ver .env.example):
  OCI_COMPARTMENT_ID
  OCI_SERVICE_ENDPOINT  (ex: https://inference.generativeai.us-chicago-1.oci.oraclecloud.com)
  OCI_CONFIG_PROFILE     (opcional, default "DEFAULT")
"""
from __future__ import annotations

import os

from .base import EmbeddingProvider


class OCIEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self,
        model_id: str = "cohere.embed-multilingual-v3.0",
        service_endpoint: str | None = None,
        compartment_id: str | None = None,
    ):
        try:
            from langchain_oci import OCIGenAIEmbeddings
        except ImportError as e:
            raise ImportError(
                "langchain-oci é necessário: pip install langchain-oci oci --break-system-packages"
            ) from e

        self._client = OCIGenAIEmbeddings(
            model_id=model_id,
            service_endpoint=service_endpoint or os.environ["OCI_SERVICE_ENDPOINT"],
            compartment_id=compartment_id or os.environ["OCI_COMPARTMENT_ID"],
        )

    def embed_textos(self, textos: list[str]) -> list[list[float]]:
        return self._client.embed_documents(textos)
