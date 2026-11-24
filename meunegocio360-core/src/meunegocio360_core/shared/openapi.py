"""Exemplos de erro ``problem+json`` para a documentacao OpenAPI (RNF-030)."""

from typing import Any

from fastapi.security import HTTPBearer
from pydantic import BaseModel

# Documenta o esquema Bearer no OpenAPI (botao "Authorize" da Swagger UI). A validacao real
# do token e do AuthGateMiddleware.
bearer_scheme = HTTPBearer(auto_error=False, description="Token de acesso (JWT) do login.")


class FieldError(BaseModel):
    field: str
    message: str


class ProblemDetail(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    code: str
    traceId: str | None = None  # noqa: N815 - nome fixado pelo contrato (RNF-BE-14)
    errors: list[FieldError] | None = None


def problem_responses(*examples: tuple[int, str, str]) -> dict[int | str, dict[str, Any]]:
    """Monta ``responses=`` a partir de tuplas ``(status, code, detail)``."""
    responses: dict[int | str, dict[str, Any]] = {}
    for status, code, detail in examples:
        slug = code.lower().replace("_", "-")
        responses[status] = {
            "model": ProblemDetail,
            "description": code,
            "content": {
                "application/problem+json": {
                    "example": {
                        "type": f"https://meunegocio360.com.br/problemas/{slug}",
                        "title": code,
                        "status": status,
                        "detail": detail,
                        "instance": "/api/v1/auth/...",
                        "code": code,
                        "traceId": "9f1c2e7a-0000-0000-0000-000000000000",
                    }
                }
            },
        }
    return responses
