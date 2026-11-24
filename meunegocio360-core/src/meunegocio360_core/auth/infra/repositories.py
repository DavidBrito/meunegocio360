"""Repositorios SQLAlchemy e Unit of Work (fronteira transacional, RNF-BE-04)."""

from datetime import datetime
from typing import Self
from uuid import UUID

from sqlalchemy import delete, or_, select, update
from sqlalchemy.orm import Session, sessionmaker

from meunegocio360_core.auth.domain.models import Perfil, RefreshToken, Usuario
from meunegocio360_core.auth.infra.models import RefreshTokenModel, UsuarioModel


def _usuario_to_domain(model: UsuarioModel) -> Usuario:
    return Usuario(
        id=model.id,
        nome=model.nome,
        email=model.email,
        senha_hash=model.senha_hash,
        perfil=Perfil(model.perfil),
        ativo=model.ativo,
        criado_em=model.criado_em,
        atualizado_em=model.atualizado_em,
        tentativas_falhas=model.tentativas_falhas,
        bloqueado_ate=model.bloqueado_ate,
        ultimo_login_em=model.ultimo_login_em,
    )


def _refresh_to_domain(model: RefreshTokenModel) -> RefreshToken:
    return RefreshToken(
        id=model.id,
        usuario_id=model.usuario_id,
        familia_id=model.familia_id,
        token_hash=model.token_hash,
        expira_em=model.expira_em,
        criado_em=model.criado_em,
        revogado_em=model.revogado_em,
    )


class SqlAlchemyUsuarioRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _find(self, *conditions, for_update: bool) -> Usuario | None:
        statement = select(UsuarioModel).where(*conditions)
        if for_update:
            # populate_existing: ao travar, o estado em memoria e relido do banco.
            statement = statement.with_for_update().execution_options(populate_existing=True)
        model = self._session.scalar(statement)
        return _usuario_to_domain(model) if model else None

    def get_by_email(self, email: str, *, for_update: bool = False) -> Usuario | None:
        return self._find(UsuarioModel.email == email, for_update=for_update)

    def get_by_id(self, usuario_id: UUID, *, for_update: bool = False) -> Usuario | None:
        return self._find(UsuarioModel.id == usuario_id, for_update=for_update)

    def add(self, usuario: Usuario) -> None:
        self._session.add(
            UsuarioModel(
                id=usuario.id,
                nome=usuario.nome,
                email=usuario.email,
                senha_hash=usuario.senha_hash,
                perfil=usuario.perfil.value,
                ativo=usuario.ativo,
                tentativas_falhas=usuario.tentativas_falhas,
                bloqueado_ate=usuario.bloqueado_ate,
                ultimo_login_em=usuario.ultimo_login_em,
                criado_em=usuario.criado_em,
                atualizado_em=usuario.atualizado_em,
            )
        )

    def save(self, usuario: Usuario) -> None:
        model = self._session.get(UsuarioModel, usuario.id)
        if model is None:
            raise LookupError("usuario inexistente")
        model.nome = usuario.nome
        model.senha_hash = usuario.senha_hash
        model.perfil = usuario.perfil.value
        model.ativo = usuario.ativo
        model.tentativas_falhas = usuario.tentativas_falhas
        model.bloqueado_ate = usuario.bloqueado_ate
        model.ultimo_login_em = usuario.ultimo_login_em
        model.atualizado_em = usuario.atualizado_em


class SqlAlchemyRefreshTokenRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        model = self._session.scalar(
            select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash)
        )
        return _refresh_to_domain(model) if model else None

    def get_by_hash_for_update(self, token_hash: str) -> RefreshToken | None:
        model = self._session.scalar(
            select(RefreshTokenModel)
            .where(RefreshTokenModel.token_hash == token_hash)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return _refresh_to_domain(model) if model else None

    def add(self, token: RefreshToken) -> None:
        self._session.add(
            RefreshTokenModel(
                id=token.id,
                usuario_id=token.usuario_id,
                familia_id=token.familia_id,
                token_hash=token.token_hash,
                expira_em=token.expira_em,
                revogado_em=token.revogado_em,
                criado_em=token.criado_em,
            )
        )

    def save(self, token: RefreshToken) -> None:
        model = self._session.get(RefreshTokenModel, token.id)
        if model is None:
            raise LookupError("refresh token inexistente")
        model.revogado_em = token.revogado_em

    def revoke_family(self, familia_id: UUID, agora: datetime) -> None:
        self._session.execute(
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.familia_id == familia_id, RefreshTokenModel.revogado_em.is_(None)
            )
            .values(revogado_em=agora)
        )

    def revoke_active_of_user(self, usuario_id: UUID, agora: datetime) -> None:
        self._session.execute(
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.usuario_id == usuario_id, RefreshTokenModel.revogado_em.is_(None)
            )
            .values(revogado_em=agora)
        )

    def delete_older_than(self, limite: datetime) -> int:
        result = self._session.execute(
            delete(RefreshTokenModel).where(
                or_(RefreshTokenModel.expira_em < limite, RefreshTokenModel.revogado_em < limite)
            )
        )
        return result.rowcount or 0


class SqlAlchemyUnitOfWork:
    """Uma sessao e uma transacao por caso de uso; sem ``commit`` explicito, faz rollback."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None

    def __enter__(self) -> Self:
        self._session = self._session_factory()
        self.usuarios = SqlAlchemyUsuarioRepository(self._session)
        self.refresh_tokens = SqlAlchemyRefreshTokenRepository(self._session)
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        assert self._session is not None
        try:
            if exc_type is not None:
                self._session.rollback()
        finally:
            self._session.close()

    def commit(self) -> None:
        assert self._session is not None
        self._session.commit()
