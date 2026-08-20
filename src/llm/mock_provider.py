"""
LLM "mock" — não gera texto de fato, apenas devolve o contexto recuperado
de forma estruturada. Serve para testar a canalização completa
(ingestão -> retrieval -> resposta) sem gastar nenhuma chamada de API
enquanto a conta OCI não está pronta.

Troque por OCILLMProvider assim que tiver credenciais.
"""
from __future__ import annotations

from .base import LLMProvider


class MockLLMProvider(LLMProvider):
    def gerar_resposta(self, prompt: str) -> str:
        return (
            "[RESPOSTA SIMULADA - MockLLMProvider]\n"
            "Este é um retorno de teste. O prompt completo que seria enviado "
            "a um LLM real está abaixo, incluindo o contexto recuperado:\n\n"
            f"{prompt}"
        )
