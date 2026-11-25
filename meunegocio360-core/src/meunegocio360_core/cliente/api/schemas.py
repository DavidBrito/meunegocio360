"""DTOs da API de clientes (camelCase, RNF-BE-11). A entidade nunca e exposta (RNF-BE-02)."""

import re
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from pydantic import Field, StringConstraints, ValidationInfo, field_validator

from meunegocio360_core.cliente.domain.models import Cliente, DadosCliente, TipoPessoa
from meunegocio360_core.shared.schemas import CamelModel
from meunegocio360_core.shared.validators import (
    is_valid_cnpj,
    is_valid_cpf,
    is_valid_email,
    somente_digitos,
)

_DOCUMENTO_COM_MASCARA = re.compile(r"[\d.\-/\s]+")


class ClientePayload(CamelModel):
    tipo_pessoa: TipoPessoa
    nome: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=150)]
    documento: Annotated[str, StringConstraints(strip_whitespace=True)] = Field(
        examples=["529.982.247-25"], description="CPF ou CNPJ, com ou sem máscara."
    )
    email: Annotated[str, StringConstraints(strip_whitespace=True, max_length=160)] | None = None
    telefone: Annotated[str, StringConstraints(strip_whitespace=True)] | None = Field(
        default=None, examples=["11987654321"], description="10 ou 11 dígitos, com DDD."
    )

    @field_validator("documento")
    @classmethod
    def _documento_valido(cls, valor: str, info: ValidationInfo) -> str:
        """Normaliza para so digitos (RNF-BE-27) e valida CPF/CNPJ conforme `tipoPessoa`."""
        if not _DOCUMENTO_COM_MASCARA.fullmatch(valor):
            raise ValueError("deve conter apenas dígitos, ponto, hífen e barra")
        digitos = somente_digitos(valor)
        tipo = info.data.get("tipo_pessoa")
        if tipo == TipoPessoa.FISICA:
            if len(digitos) != 11:
                raise ValueError("pessoa física exige CPF com 11 dígitos")
            if not is_valid_cpf(digitos):
                raise ValueError("CPF inválido")
        elif tipo == TipoPessoa.JURIDICA:
            if len(digitos) != 14:
                raise ValueError("pessoa jurídica exige CNPJ com 14 dígitos")
            if not is_valid_cnpj(digitos):
                raise ValueError("CNPJ inválido")
        return digitos

    @field_validator("email", "telefone")
    @classmethod
    def _opcional_em_branco_vira_none(cls, valor: str | None) -> str | None:
        return valor or None

    @field_validator("email")
    @classmethod
    def _email_valido(cls, valor: str | None) -> str | None:
        if valor is not None and not is_valid_email(valor):
            raise ValueError("deve ser um e-mail válido")
        return valor

    @field_validator("telefone")
    @classmethod
    def _telefone_valido(cls, valor: str | None) -> str | None:
        if valor is not None and not re.fullmatch(r"\d{10,11}", valor):
            raise ValueError("deve ter 10 ou 11 dígitos, sem máscara")
        return valor

    def para_dominio(self) -> DadosCliente:
        return DadosCliente(
            tipo_pessoa=self.tipo_pessoa,
            nome=self.nome,
            documento=self.documento,
            email=self.email,
            telefone=self.telefone,
        )


class ClienteAtualizacao(ClientePayload):
    versao: int = Field(ge=0, description="Versão lida (controle otimista, RNF-BE-28).")


class SituacaoPayload(CamelModel):
    ativo: bool
    versao: int = Field(ge=0, description="Versão lida (controle otimista, RNF-BE-28).")


class ClienteResponse(CamelModel):
    id: UUID
    tipo_pessoa: TipoPessoa
    nome: str
    documento: str
    email: str | None
    telefone: str | None
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
    versao: int

    @classmethod
    def de(cls, cliente: Cliente) -> "ClienteResponse":
        return cls(
            id=cliente.id,
            tipo_pessoa=cliente.tipo_pessoa,
            nome=cliente.nome,
            documento=cliente.documento,
            email=cliente.email,
            telefone=cliente.telefone,
            ativo=cliente.ativo,
            criado_em=cliente.criado_em.astimezone(UTC),  # sempre UTC (RNF-033)
            atualizado_em=cliente.atualizado_em.astimezone(UTC),
            versao=cliente.versao,
        )
