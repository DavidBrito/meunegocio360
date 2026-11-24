"""Paginacao e ordenacao padrao das listagens (RNF-BE-13, RNF-BE-16, RNF-054).

Parametros: ``page`` (a partir de 0), ``size`` (padrao 20, maximo 100) e ``sort`` no formato
``campo,asc|desc``, restrito a uma lista permitida por listagem.
"""

import math
from collections.abc import Callable, Collection
from dataclasses import dataclass
from typing import Generic, TypeVar

from fastapi import Query

from meunegocio360_core.shared.errors import AppError
from meunegocio360_core.shared.schemas import CamelModel

DEFAULT_SIZE = 20
MAX_SIZE = 100

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class PageParams:
    page: int
    size: int
    sort_field: str
    descending: bool

    @property
    def offset(self) -> int:
        return self.page * self.size


class Page(CamelModel, Generic[T]):  # noqa: UP046 - TypeVar clássico: compatível com o FastAPI/Pydantic
    content: list[T]
    page: int
    size: int
    total_elements: int
    total_pages: int

    @classmethod
    def of(cls, content: list[T], params: PageParams, total: int) -> "Page[T]":
        return cls(
            content=content,
            page=params.page,
            size=params.size,
            total_elements=total,
            total_pages=math.ceil(total / params.size) if total else 0,
        )


def page_params(
    *, allowed_sort: Collection[str], default_sort: str
) -> Callable[[int, int, str], PageParams]:
    """Cria a dependencia FastAPI de paginacao para uma listagem."""

    def dependency(
        page: int = Query(0, ge=0, description="Página, a partir de 0."),
        size: int = Query(
            DEFAULT_SIZE, ge=1, le=MAX_SIZE, description=f"Itens por página (máximo {MAX_SIZE})."
        ),
        sort: str = Query(
            default_sort,
            description=f"`campo,asc|desc`. Campos: {', '.join(sorted(allowed_sort))}.",
        ),
    ) -> PageParams:
        field, _, direction = sort.partition(",")
        direction = (direction or "asc").lower()
        if field not in allowed_sort or direction not in {"asc", "desc"}:
            campos = ", ".join(sorted(allowed_sort))
            raise AppError(
                400,
                "VALIDATION_ERROR",
                "Dados inválidos",
                "Um ou mais parâmetros são inválidos.",
                type_slug="validacao",
                errors=[
                    {
                        "field": "sort",
                        "message": f"use campo,asc|desc com campo em: {campos}",
                    }
                ],
            )
        return PageParams(page=page, size=size, sort_field=field, descending=direction == "desc")

    return dependency
