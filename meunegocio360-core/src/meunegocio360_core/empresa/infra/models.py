"""Modelo SQLAlchemy da empresa. Nunca exposto na API (RNF-BE-02)."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CHAR,
    BigInteger,
    Boolean,
    CheckConstraint,
    Index,
    String,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from meunegocio360_core.shared.db import Base, UtcDateTime


class EmpresaModel(Base):
    __tablename__ = "empresa"
    __table_args__ = (
        UniqueConstraint("cnpj", name="uk_empresa_cnpj"),
        CheckConstraint("cnpj ~ '^[0-9]{14}$'", name="ck_empresa_cnpj_formato"),
        # No maximo uma empresa ativa, garantido pelo banco (RN-02).
        Index(
            "uk_empresa_ativa_unica", text("(true)"), unique=True, postgresql_where=text("ativa")
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    razao_social: Mapped[str] = mapped_column(String(150))
    nome_fantasia: Mapped[str | None] = mapped_column(String(150))
    cnpj: Mapped[str] = mapped_column(CHAR(14))
    email: Mapped[str | None] = mapped_column(String(160))
    telefone: Mapped[str | None] = mapped_column(String(11))
    fuso_horario: Mapped[str] = mapped_column(String(50), server_default="America/Sao_Paulo")
    moeda: Mapped[str] = mapped_column(CHAR(3), server_default="BRL")
    ativa: Mapped[bool] = mapped_column(Boolean, server_default="true")
    criado_em: Mapped[datetime] = mapped_column(UtcDateTime)
    atualizado_em: Mapped[datetime] = mapped_column(UtcDateTime)
    versao: Mapped[int] = mapped_column(BigInteger)

    # Controle otimista (RNF-BE-28). O contrato comeca em 0 (e vai a 1 na primeira edicao).
    __mapper_args__ = {
        "version_id_col": versao,
        "version_id_generator": lambda atual: 0 if atual is None else atual + 1,
    }

    def __repr__(self) -> str:
        return f"EmpresaModel(id={self.id})"
