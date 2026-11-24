"""Modelos SQLAlchemy (persistencia). Nunca expostos na API (RNF-BE-02)."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CHAR,
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from meunegocio360_core.shared.db import Base, UtcDateTime


class UsuarioModel(Base):
    __tablename__ = "usuario"
    __table_args__ = (
        UniqueConstraint("email", name="uk_usuario_email"),
        CheckConstraint(
            "perfil IN ('ADMIN', 'OPERADOR_COMERCIAL', 'OPERADOR_FINANCEIRO')",
            name="ck_usuario_perfil",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(160))
    senha_hash: Mapped[str] = mapped_column(String(100))
    perfil: Mapped[str] = mapped_column(String(20))
    ativo: Mapped[bool] = mapped_column(Boolean, server_default="true")
    tentativas_falhas: Mapped[int] = mapped_column(Integer, server_default="0")
    bloqueado_ate: Mapped[datetime | None] = mapped_column(UtcDateTime)
    ultimo_login_em: Mapped[datetime | None] = mapped_column(UtcDateTime)
    criado_em: Mapped[datetime] = mapped_column(UtcDateTime)
    atualizado_em: Mapped[datetime] = mapped_column(UtcDateTime)
    versao: Mapped[int] = mapped_column(BigInteger)

    __mapper_args__ = {"version_id_col": versao}  # controle otimista (RNF-BE-22)

    def __repr__(self) -> str:  # sem senha_hash nem e-mail (RNF-023, RNF-025)
        return f"UsuarioModel(id={self.id})"


class RefreshTokenModel(Base):
    __tablename__ = "refresh_token"
    __table_args__ = (
        ForeignKeyConstraint(["usuario_id"], ["usuario.id"], name="fk_refresh_token_usuario"),
        UniqueConstraint("token_hash", name="uk_refresh_token_hash"),
        Index("ix_refresh_token_usuario_id", "usuario_id"),
        Index("ix_refresh_token_familia_id", "familia_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    usuario_id: Mapped[UUID] = mapped_column(Uuid)
    familia_id: Mapped[UUID] = mapped_column(Uuid)
    token_hash: Mapped[str] = mapped_column(CHAR(64))
    expira_em: Mapped[datetime] = mapped_column(UtcDateTime)
    revogado_em: Mapped[datetime | None] = mapped_column(UtcDateTime)
    criado_em: Mapped[datetime] = mapped_column(UtcDateTime)

    def __repr__(self) -> str:  # sem token_hash
        return f"RefreshTokenModel(id={self.id})"
