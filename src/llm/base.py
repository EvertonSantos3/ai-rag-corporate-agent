"""Interface de LLM de geração — mesma lógica de troca de backend dos embeddings."""
from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def gerar_resposta(self, prompt: str) -> str:
        """Recebe o prompt completo (pergunta + contexto) e devolve a resposta gerada."""
