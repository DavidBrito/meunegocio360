"""Health check sem autenticacao e sem detalhes (RNF-051, RNF-104)."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from meunegocio360_core.shared.db import get_engine

router = APIRouter(tags=["Operação"])


@router.get("/actuator/health", summary="Health check")
def health() -> JSONResponse:
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse({"status": "DOWN"}, status_code=503)
    return JSONResponse({"status": "UP"})
