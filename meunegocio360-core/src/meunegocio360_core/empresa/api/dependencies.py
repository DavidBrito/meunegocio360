"""Composicao da feature empresa e o mecanismo `EmpresaAtiva` para as demais features."""

from uuid import UUID

from fastapi import Depends

from meunegocio360_core.empresa.application.casos_de_uso import (
    AlterarSituacaoEmpresa,
    AtualizarEmpresa,
    CadastrarEmpresa,
    ListarEmpresasInativas,
    ObterEmpresaAtiva,
)
from meunegocio360_core.empresa.application.empresa_ativa import EmpresaAtiva
from meunegocio360_core.empresa.domain.errors import CompanyNotActiveError
from meunegocio360_core.empresa.infra.repositories import SqlAlchemyEmpresaUnitOfWork
from meunegocio360_core.shared.clock import SystemClock
from meunegocio360_core.shared.db import get_session_factory
from meunegocio360_core.shared.errors import AppError
from meunegocio360_core.shared.openapi import problem_responses

# Resposta a documentar (`responses=`) em toda rota que dependa de `empresa_ativa_id`.
EMPRESA_ATIVA_RESPONSES = problem_responses(
    (422, "COMPANY_NOT_ACTIVE", "Não existe empresa ativa. Cadastre ou reative a empresa.")
)


def uow_factory() -> SqlAlchemyEmpresaUnitOfWork:
    return SqlAlchemyEmpresaUnitOfWork(get_session_factory())


def get_obter_empresa_ativa() -> ObterEmpresaAtiva:
    return ObterEmpresaAtiva(uow_factory)


def get_listar_empresas_inativas() -> ListarEmpresasInativas:
    return ListarEmpresasInativas(uow_factory)


def get_cadastrar_empresa() -> CadastrarEmpresa:
    return CadastrarEmpresa(uow_factory, SystemClock())


def get_atualizar_empresa() -> AtualizarEmpresa:
    return AtualizarEmpresa(uow_factory, SystemClock())


def get_alterar_situacao_empresa() -> AlterarSituacaoEmpresa:
    return AlterarSituacaoEmpresa(uow_factory, SystemClock())


def get_empresa_ativa() -> EmpresaAtiva:
    return EmpresaAtiva(uow_factory)


def empresa_ativa_id(componente: EmpresaAtiva = Depends(get_empresa_ativa)) -> UUID:
    """Dependencia para os demais requisitos: o `empresa_id` e resolvido no servidor (RNF-096).

    Sem empresa ativa, responde `422 COMPANY_NOT_ACTIVE`. Documente a rota com
    `responses=EMPRESA_ATIVA_RESPONSES`.
    """
    try:
        return componente.id()
    except CompanyNotActiveError:
        raise AppError(
            422,
            "COMPANY_NOT_ACTIVE",
            "Empresa não ativa",
            "Não existe empresa ativa. Cadastre ou reative a empresa antes de continuar.",
        ) from None
