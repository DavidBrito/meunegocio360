"""Resultados dos casos de uso (independentes da camada web)."""

from dataclasses import dataclass
from uuid import UUID

from meunegocio360_core.auth.domain.models import Usuario


@dataclass(frozen=True, slots=True)
class UsuarioDados:
    id: UUID
    nome: str
    email: str
    perfil: str

    @classmethod
    def de(cls, usuario: Usuario) -> "UsuarioDados":
        return cls(usuario.id, usuario.nome, usuario.email, usuario.perfil.value)


@dataclass(frozen=True, slots=True)
class AuthResult:
    access_token: str
    expires_in: int
    usuario: UsuarioDados
    refresh_token: str
    refresh_max_age_seconds: int


@dataclass(frozen=True, slots=True)
class AuthConfig:
    max_tentativas: int
    bloqueio_minutos: int
    refresh_expiracao_dias: int
