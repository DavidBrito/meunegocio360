"""Erros padronizados em ``application/problem+json`` (RFC 9457, RNF-BE-14/15, RNF-024)."""

import logging
from typing import Any

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request

from meunegocio360_core.shared.request_id import HEADER, get_request_id

PROBLEM_JSON = "application/problem+json"
_TYPE_BASE = "https://meunegocio360.com.br/problemas"

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Erro de negocio/aplicacao com ``code`` estavel, traduzido para problem+json."""

    def __init__(
        self,
        status: int,
        code: str,
        title: str,
        detail: str,
        *,
        type_slug: str | None = None,
        headers: dict[str, str] | None = None,
        errors: list[dict[str, str]] | None = None,
    ) -> None:
        super().__init__(detail)
        self.status = status
        self.code = code
        self.title = title
        self.detail = detail
        self.type_slug = type_slug or code.lower().replace("_", "-")
        self.headers = headers or {}
        self.errors = errors


def problem_response(
    request: Request,
    *,
    status: int,
    code: str,
    title: str,
    detail: str,
    type_slug: str | None = None,
    errors: list[dict[str, str]] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    request_id = get_request_id(request)
    body: dict[str, Any] = {
        "type": f"{_TYPE_BASE}/{type_slug or code.lower().replace('_', '-')}",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": request.url.path,
        "code": code,
        "traceId": request_id,
    }
    if errors:
        body["errors"] = errors
    response_headers = dict(headers or {})
    if request_id:
        response_headers.setdefault(HEADER, request_id)
    return JSONResponse(body, status_code=status, media_type=PROBLEM_JSON, headers=response_headers)


_BODY_LOCATIONS = {"body", "query", "path", "header", "cookie"}


def _validation_errors(exc: RequestValidationError) -> list[dict[str, str]]:
    """Converte erros do Pydantic em ``errors[]``. Nunca devolve o valor recebido (ex.: senha)."""
    result: list[dict[str, str]] = []
    for error in exc.errors():
        loc = [str(part) for part in error["loc"]]
        if loc and loc[0] in _BODY_LOCATIONS:
            loc = loc[1:]
        field = ".".join(loc) or "corpo"
        kind = error["type"]
        ctx = error.get("ctx", {})
        if kind == "missing":
            message = "campo obrigatório" if loc else "corpo da requisição obrigatório"
        elif kind == "json_invalid":
            message = "JSON malformado"
        elif kind == "string_too_short":
            message = f"deve ter no mínimo {ctx.get('min_length')} caracteres"
        elif kind == "string_too_long":
            message = f"deve ter no máximo {ctx.get('max_length')} caracteres"
        elif kind == "string_type":
            message = "deve ser um texto"
        elif kind == "value_error":
            message = str(error["msg"]).removeprefix("Value error, ")
        else:
            message = "valor inválido"
        result.append({"field": field, "message": message})
    return result


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(request: Request, exc: AppError) -> JSONResponse:
        return problem_response(
            request,
            status=exc.status,
            code=exc.code,
            title=exc.title,
            detail=exc.detail,
            type_slug=exc.type_slug,
            headers=exc.headers,
            errors=exc.errors,
        )

    @app.exception_handler(RequestValidationError)
    async def _validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        return problem_response(
            request,
            status=400,
            code="VALIDATION_ERROR",
            title="Dados inválidos",
            detail="Um ou mais campos são inválidos.",
            type_slug="validacao",
            errors=_validation_errors(exc),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        mapping = {
            404: ("NOT_FOUND", "Recurso não encontrado", "O recurso solicitado não existe."),
            405: ("METHOD_NOT_ALLOWED", "Método não permitido", "Método HTTP não permitido."),
        }
        code, title, detail = mapping.get(
            exc.status_code, ("HTTP_ERROR", "Erro na requisição", "Não foi possível processar.")
        )
        return problem_response(
            request,
            status=exc.status_code,
            code=code,
            title=title,
            detail=detail,
            headers=dict(exc.headers or {}),
        )

    @app.exception_handler(Exception)
    async def _unexpected(request: Request, exc: Exception) -> JSONResponse:
        # O stack trace vai somente para o log; a resposta nao vaza detalhes (RNF-024).
        logger.error("erro_inesperado", exc_info=exc)
        return problem_response(
            request,
            status=500,
            code="INTERNAL_ERROR",
            title="Erro interno",
            detail="Ocorreu um erro inesperado. Tente novamente mais tarde.",
        )
