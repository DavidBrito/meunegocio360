"""Seguranca transversal: gate *deny-by-default* e cabecalhos (RNF-021, RNF-BE-40/41)."""

from collections.abc import Callable, Collection
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from starlette.datastructures import Headers, MutableHeaders
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from meunegocio360_core.shared.errors import AppError, problem_response
from meunegocio360_core.shared.perfil import Perfil


@dataclass(frozen=True, slots=True)
class AccessClaims:
    user_id: UUID
    perfil: str
    jti: str
    expires_at: datetime


class InvalidAccessTokenError(Exception):
    """Token de acesso invalido: assinatura, algoritmo, emissor ou expiracao."""


class AccessTokenVerifier(Protocol):
    def verify(self, token: str) -> AccessClaims: ...


def unauthorized_error_response(request: Request) -> JSONResponse:
    return problem_response(
        request,
        status=401,
        code="UNAUTHORIZED",
        title="Não autenticado",
        detail="Token de acesso ausente, inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )


class AuthGateMiddleware:
    """Exige token de acesso valido em TODA rota, exceto a lista publica explicita.

    Vale tambem para caminhos inexistentes: sem token, a resposta e 401 (nao 404).
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        public_routes: Collection[tuple[str, str]],
        verifier: AccessTokenVerifier,
    ) -> None:
        self.app = app
        self.public_routes = frozenset(public_routes)
        self.verifier = verifier

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        if (scope["method"], scope["path"]) in self.public_routes:
            await self.app(scope, receive, send)
            return

        claims = self._claims(Headers(scope=scope).get("authorization"))
        if claims is None:
            response = unauthorized_error_response(Request(scope))
            await response(scope, receive, send)
            return

        scope.setdefault("state", {})["claims"] = claims
        await self.app(scope, receive, send)

    def _claims(self, authorization: str | None) -> AccessClaims | None:
        if not authorization:
            return None
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token.strip():
            return None
        try:
            return self.verifier.verify(token.strip())
        except InvalidAccessTokenError:
            return None


class SecurityHeadersMiddleware:
    """Cabecalhos de seguranca padrao (RNF-BE-41); HSTS somente em producao."""

    def __init__(self, app: ASGIApp, *, hsts: bool) -> None:
        self.app = app
        self.hsts = hsts

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        is_api = scope["path"].startswith("/api/")

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["X-Content-Type-Options"] = "nosniff"
                if is_api:
                    headers["Cache-Control"] = "no-store"
                if self.hsts:
                    headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            await send(message)

        await self.app(scope, receive, send_with_headers)


def require_perfis(*permitidos: Perfil) -> Callable[[Request], AccessClaims]:
    """Autorizacao por perfil (RNF-BE-47): dependencia a aplicar em cada operacao protegida.

    O gate ja validou o token; aqui so se confere a claim ``perfil``. Sem permissao:
    ``403 ACCESS_DENIED``. E regra de acesso, nao de negocio.
    """
    aceitos = {perfil.value for perfil in permitidos}

    def dependency(request: Request) -> AccessClaims:
        claims: AccessClaims | None = request.scope.get("state", {}).get("claims")
        if claims is None:  # nao deveria ocorrer: o gate ja barra rotas sem token
            raise AppError(
                401,
                "UNAUTHORIZED",
                "Não autenticado",
                "Token de acesso ausente, inválido ou expirado.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if claims.perfil not in aceitos:
            raise AppError(
                403,
                "ACCESS_DENIED",
                "Acesso negado",
                "Seu perfil não tem permissão para esta operação.",
            )
        return claims

    return dependency
