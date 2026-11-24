"""Entidades de dominio da autenticacao (sem dependencia de framework, RNF-010)."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import StrEnum
from uuid import UUID


class Perfil(StrEnum):
    # RF-BE-002 substitui USUARIO por OPERADOR_COMERCIAL e OPERADOR_FINANCEIRO.
    ADMIN = "ADMIN"
    USUARIO = "USUARIO"


@dataclass(slots=True)
class Usuario:
    id: UUID
    nome: str
    email: str
    senha_hash: str = field(repr=False)
    perfil: Perfil
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
    tentativas_falhas: int = 0
    bloqueado_ate: datetime | None = None
    ultimo_login_em: datetime | None = None

    def esta_bloqueado(self, agora: datetime) -> bool:
        return self.bloqueado_ate is not None and self.bloqueado_ate > agora

    def registrar_falha(self, agora: datetime, max_tentativas: int, bloqueio_minutos: int) -> bool:
        """Conta uma falha consecutiva (RN-04). Retorna True se a conta foi bloqueada agora."""
        self.tentativas_falhas += 1
        self.atualizado_em = agora
        if self.tentativas_falhas >= max_tentativas:
            self.bloqueado_ate = agora + timedelta(minutes=bloqueio_minutos)
            self.tentativas_falhas = 0
            return True
        return False

    def registrar_sucesso(self, agora: datetime) -> None:
        self.tentativas_falhas = 0
        self.bloqueado_ate = None
        self.ultimo_login_em = agora
        self.atualizado_em = agora


@dataclass(slots=True)
class RefreshToken:
    id: UUID
    usuario_id: UUID
    familia_id: UUID
    token_hash: str = field(repr=False)
    expira_em: datetime
    criado_em: datetime
    revogado_em: datetime | None = None

    @property
    def revogado(self) -> bool:
        return self.revogado_em is not None

    def expirado(self, agora: datetime) -> bool:
        return self.expira_em <= agora

    def revogar(self, agora: datetime) -> None:
        self.revogado_em = agora
