"""DTOs de entrada e saida da API de autenticacao (camelCase, RNF-BE-11)."""

import re
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel

from meunegocio360_core.auth.application.dto import AuthResult, UsuarioDados
from meunegocio360_core.shared.config import PASSWORD_MAX, PASSWORD_MIN

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class LoginRequest(CamelModel):
    email: str = Field(max_length=160, examples=["admin@meunegocio360.com.br"])
    senha: str = Field(min_length=PASSWORD_MIN, max_length=PASSWORD_MAX, repr=False)

    @field_validator("email")
    @classmethod
    def _normalizar_email(cls, value: str) -> str:
        email = value.strip().lower()  # RN-01
        if not _EMAIL.match(email):
            raise ValueError("deve ser um e-mail válido")
        return email

    @field_validator("senha")
    @classmethod
    def _senha_ate_72_bytes(cls, value: str) -> str:
        if len(value.encode("utf-8")) > PASSWORD_MAX:  # limite do BCrypt (RN-11)
            raise ValueError(f"deve ter no máximo {PASSWORD_MAX} bytes")
        return value


class UsuarioResponse(CamelModel):
    id: UUID
    nome: str
    email: str
    perfil: str

    @classmethod
    def de(cls, dados: UsuarioDados) -> "UsuarioResponse":
        return cls(id=dados.id, nome=dados.nome, email=dados.email, perfil=dados.perfil)


class AuthResponse(CamelModel):
    token_type: str = "Bearer"
    access_token: str = Field(repr=False)
    expires_in: int
    usuario: UsuarioResponse

    @classmethod
    def de(cls, result: AuthResult) -> "AuthResponse":
        return cls(
            access_token=result.access_token,
            expires_in=result.expires_in,
            usuario=UsuarioResponse.de(result.usuario),
        )
