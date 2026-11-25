"""Modelo SQLAlchemy do cliente. Nunca exposto na API (RNF-BE-02)."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from meunegocio360_core.shared.db import Base, UtcDateTime


class ClienteModel(Base):
    __tablename__ = "cliente"
    __table_args__ = (
        ForeignKeyConstraint(["empresa_id"], ["empresa.id"], name="fk_cliente_empresa"),
        UniqueConstraint("empresa_id", "documento", name="uk_cliente_empresa_documento"),
        CheckConstraint("tipo_pessoa IN ('FISICA', 'JURIDICA')", name="ck_cliente_tipo_pessoa"),
        CheckConstraint(
            "(tipo_pessoa = 'FISICA' AND documento ~ '^[0-9]{11}$') "
            "OR (tipo_pessoa = 'JURIDICA' AND documento ~ '^[0-9]{14}$')",
            name="ck_cliente_documento",
        ),
        Index("idx_cliente_empresa_nome", "empresa_id", "nome"),
        Index("idx_cliente_empresa_ativo", "empresa_id", "ativo"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    empresa_id: Mapped[UUID] = mapped_column(Uuid)
    tipo_pessoa: Mapped[str] = mapped_column(String(10))
    # `ci_ai`: igualdade e ordenacao sem acento/caixa (ADR 0006). O "contem" NAO usa esta
    # collation (nao suporta LIKE): ver `repositories._filtro_busca`.
    nome: Mapped[str] = mapped_column(String(150, collation="ci_ai"))
    documento: Mapped[str] = mapped_column(String(14))
    email: Mapped[str | None] = mapped_column(String(160))
    telefone: Mapped[str | None] = mapped_column(String(11))
    ativo: Mapped[bool] = mapped_column(Boolean, server_default="true")
    criado_em: Mapped[datetime] = mapped_column(UtcDateTime)
    atualizado_em: Mapped[datetime] = mapped_column(UtcDateTime)
    versao: Mapped[int] = mapped_column(BigInteger)

    # Controle otimista (RNF-BE-28). O contrato comeca em 0 (e vai a 1 na primeira edicao).
    __mapper_args__ = {
        "version_id_col": versao,
        "version_id_generator": lambda atual: 0 if atual is None else atual + 1,
    }

    def __repr__(self) -> str:  # sem documento, e-mail nem telefone (RNF-025)
        return f"ClienteModel(id={self.id})"
