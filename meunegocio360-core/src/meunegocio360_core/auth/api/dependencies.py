"""Montagem das dependencias (composicao) da feature auth."""

from functools import lru_cache

from fastapi import Depends, Request
from fastapi.security import HTTPBearer

from meunegocio360_core.auth.application.current_user import GetCurrentUserUseCase
from meunegocio360_core.auth.application.dto import AuthConfig
from meunegocio360_core.auth.application.login import LoginUseCase
from meunegocio360_core.auth.application.logout import LogoutUseCase
from meunegocio360_core.auth.application.refresh import RefreshUseCase
from meunegocio360_core.auth.infra.repositories import SqlAlchemyUnitOfWork
from meunegocio360_core.auth.infra.security import (
    BcryptPasswordHasher,
    JwtService,
    Sha256RefreshTokenGenerator,
)
from meunegocio360_core.shared.clock import SystemClock
from meunegocio360_core.shared.config import Settings, get_settings
from meunegocio360_core.shared.db import get_session_factory
from meunegocio360_core.shared.errors import AppError
from meunegocio360_core.shared.security import AccessClaims

# Apenas para documentar o esquema Bearer no OpenAPI (botao "Authorize" da Swagger UI).
# A validacao real do token e feita pelo AuthGateMiddleware.
bearer_scheme = HTTPBearer(auto_error=False, description="Token de acesso (JWT) do login.")


def uow_factory() -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(get_session_factory())


@lru_cache
def get_hasher() -> BcryptPasswordHasher:
    return BcryptPasswordHasher()


@lru_cache
def get_jwt_service() -> JwtService:
    settings = get_settings()
    return JwtService(
        settings.jwt_secret.get_secret_value(), settings.app_auth_jwt_expiracao_minutos
    )


def get_auth_config(settings: Settings = Depends(get_settings)) -> AuthConfig:
    return AuthConfig(
        max_tentativas=settings.app_auth_max_tentativas,
        bloqueio_minutos=settings.app_auth_bloqueio_minutos,
        refresh_expiracao_dias=settings.app_auth_refresh_expiracao_dias,
    )


def get_login_use_case(config: AuthConfig = Depends(get_auth_config)) -> LoginUseCase:
    return LoginUseCase(
        uow_factory,
        get_hasher(),
        get_jwt_service(),
        Sha256RefreshTokenGenerator(),
        SystemClock(),
        config,
    )


def get_refresh_use_case(config: AuthConfig = Depends(get_auth_config)) -> RefreshUseCase:
    return RefreshUseCase(
        uow_factory, get_jwt_service(), Sha256RefreshTokenGenerator(), SystemClock(), config
    )


def get_logout_use_case() -> LogoutUseCase:
    return LogoutUseCase(uow_factory, Sha256RefreshTokenGenerator(), SystemClock())


def get_current_user_use_case() -> GetCurrentUserUseCase:
    return GetCurrentUserUseCase(uow_factory)


def require_allowed_origin(request: Request, settings: Settings = Depends(get_settings)) -> None:
    """Se ``Origin`` vier, deve constar em CORS_ALLOWED_ORIGINS (RNF-BE-40)."""
    origin = request.headers.get("origin")
    if origin is None:
        return
    permitidas = {item.rstrip("/").lower() for item in settings.cors_allowed_origins}
    if origin.rstrip("/").lower() not in permitidas:
        raise AppError(
            403,
            "ORIGIN_NOT_ALLOWED",
            "Origem não permitida",
            "A origem da requisição não é permitida.",
        )


def get_access_claims(request: Request) -> AccessClaims:
    claims = request.scope.get("state", {}).get("claims")
    if claims is None:  # nao deveria ocorrer: o gate ja barra rotas sem token
        raise AppError(
            401,
            "UNAUTHORIZED",
            "Não autenticado",
            "Token de acesso ausente, inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return claims
