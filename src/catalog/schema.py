"""
Schema do catálogo de documentos.

Cada documento indexado na base precisa aparecer aqui com seus metadados,
conforme definido em docs/architecture.md (etapa 1 do desafio: coleta e
organização de documentos).
"""
from __future__ import annotations

from datetime import date
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class Categoria(str, Enum):
    ATENDIMENTO = "atendimento"
    PRIVACIDADE = "privacidade"
    SEGURANCA = "seguranca"
    TARIFAS = "tarifas"
    TRANSACOES = "transacoes"


class DocumentoMetadata(BaseModel):
    """Metadados de um documento na base de conhecimento."""

    id: str = Field(..., description="Identificador único do documento")
    titulo: str = Field(..., description="Título legível do documento")
    categoria: Categoria = Field(..., description="Categoria de negócio")
    owner: str = Field(..., description="Área responsável (ex: Jurídico, Segurança, Produto)")
    versao: str = Field(default="1.0", description="Versão do documento")
    data_atualizacao: date = Field(..., description="Data da última revisão")
    caminho_arquivo: str = Field(..., description="Caminho relativo em data/documents/")
    formato: str = Field(..., description="Extensão do arquivo original (pdf, docx, md, etc.)")
    ativo: bool = Field(default=True, description="Se False, é ignorado na ingestão (versão desatualizada)")

    def caminho_absoluto(self, base_dir: Path) -> Path:
        return base_dir / self.caminho_arquivo


class Catalogo(BaseModel):
    """Coleção de documentos, espelha data/catalog/documents.json."""

    documentos: list[DocumentoMetadata]

    def por_categoria(self, categoria: Categoria) -> list[DocumentoMetadata]:
        return [d for d in self.documentos if d.categoria == categoria and d.ativo]

    def ativos(self) -> list[DocumentoMetadata]:
        return [d for d in self.documentos if d.ativo]
