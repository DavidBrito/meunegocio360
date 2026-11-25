"""Entidades de dominio do cliente (sem dependencia de framework, RNF-010)."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class TipoPessoa(StrEnum):
    FISICA = "FISICA"  # documento = CPF (11 digitos)
    JURIDICA = "JURIDICA"  # documento = CNPJ (14 digitos)


class SituacaoFiltro(StrEnum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    TODOS = "TODOS"


@dataclass(slots=True)
class DadosCliente:
    """Campos editaveis do cliente, ja validados e normalizados na borda."""

    tipo_pessoa: TipoPessoa
    nome: str
    documento: str  # so digitos
    email: str | None
    telefone: str | None


@dataclass(slots=True)
class Cliente:
    id: UUID
    empresa_id: UUID
    tipo_pessoa: TipoPessoa
    nome: str
    documento: str
    email: str | None
    telefone: str | None
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
    versao: int

    def atualizar(self, dados: DadosCliente, agora: datetime) -> None:
        self.tipo_pessoa = dados.tipo_pessoa
        self.nome = dados.nome
        self.documento = dados.documento
        self.email = dados.email
        self.telefone = dados.telefone
        self.atualizado_em = agora

    def definir_situacao(self, ativo: bool, agora: datetime) -> None:
        self.ativo = ativo
        self.atualizado_em = agora
