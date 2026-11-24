"""Endpoints de autenticacao (RF-BE-001). Controllers finos (RNF-BE-01)."""

from fastapi import APIRouter, Cookie, Depends, Response, Security

from meunegocio360_core.auth.api.cookies import (
    COOKIE_NAME,
    clear_cookie_header,
    clear_refresh_cookie,
    set_refresh_cookie,
)
from meunegocio360_core.auth.api.dependencies import (
    get_access_claims,
    get_current_user_use_case,
    get_login_use_case,
    get_logout_use_case,
    get_refresh_use_case,
    require_allowed_origin,
)
from meunegocio360_core.auth.api.schemas import AuthResponse, LoginRequest, UsuarioResponse
from meunegocio360_core.auth.application.current_user import GetCurrentUserUseCase
from meunegocio360_core.auth.application.login import LoginUseCase
from meunegocio360_core.auth.application.logout import LogoutUseCase
from meunegocio360_core.auth.application.refresh import RefreshUseCase
from meunegocio360_core.auth.domain.errors import (
    AccountLockedError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    UserNotAuthenticatedError,
)
from meunegocio360_core.shared.config import Settings, get_settings
from meunegocio360_core.shared.errors import AppError
from meunegocio360_core.shared.openapi import bearer_scheme, problem_responses
from meunegocio360_core.shared.security import AccessClaims

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticação"])


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Autentica o usuário por e-mail e senha",
    description=(
        "Devolve o token de acesso (JWT) no corpo e entrega o refresh token somente no "
        "cookie `mn360_refresh` (HttpOnly, SameSite=Strict)."
    ),
    responses=problem_responses(
        (400, "VALIDATION_ERROR", "Um ou mais campos são inválidos."),
        (401, "INVALID_CREDENTIALS", "E-mail ou senha inválidos."),
        (429, "ACCOUNT_TEMPORARILY_LOCKED", "Conta temporariamente bloqueada."),
    ),
)
def login(
    body: LoginRequest,
    response: Response,
    use_case: LoginUseCase = Depends(get_login_use_case),
    settings: Settings = Depends(get_settings),
) -> AuthResponse:
    try:
        result = use_case.execute(body.email, body.senha)
    except InvalidCredentialsError:
        raise AppError(
            401, "INVALID_CREDENTIALS", "Credenciais inválidas", "E-mail ou senha inválidos."
        ) from None
    except AccountLockedError as exc:
        raise AppError(
            429,
            "ACCOUNT_TEMPORARILY_LOCKED",
            "Conta temporariamente bloqueada",
            "Muitas tentativas inválidas. Tente novamente mais tarde.",
            headers={"Retry-After": str(exc.retry_after_seconds)},
        ) from None
    set_refresh_cookie(
        response,
        result.refresh_token,
        max_age=result.refresh_max_age_seconds,
        secure=settings.app_auth_cookie_secure,
    )
    return AuthResponse.de(result)


@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Renova a sessão com o refresh token (cookie)",
    description="Sem corpo. Rotaciona o refresh token; devolve novo token de acesso e cookie.",
    dependencies=[Depends(require_allowed_origin)],
    responses=problem_responses(
        (401, "INVALID_REFRESH_TOKEN", "Sessão inválida ou expirada."),
        (403, "ORIGIN_NOT_ALLOWED", "A origem da requisição não é permitida."),
    ),
)
def refresh(
    response: Response,
    use_case: RefreshUseCase = Depends(get_refresh_use_case),
    settings: Settings = Depends(get_settings),
    mn360_refresh: str | None = Cookie(default=None, alias=COOKIE_NAME),
) -> AuthResponse:
    try:
        result = use_case.execute(mn360_refresh)
    except InvalidRefreshTokenError:
        raise AppError(
            401,
            "INVALID_REFRESH_TOKEN",
            "Sessão inválida",
            "Sessão inválida ou expirada. Entre novamente.",
            headers=clear_cookie_header(secure=settings.app_auth_cookie_secure),
        ) from None
    set_refresh_cookie(
        response,
        result.refresh_token,
        max_age=result.refresh_max_age_seconds,
        secure=settings.app_auth_cookie_secure,
    )
    return AuthResponse.de(result)


@router.post(
    "/logout",
    status_code=204,
    summary="Encerra a sessão",
    description="Idempotente: sempre `204`, mesmo sem cookie ou com token inválido.",
    dependencies=[Depends(require_allowed_origin)],
    responses=problem_responses(
        (403, "ORIGIN_NOT_ALLOWED", "A origem da requisição não é permitida.")
    ),
)
def logout(
    response: Response,
    use_case: LogoutUseCase = Depends(get_logout_use_case),
    settings: Settings = Depends(get_settings),
    mn360_refresh: str | None = Cookie(default=None, alias=COOKIE_NAME),
) -> Response:
    use_case.execute(mn360_refresh)
    clear_refresh_cookie(response, secure=settings.app_auth_cookie_secure)
    response.status_code = 204
    return response


@router.get(
    "/me",
    response_model=UsuarioResponse,
    summary="Dados do usuário autenticado",
    dependencies=[Security(bearer_scheme)],
    responses=problem_responses(
        (401, "UNAUTHORIZED", "Token de acesso ausente, inválido ou expirado.")
    ),
)
def me(
    claims: AccessClaims = Depends(get_access_claims),
    use_case: GetCurrentUserUseCase = Depends(get_current_user_use_case),
) -> UsuarioResponse:
    try:
        return UsuarioResponse.de(use_case.execute(claims.user_id))
    except UserNotAuthenticatedError:
        raise AppError(
            401,
            "UNAUTHORIZED",
            "Não autenticado",
            "Token de acesso ausente, inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
