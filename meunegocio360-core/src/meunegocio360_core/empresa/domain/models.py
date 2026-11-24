"""Entidade de dominio da empresa (sem dependencia de framework, RNF-010)."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class DadosEmpresa:
    """Campos editaveis da empresa (cadastro e edicao), ja validados na borda."""

    razao_social: str
    nome_fantasia: str | None
    cnpj: str
    email: str | None
    telefone: str | None
    fuso_horario: str
    moeda: str


@dataclass(slots=True)
class Empresa:
    id: UUID
    razao_social: str
    nome_fantasia: str | None
    cnpj: str
    email: str | None
    telefone: str | None
    fuso_horario: str
    moeda: str
    ativa: bool
    criado_em: datetime
    atualizado_em: datetime
    versao: int

    def atualizar(self, dados: DadosEmpresa, agora: datetime) -> None:
        self.razao_social = dados.razao_social
        self.nome_fantasia = dados.nome_fantasia
        self.cnpj = dados.cnpj
        self.email = dados.email
        self.telefone = dados.telefone
        self.fuso_horario = dados.fuso_horario
        self.moeda = dados.moeda
        self.atualizado_em = agora

    def definir_situacao(self, ativa: bool, agora: datetime) -> None:
        self.ativa = ativa
        self.atualizado_em = agora
