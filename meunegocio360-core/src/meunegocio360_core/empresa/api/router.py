"""Endpoints da empresa (RF-BE-002). Controllers finos (RNF-BE-01)."""

from collections.abc import Iterator
from contextlib import contextmanager
from uuid import UUID

from fastapi import APIRouter, Depends, Response, Security

from meunegocio360_core.empresa.api.dependencies import (
    get_alterar_situacao_empresa,
    get_atualizar_empresa,
    get_cadastrar_empresa,
    get_obter_empresa_ativa,
)
from meunegocio360_core.empresa.api.schemas import (
    EmpresaAtualizacao,
    EmpresaPayload,
    EmpresaResponse,
    SituacaoPayload,
)
from meunegocio360_core.empresa.application.casos_de_uso import (
    AlterarSituacaoEmpresa,
    AtualizarEmpresa,
    CadastrarEmpresa,
    ObterEmpresaAtiva,
)
from meunegocio360_core.empresa.domain.errors import (
    CompanyAlreadyActiveError,
    CompanyCnpjDuplicateError,
    CompanyNotFoundError,
    CompanyNotRegisteredError,
    VersionConflictError,
)
from meunegocio360_core.shared.errors import AppError
from meunegocio360_core.shared.openapi import bearer_scheme, problem_responses
from meunegocio360_core.shared.perfil import Perfil
from meunegocio360_core.shared.security import require_perfis

router = APIRouter(prefix="/api/v1/empresa", tags=["Empresa"])

# Matriz de autorizacao (RF-BE-002): somente ADMIN escreve; qualquer autenticado consulta.
somente_admin = [Security(bearer_scheme), Depends(require_perfis(Perfil.ADMIN))]
autenticado = [Security(bearer_scheme)]

_NEGOCIO = {
    CompanyNotRegisteredError: (
        404,
        "COMPANY_NOT_REGISTERED",
        "Empresa não cadastrada",
        "Não existe empresa ativa. Faça o primeiro cadastro.",
    ),
    CompanyNotFoundError: (
        404,
        "COMPANY_NOT_FOUND",
        "Empresa não encontrada",
        "Nenhuma empresa corresponde ao identificador informado.",
    ),
    CompanyCnpjDuplicateError: (
        409,
        "COMPANY_CNPJ_DUPLICATE",
        "CNPJ já cadastrado",
        "Já existe uma empresa (ativa ou inativa) com este CNPJ.",
    ),
    CompanyAlreadyActiveError: (
        409,
        "COMPANY_ALREADY_ACTIVE",
        "Já existe empresa ativa",
        "Só pode haver uma empresa ativa. Inative a atual antes.",
    ),
    VersionConflictError: (
        409,
        "VERSION_CONFLICT",
        "Versão desatualizada",
        "O registro foi alterado por outra pessoa. Recarregue e tente novamente.",
    ),
}


@contextmanager
def _erros_de_negocio() -> Iterator[None]:
    """Traduz erros de dominio para `problem+json` com `code` estavel (RNF-BE-15)."""
    try:
        yield
    except tuple(_NEGOCIO) as exc:
        status, code, title, detail = _NEGOCIO[type(exc)]
        raise AppError(status, code, title, detail) from None


@router.get(
    "",
    response_model=EmpresaResponse,
    summary="Consulta a empresa ativa",
    description="Qualquer usuário autenticado pode consultar. `404` quando não há empresa ativa.",
    dependencies=autenticado,
    responses=problem_responses(
        (401, "UNAUTHORIZED", "Token de acesso ausente, inválido ou expirado."),
        (404, "COMPANY_NOT_REGISTERED", "Não existe empresa ativa. Faça o primeiro cadastro."),
    ),
)
def consultar(use_case: ObterEmpresaAtiva = Depends(get_obter_empresa_ativa)) -> EmpresaResponse:
    with _erros_de_negocio():
        return EmpresaResponse.de(use_case.execute())


@router.post(
    "",
    status_code=201,
    response_model=EmpresaResponse,
    summary="Cadastra a empresa (ADMIN)",
    description="A empresa nasce **ativa**. Só pode haver uma empresa ativa e o CNPJ é único.",
    dependencies=somente_admin,
    responses=problem_responses(
        (400, "VALIDATION_ERROR", "Um ou mais campos são inválidos."),
        (403, "ACCESS_DENIED", "Seu perfil não tem permissão para esta operação."),
        (409, "COMPANY_CNPJ_DUPLICATE", "Já existe uma empresa (ativa ou inativa) com este CNPJ."),
    ),
)
def cadastrar(
    body: EmpresaPayload,
    response: Response,
    use_case: CadastrarEmpresa = Depends(get_cadastrar_empresa),
) -> EmpresaResponse:
    with _erros_de_negocio():
        empresa = use_case.execute(body.para_dominio())
    response.headers["Location"] = "/api/v1/empresa"  # recurso: a empresa ativa
    return EmpresaResponse.de(empresa)


@router.put(
    "/{empresa_id}",
    response_model=EmpresaResponse,
    summary="Edita a empresa (ADMIN)",
    description="Exige a `versao` lida. O CNPJ pode mudar, respeitando a unicidade.",
    dependencies=somente_admin,
    responses=problem_responses(
        (400, "VALIDATION_ERROR", "Um ou mais campos são inválidos."),
        (403, "ACCESS_DENIED", "Seu perfil não tem permissão para esta operação."),
        (404, "COMPANY_NOT_FOUND", "Nenhuma empresa corresponde ao identificador informado."),
        (409, "VERSION_CONFLICT", "O registro foi alterado por outra pessoa."),
    ),
)
def atualizar(
    empresa_id: UUID,
    body: EmpresaAtualizacao,
    use_case: AtualizarEmpresa = Depends(get_atualizar_empresa),
) -> EmpresaResponse:
    with _erros_de_negocio():
        return EmpresaResponse.de(use_case.execute(empresa_id, body.para_dominio(), body.versao))


@router.patch(
    "/{empresa_id}/situacao",
    response_model=EmpresaResponse,
    summary="Inativa ou reativa a empresa (ADMIN)",
    description=(
        "A empresa nunca é excluída. Sem empresa ativa, as operações de negócio dos demais "
        "módulos respondem `422 COMPANY_NOT_ACTIVE`. Reativar com outra ativa dá `409`."
    ),
    dependencies=somente_admin,
    responses=problem_responses(
        (403, "ACCESS_DENIED", "Seu perfil não tem permissão para esta operação."),
        (404, "COMPANY_NOT_FOUND", "Nenhuma empresa corresponde ao identificador informado."),
        (409, "COMPANY_ALREADY_ACTIVE", "Só pode haver uma empresa ativa."),
    ),
)
def alterar_situacao(
    empresa_id: UUID,
    body: SituacaoPayload,
    use_case: AlterarSituacaoEmpresa = Depends(get_alterar_situacao_empresa),
) -> EmpresaResponse:
    with _erros_de_negocio():
        return EmpresaResponse.de(use_case.execute(empresa_id, body.ativa, body.versao))
