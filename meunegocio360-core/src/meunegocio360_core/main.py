"""Aplicacao FastAPI do Nucleo: composicao de middlewares, handlers, rotas e tarefas."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from meunegocio360_core.auth.api.dependencies import get_hasher, get_jwt_service, uow_factory
from meunegocio360_core.auth.api.router import router as auth_router
from meunegocio360_core.auth.application.cleanup import CleanupRefreshTokensUseCase
from meunegocio360_core.auth.infra.seed import seed_dev_users
from meunegocio360_core.cliente.api.router import router as cliente_router
from meunegocio360_core.empresa.api.router import router as empresa_router
from meunegocio360_core.shared.clock import SystemClock
from meunegocio360_core.shared.config import Settings, get_settings
from meunegocio360_core.shared.errors import register_error_handlers
from meunegocio360_core.shared.health import router as health_router
from meunegocio360_core.shared.logging import configure_logging
from meunegocio360_core.shared.request_id import RequestIdMiddleware
from meunegocio360_core.shared.security import AuthGateMiddleware, SecurityHeadersMiddleware

logger = logging.getLogger(__name__)

# Unicas rotas acessiveis sem token de acesso (RNF-021, RNF-BE-40). Todo o resto exige Bearer.
PUBLIC_ROUTES = frozenset(
    {
        ("POST", "/api/v1/auth/login"),
        ("POST", "/api/v1/auth/refresh"),  # autentica pelo cookie de refresh
        ("POST", "/api/v1/auth/logout"),  # idempotente; usa o cookie de refresh
        ("GET", "/actuator/health"),
    }
)
DOCS_ROUTES = frozenset(
    {("GET", "/docs"), ("GET", "/openapi.json"), ("GET", "/docs/oauth2-redirect")}
)


def _cleanup_job() -> None:
    try:
        CleanupRefreshTokensUseCase(uow_factory, SystemClock()).execute()
    except Exception:
        logger.exception("falha_limpeza_refresh_tokens")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(json_logs=not settings.is_dev)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        if settings.is_dev:
            seed_dev_users(
                uow_factory,
                get_hasher(),
                SystemClock(),
                admin_senha=settings.seed_admin_senha,
                usuario_senha=settings.seed_usuario_senha,
                financeiro_senha=settings.seed_financeiro_senha,
            )
        scheduler: BackgroundScheduler | None = None
        if settings.scheduler_enabled:
            scheduler = BackgroundScheduler(timezone="UTC")
            scheduler.add_job(_cleanup_job, CronTrigger(hour=3, minute=0, timezone="UTC"))
            scheduler.start()
        try:
            yield
        finally:
            if scheduler is not None:
                scheduler.shutdown(wait=False)

    docs = settings.docs_enabled
    app = FastAPI(
        title="MeuNegocio360 — Núcleo",
        version="0.1.0",
        description=(
            "API do microsserviço Núcleo. Faça login em `/api/v1/auth/login` e use *Authorize*.\n\n"
            "**Empresa ativa (`EmpresaAtiva`):** os módulos de negócio (clientes, fornecedores, "
            "catálogo e demais) nunca recebem `empresa_id` do cliente; o servidor resolve a "
            "empresa ativa. Sem empresa ativa, a criação de registros responde "
            "`422 COMPANY_NOT_ACTIVE`; a consulta aos dados existentes continua permitida."
        ),
        openapi_tags=[
            {
                "name": "Clientes",
                "description": (
                    "Cadastro de clientes da empresa ativa. `ADMIN` e `OPERADOR_COMERCIAL`; "
                    "o financeiro recebe `403`. Busca por nome (sem acento/caixa) ou documento."
                ),
            },
            {
                "name": "Empresa",
                "description": (
                    "Cadastro da empresa única ativa e seus parâmetros. Somente `ADMIN` escreve; "
                    "qualquer perfil autenticado consulta."
                ),
            },
        ],
        docs_url="/docs" if docs else None,
        redoc_url=None,
        openapi_url="/openapi.json" if docs else None,
        lifespan=lifespan,
    )

    register_error_handlers(app)
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(empresa_router)
    app.include_router(cliente_router)

    # Ordem: o ultimo adicionado e o mais externo.
    app.add_middleware(
        AuthGateMiddleware,
        public_routes=PUBLIC_ROUTES | (DOCS_ROUTES if docs else frozenset()),
        verifier=get_jwt_service(),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "X-Request-Id"],
        expose_headers=["X-Request-Id", "Retry-After"],
    )
    app.add_middleware(SecurityHeadersMiddleware, hsts=settings.is_prod)
    app.add_middleware(RequestIdMiddleware)

    # Erros de validacao saem como 400 (RNF-BE-14), nao 422: remove so o 422 PADRAO do FastAPI
    # (schema HTTPValidationError); o 422 COMPANY_NOT_ACTIVE documentado nas rotas permanece.
    gerar_openapi = app.openapi

    def _e_422_padrao(resposta: dict) -> bool:
        conteudo = resposta.get("content", {}).get("application/json", {})
        return "HTTPValidationError" in str(conteudo.get("schema", {}))

    def openapi_sem_422() -> dict:
        schema = gerar_openapi()
        for caminho in schema.get("paths", {}).values():
            for operacao in caminho.values():
                respostas = operacao.get("responses", {})
                if "422" in respostas and _e_422_padrao(respostas["422"]):
                    del respostas["422"]
        return schema

    app.openapi = openapi_sem_422  # type: ignore[method-assign]
    return app


app = create_app()
