"""DTOs da API da empresa (camelCase, RNF-BE-11). A entidade nunca e exposta (RNF-BE-02)."""

import re
from datetime import UTC, datetime
from typing import Annotated, Literal
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import Field, StringConstraints, field_validator

from meunegocio360_core.empresa.domain.models import DadosEmpresa, Empresa
from meunegocio360_core.shared.schemas import CamelModel
from meunegocio360_core.shared.validators import is_valid_cnpj, is_valid_email

FUSO_PADRAO = "America/Sao_Paulo"
_CHAVE_IANA = re.compile(r"^[A-Za-z_]+(/[A-Za-z0-9_+-]+)*$")

# RN-06: campos de texto sofrem trim.
Texto = Annotated[str, StringConstraints(strip_whitespace=True)]


def _vazio_para_none(valor: str | None) -> str | None:
    return valor or None


class EmpresaPayload(CamelModel):
    razao_social: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=3, max_length=150)
    ]
    nome_fantasia: (
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=150)] | None
    ) = None
    cnpj: Texto = Field(examples=["11222333000181"])
    email: Annotated[str, StringConstraints(strip_whitespace=True, max_length=160)] | None = None
    telefone: Texto | None = Field(default=None, examples=["11987654321"])
    fuso_horario: Texto = Field(default=FUSO_PADRAO, examples=[FUSO_PADRAO])
    moeda: Literal["BRL"] = "BRL"  # nesta fase somente BRL (RN-05)

    @field_validator("nome_fantasia", "email", "telefone")
    @classmethod
    def _opcional_em_branco_vira_none(cls, valor: str | None) -> str | None:
        return _vazio_para_none(valor)

    @field_validator("cnpj")
    @classmethod
    def _cnpj_valido(cls, valor: str) -> str:
        # Armazenado e trafegado so com digitos; a mascara e do frontend (RNF-BE-27).
        if not re.fullmatch(r"\d{14}", valor):
            raise ValueError("deve ter 14 dígitos, sem máscara")
        if not is_valid_cnpj(valor):
            raise ValueError("CNPJ inválido")
        return valor

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

    @field_validator("fuso_horario")
    @classmethod
    def _fuso_iana(cls, valor: str) -> str:
        # Identificador IANA valido (RN-05); a chave e checada antes para evitar caminhos.
        if _CHAVE_IANA.fullmatch(valor):
            try:
                ZoneInfo(valor)
                return valor
            except (KeyError, ValueError, OSError):
                pass
        raise ValueError("deve ser um fuso horário IANA válido (ex.: America/Sao_Paulo)")

    def para_dominio(self) -> DadosEmpresa:
        return DadosEmpresa(
            razao_social=self.razao_social,
            nome_fantasia=self.nome_fantasia,
            cnpj=self.cnpj,
            email=self.email,
            telefone=self.telefone,
            fuso_horario=self.fuso_horario,
            moeda=self.moeda,
        )


class EmpresaAtualizacao(EmpresaPayload):
    versao: int = Field(ge=0, description="Versão lida (controle otimista, RNF-BE-28).")


class SituacaoPayload(CamelModel):
    ativa: bool
    versao: int = Field(ge=0, description="Versão lida (controle otimista, RNF-BE-28).")


class EmpresaResponse(CamelModel):
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

    @classmethod
    def de(cls, empresa: Empresa) -> "EmpresaResponse":
        return cls(
            id=empresa.id,
            razao_social=empresa.razao_social,
            nome_fantasia=empresa.nome_fantasia,
            cnpj=empresa.cnpj,
            email=empresa.email,
            telefone=empresa.telefone,
            fuso_horario=empresa.fuso_horario,
            moeda=empresa.moeda,
            ativa=empresa.ativa,
            criado_em=empresa.criado_em.astimezone(UTC),  # sempre UTC (RNF-033)
            atualizado_em=empresa.atualizado_em.astimezone(UTC),
            versao=empresa.versao,
        )
