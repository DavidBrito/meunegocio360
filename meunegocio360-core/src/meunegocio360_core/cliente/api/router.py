"""Endpoints de clientes (RF-BE-003). Controllers finos (RNF-BE-01)."""

from collections.abc import Iterator
from contextlib import contextmanager
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, Security

from meunegocio360_core.cliente.api.dependencies import (
    get_alterar_situacao_cliente,
    get_atualizar_cliente,
    get_cadastrar_cliente,
    get_excluir_cliente,
    get_listar_clientes,
    get_obter_cliente,
)
from meunegocio360_core.cliente.api.schemas import (
    ClienteAtualizacao,
    ClientePayload,
    ClienteResponse,
    SituacaoPayload,
)
from meunegocio360_core.cliente.application.casos_de_uso import (
    AlterarSituacaoCliente,
    AtualizarCliente,
    CadastrarCliente,
    ExcluirCliente,
    ListarClientes,
    ObterCliente,
)
from meunegocio360_core.cliente.domain.errors import (
    CustomerDocumentDuplicateError,
    CustomerHasHistoryError,
    CustomerNotFoundError,
    VersionConflictError,
)
from meunegocio360_core.cliente.domain.models import SituacaoFiltro
from meunegocio360_core.empresa import EMPRESA_ATIVA_RESPONSES, empresa_ativa_id
from meunegocio360_core.shared.errors import AppError
from meunegocio360_core.shared.openapi import bearer_scheme, problem_responses
from meunegocio360_core.shared.pagination import Page, PageParams, page_params
from meunegocio360_core.shared.perfil import Perfil
from meunegocio360_core.shared.security import require_perfis

router = APIRouter(prefix="/api/v1/clientes", tags=["Clientes"])

# Matriz de autorizacao (RF-BE-003): ADMIN e OPERADOR_COMERCIAL; o financeiro recebe 403.
# O perfil e conferido ANTES da empresa ativa (dependencias do router rodam primeiro).
acesso = [
    Security(bearer_scheme),
    Depends(require_perfis(Perfil.ADMIN, Perfil.OPERADOR_COMERCIAL)),
]

_PERMISSAO = (403, "ACCESS_DENIED", "Seu perfil não tem permissão para esta operação.")
_NAO_ENCONTRADO = (404, "CUSTOMER_NOT_FOUND", "Cliente não encontrado na empresa ativa.")
_NEGOCIO = {
    CustomerNotFoundError: (
        404,
        "CUSTOMER_NOT_FOUND",
        "Cliente não encontrado",
        "Nenhum cliente da empresa ativa corresponde ao identificador informado.",
    ),
    CustomerDocumentDuplicateError: (
        409,
        "CUSTOMER_DOCUMENT_DUPLICATE",
        "Documento já cadastrado",
        "Já existe um cliente com este documento nesta empresa (ele pode estar inativo).",
    ),
    CustomerHasHistoryError: (
        422,
        "CUSTOMER_HAS_HISTORY",
        "Cliente com histórico",
        "O cliente possui vendas ou ordens de serviço vinculadas e não pode ser excluído. "
        "Inative o cliente.",
    ),
    VersionConflictError: (
        409,
        "VERSION_CONFLICT",
        "Versão desatualizada",
        "O registro foi alterado por outra pessoa. Recarregue e tente novamente.",
    ),
}

# Ordenacao permitida da listagem (RNF-BE-16): so estes campos.
_paginacao = page_params(allowed_sort={"nome", "criadoEm"}, default_sort="nome")


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
    response_model=Page[ClienteResponse],
    summary="Lista e busca clientes",
    description=(
        "Paginada. `q` procura por **nome** (contém, sem distinguir maiúsculas e acentos) ou "
        "por **documento** (prefixo dos dígitos, ignorando a máscara). `situacao`: `ATIVO` "
        "(padrão), `INATIVO` ou `TODOS`. `sort`: `nome` (padrão) ou `criadoEm`."
    ),
    dependencies=acesso,
    responses={
        **problem_responses(
            (400, "VALIDATION_ERROR", "Um ou mais parâmetros são inválidos."), _PERMISSAO
        ),
        **EMPRESA_ATIVA_RESPONSES,
    },
)
def listar(
    q: str | None = Query(None, max_length=160, description="Nome ou documento."),
    situacao: SituacaoFiltro = Query(SituacaoFiltro.ATIVO),
    params: PageParams = Depends(_paginacao),
    empresa_id: UUID = Depends(empresa_ativa_id),
    use_case: ListarClientes = Depends(get_listar_clientes),
) -> Page[ClienteResponse]:
    itens, total = use_case.execute(
        empresa_id,
        q=q,
        situacao=situacao,
        offset=params.offset,
        limit=params.size,
        sort_field=params.sort_field,
        descending=params.descending,
    )
    return Page.of([ClienteResponse.de(item) for item in itens], params, total)


