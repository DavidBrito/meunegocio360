"""Repositorio e Unit of Work do cliente. Toda consulta filtra por `empresa_id` (RNF-096)."""

import re
from typing import Self
from uuid import UUID

from sqlalchemy import String, exists, func, literal, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm.exc import StaleDataError

from meunegocio360_core.cliente.domain.errors import (
    CustomerDocumentDuplicateError,
    VersionConflictError,
)
from meunegocio360_core.cliente.domain.models import Cliente, SituacaoFiltro, TipoPessoa
from meunegocio360_core.cliente.infra.models import ClienteModel
from meunegocio360_core.shared.busca import escape_like

# Restricoes do banco -> erro de negocio (RNF-BE-15: nunca um 500 generico).
_CONSTRAINTS = {"uk_cliente_empresa_documento": CustomerDocumentDuplicateError}

# Campos de ordenacao permitidos (nome do contrato -> coluna). `nome` usa a collation ci_ai.
_ORDENACAO = {"nome": ClienteModel.nome, "criadoEm": ClienteModel.criado_em}

_SO_DIGITOS_E_MASCARA = re.compile(r"[\d.\-/\s]+")


def _traduzir(exc: IntegrityError) -> Exception:
    constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
    erro = _CONSTRAINTS.get(constraint)
    return erro() if erro else exc


def _to_domain(model: ClienteModel) -> Cliente:
    return Cliente(
        id=model.id,
        empresa_id=model.empresa_id,
        tipo_pessoa=TipoPessoa(model.tipo_pessoa),
        nome=model.nome,
        documento=model.documento,
        email=model.email,
        telefone=model.telefone,
        ativo=model.ativo,
        criado_em=model.criado_em,
        atualizado_em=model.atualizado_em,
        versao=model.versao,
    )


def _filtro_busca(q: str | None):  # noqa: ANN202
    """RN-08. Nome: "contem", sem acento e sem caixa. Documento: prefixo dos digitos.

    O "contem" NAO pode usar a collation nao deterministica da coluna (o PostgreSQL nao
    suporta LIKE com ela, ADR 0006): normaliza-se com `lower(f_unaccent(...))` e compara-se
    com `COLLATE "default"`. O `q` vai como parametro vinculado, com curingas escapados.
    """
    texto = (q or "").strip()
    if not texto:
        return None
    termo = func.lower(func.f_unaccent(literal(escape_like(texto), String), type_=String))
    nome_normalizado = func.lower(func.f_unaccent(ClienteModel.nome, type_=String)).collate(
        '"default"'
    )
    condicoes = [nome_normalizado.like(func.concat("%", termo, "%"), escape="\\")]
    if _SO_DIGITOS_E_MASCARA.fullmatch(texto):
        digitos = re.sub(r"\D", "", texto)
        if digitos:
            condicoes.append(ClienteModel.documento.like(f"{digitos}%"))
    return or_(*condicoes)


class SqlAlchemyClienteRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(
        self, empresa_id: UUID, cliente_id: UUID, *, for_update: bool = False
    ) -> Cliente | None:
        statement = select(ClienteModel).where(
            ClienteModel.id == cliente_id, ClienteModel.empresa_id == empresa_id
        )
        if for_update:
            statement = statement.with_for_update().execution_options(populate_existing=True)
        model = self._session.scalar(statement)
        return _to_domain(model) if model else None

    def documento_exists(
        self, empresa_id: UUID, documento: str, *, excluding: UUID | None = None
    ) -> bool:
        condition = (ClienteModel.empresa_id == empresa_id) & (ClienteModel.documento == documento)
        if excluding is not None:
            condition = condition & (ClienteModel.id != excluding)
        return bool(self._session.scalar(select(exists().where(condition))))

    def search(
        self,
        empresa_id: UUID,
        *,
        q: str | None,
        situacao: SituacaoFiltro,
        offset: int,
        limit: int,
        sort_field: str,
        descending: bool,
    ) -> tuple[list[Cliente], int]:
        condicoes = [ClienteModel.empresa_id == empresa_id]
        if situacao is SituacaoFiltro.ATIVO:
            condicoes.append(ClienteModel.ativo.is_(True))
        elif situacao is SituacaoFiltro.INATIVO:
            condicoes.append(ClienteModel.ativo.is_(False))
        busca = _filtro_busca(q)
        if busca is not None:
            condicoes.append(busca)

        coluna = _ORDENACAO[sort_field]
        ordem = coluna.desc() if descending else coluna.asc()
        total = self._session.scalar(
            select(func.count()).select_from(ClienteModel).where(*condicoes)
        )
        statement = (
            select(ClienteModel)
            .where(*condicoes)
            .order_by(ordem, ClienteModel.id)  # `id` desempata: paginacao estavel
            .offset(offset)
            .limit(limit)
        )
        return [_to_domain(m) for m in self._session.scalars(statement)], int(total or 0)

    def add(self, cliente: Cliente) -> None:
        self._session.add(
            ClienteModel(
                id=cliente.id,
                empresa_id=cliente.empresa_id,
                tipo_pessoa=cliente.tipo_pessoa.value,
                nome=cliente.nome,
                documento=cliente.documento,
                email=cliente.email,
                telefone=cliente.telefone,
                ativo=cliente.ativo,
                criado_em=cliente.criado_em,
                atualizado_em=cliente.atualizado_em,
            )
        )

    def save(self, cliente: Cliente) -> None:
        model = self._session.get(ClienteModel, cliente.id)
        if model is None:
            raise LookupError("cliente inexistente")
        model.tipo_pessoa = cliente.tipo_pessoa.value
        model.nome = cliente.nome
        model.documento = cliente.documento
        model.email = cliente.email
        model.telefone = cliente.telefone
        model.ativo = cliente.ativo
        model.atualizado_em = cliente.atualizado_em
        try:
            self._session.flush()  # aplica o UPDATE (e o controle otimista) agora
        except IntegrityError as exc:
            raise _traduzir(exc) from None
        except StaleDataError:
            raise VersionConflictError from None
        cliente.versao = model.versao

    def delete(self, cliente: Cliente) -> None:
        model = self._session.get(ClienteModel, cliente.id)
        if model is not None:
            self._session.delete(model)


class SqlAlchemyClienteUnitOfWork:
    """Uma sessao/transacao por caso de uso; sem ``commit`` explicito, faz rollback."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None

    def __enter__(self) -> Self:
        self._session = self._session_factory()
        self.clientes = SqlAlchemyClienteRepository(self._session)
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
