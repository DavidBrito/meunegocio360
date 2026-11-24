"""Repositorio e Unit of Work da empresa. Traduz violacoes do banco em erros de dominio."""

from typing import Self
from uuid import UUID

from sqlalchemy import exists, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm.exc import StaleDataError

from meunegocio360_core.empresa.domain.errors import (
    CompanyAlreadyActiveError,
    CompanyCnpjDuplicateError,
    VersionConflictError,
)
from meunegocio360_core.empresa.domain.models import Empresa
from meunegocio360_core.empresa.infra.models import EmpresaModel

# Nome das restricoes do banco -> erro de negocio (RNF-BE-15: nunca um 500 generico).
_CONSTRAINTS = {
    "uk_empresa_cnpj": CompanyCnpjDuplicateError,
    "uk_empresa_ativa_unica": CompanyAlreadyActiveError,
}


# Campos de ordenacao permitidos (nome do contrato -> coluna).
_ORDENACAO = {
    "atualizadoEm": EmpresaModel.atualizado_em,
    "razaoSocial": EmpresaModel.razao_social,
}


def _traduzir(exc: IntegrityError) -> Exception:
    """Converte a violacao de unicidade do banco no erro de negocio correspondente."""
    constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
    erro = _CONSTRAINTS.get(constraint)
    return erro() if erro else exc


def _to_domain(model: EmpresaModel) -> Empresa:
    return Empresa(
        id=model.id,
        razao_social=model.razao_social,
        nome_fantasia=model.nome_fantasia,
        cnpj=model.cnpj,
        email=model.email,
        telefone=model.telefone,
        fuso_horario=model.fuso_horario,
        moeda=model.moeda,
        ativa=model.ativa,
        criado_em=model.criado_em,
        atualizado_em=model.atualizado_em,
        versao=model.versao,
    )


class SqlAlchemyEmpresaRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_active(self) -> Empresa | None:
        model = self._session.scalar(select(EmpresaModel).where(EmpresaModel.ativa.is_(True)))
        return _to_domain(model) if model else None

    def get_by_id(self, empresa_id: UUID, *, for_update: bool = False) -> Empresa | None:
        statement = select(EmpresaModel).where(EmpresaModel.id == empresa_id)
        if for_update:
            statement = statement.with_for_update().execution_options(populate_existing=True)
        model = self._session.scalar(statement)
        return _to_domain(model) if model else None

    def cnpj_exists(self, cnpj: str, *, excluding: UUID | None = None) -> bool:
        condition = EmpresaModel.cnpj == cnpj
        if excluding is not None:
            condition = condition & (EmpresaModel.id != excluding)
        return bool(self._session.scalar(select(exists().where(condition))))

    def has_active(self, *, excluding: UUID | None = None) -> bool:
        condition = EmpresaModel.ativa.is_(True)
        if excluding is not None:
            condition = condition & (EmpresaModel.id != excluding)
        return bool(self._session.scalar(select(exists().where(condition))))

    def list_inactive(
        self, *, offset: int, limit: int, sort_field: str, descending: bool
    ) -> list[Empresa]:
        coluna = _ORDENACAO[sort_field]
        ordem = coluna.desc() if descending else coluna.asc()
        # `id` desempata: a paginacao fica estavel mesmo com valores repetidos.
        statement = (
            select(EmpresaModel)
            .where(EmpresaModel.ativa.is_(False))
            .order_by(ordem, EmpresaModel.id)
            .offset(offset)
            .limit(limit)
        )
        return [_to_domain(model) for model in self._session.scalars(statement)]

    def count_inactive(self) -> int:
        statement = (
            select(func.count()).select_from(EmpresaModel).where(EmpresaModel.ativa.is_(False))
        )
        return int(self._session.scalar(statement) or 0)

    def add(self, empresa: Empresa) -> None:
        self._session.add(
            EmpresaModel(
                id=empresa.id,
                razao_social=empresa.razao_social,
                nome_fantasia=empresa.nome_fantasia,
                cnpj=empresa.cnpj,
                email=empresa.email,
                telefone=empresa.telefone,
                fuso_horario=empresa.fuso_horario,
                moeda=empresa.moeda,
                ativa=empresa.ativa,
                criado_em=empresa.criado_em,
                atualizado_em=empresa.atualizado_em,
            )
        )

    def save(self, empresa: Empresa) -> None:
        model = self._session.get(EmpresaModel, empresa.id)
        if model is None:
            raise LookupError("empresa inexistente")
        model.razao_social = empresa.razao_social
        model.nome_fantasia = empresa.nome_fantasia
        model.cnpj = empresa.cnpj
        model.email = empresa.email
        model.telefone = empresa.telefone
        model.fuso_horario = empresa.fuso_horario
        model.moeda = empresa.moeda
        model.ativa = empresa.ativa
        model.atualizado_em = empresa.atualizado_em
        try:
            self._session.flush()  # aplica o UPDATE (e o controle otimista) agora
        except IntegrityError as exc:
            raise _traduzir(exc) from None
        except StaleDataError:
            raise VersionConflictError from None
        empresa.versao = model.versao


class SqlAlchemyEmpresaUnitOfWork:
    """Uma sessao/transacao por caso de uso; sem ``commit`` explicito, faz rollback."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None

    def __enter__(self) -> Self:
        self._session = self._session_factory()
        self.empresas = SqlAlchemyEmpresaRepository(self._session)
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
        try:
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise _traduzir(exc) from None
        except StaleDataError:
            self._session.rollback()
            raise VersionConflictError from None