@router.post(
    "",
    status_code=201,
    response_model=ClienteResponse,
    summary="Cadastra um cliente",
    description=(
        "O documento é único por empresa (clientes ativos e inativos), aceita máscara e é "
        "armazenado só com dígitos. A empresa nunca é informada: é a empresa ativa."
    ),
    dependencies=acesso,
    responses={
        **problem_responses(
            (400, "VALIDATION_ERROR", "Um ou mais campos são inválidos."),
            _PERMISSAO,
            (409, "CUSTOMER_DOCUMENT_DUPLICATE", "Já existe um cliente com este documento."),
        ),
        **EMPRESA_ATIVA_RESPONSES,
    },
)
def cadastrar(
    body: ClientePayload,
    response: Response,
    empresa_id: UUID = Depends(empresa_ativa_id),
    use_case: CadastrarCliente = Depends(get_cadastrar_cliente),
) -> ClienteResponse:
    with _erros_de_negocio():
        cliente = use_case.execute(empresa_id, body.para_dominio())
    response.headers["Location"] = f"/api/v1/clientes/{cliente.id}"
    return ClienteResponse.de(cliente)


@router.get(
    "/{cliente_id}",
    response_model=ClienteResponse,
    summary="Consulta um cliente",
    dependencies=acesso,
    responses={**problem_responses(_PERMISSAO, _NAO_ENCONTRADO), **EMPRESA_ATIVA_RESPONSES},
)
def consultar(
    cliente_id: UUID,
    empresa_id: UUID = Depends(empresa_ativa_id),
    use_case: ObterCliente = Depends(get_obter_cliente),
) -> ClienteResponse:
    with _erros_de_negocio():
        return ClienteResponse.de(use_case.execute(empresa_id, cliente_id))


@router.put(
    "/{cliente_id}",
    response_model=ClienteResponse,
    summary="Edita um cliente",
    description="Leva todos os campos e a `versao` lida. Tipo e documento podem ser corrigidos.",
    dependencies=acesso,
    responses={
        **problem_responses(
            (400, "VALIDATION_ERROR", "Um ou mais campos são inválidos."),
            _PERMISSAO,
            _NAO_ENCONTRADO,
            (409, "VERSION_CONFLICT", "O registro foi alterado por outra pessoa."),
        ),
        **EMPRESA_ATIVA_RESPONSES,
    },
)
def atualizar(
    cliente_id: UUID,
    body: ClienteAtualizacao,
    empresa_id: UUID = Depends(empresa_ativa_id),
    use_case: AtualizarCliente = Depends(get_atualizar_cliente),
) -> ClienteResponse:
    with _erros_de_negocio():
        cliente = use_case.execute(empresa_id, cliente_id, body.para_dominio(), body.versao)
    return ClienteResponse.de(cliente)


@router.patch(
    "/{cliente_id}/situacao",
    response_model=ClienteResponse,
    summary="Inativa ou reativa um cliente",
    description=(
        "Idempotente. Cliente inativo some da listagem padrão (`situacao=ATIVO`), mas continua "
        "consultável e vinculado ao histórico (RN-07)."
    ),
    dependencies=acesso,
    responses={
        **problem_responses(
            _PERMISSAO,
            _NAO_ENCONTRADO,
            (409, "VERSION_CONFLICT", "O registro foi alterado por outra pessoa."),
        ),
        **EMPRESA_ATIVA_RESPONSES,
    },
)
def alterar_situacao(
    cliente_id: UUID,
    body: SituacaoPayload,
    empresa_id: UUID = Depends(empresa_ativa_id),
    use_case: AlterarSituacaoCliente = Depends(get_alterar_situacao_cliente),
) -> ClienteResponse:
    with _erros_de_negocio():
        return ClienteResponse.de(use_case.execute(empresa_id, cliente_id, body.ativo, body.versao))


@router.delete(
    "/{cliente_id}",
    status_code=204,
    summary="Exclui um cliente sem vínculos",
    description=(
        "Só é permitida sem vínculos (venda ou OS); caso contrário `422 CUSTOMER_HAS_HISTORY` "
        "e o cliente deve ser inativado (RNF-097). Os vínculos são consultados pelos "
        "verificadores registrados por cada módulo (ponto de extensão, RN-06). Sem empresa "
        "ativa, também responde `422 COMPANY_NOT_ACTIVE`."
    ),
    dependencies=acesso,
    responses={
        **problem_responses(
            _PERMISSAO,
            _NAO_ENCONTRADO,
            (
                422,
                "CUSTOMER_HAS_HISTORY",
                "O cliente possui vendas ou ordens de serviço vinculadas e não pode ser excluído. "
                "Inative o cliente.",
            ),
        ),
    },
)
def excluir(
    cliente_id: UUID,
    empresa_id: UUID = Depends(empresa_ativa_id),
    use_case: ExcluirCliente = Depends(get_excluir_cliente),
) -> Response:
    with _erros_de_negocio():
        use_case.execute(empresa_id, cliente_id)
    return Response(status_code=204)
