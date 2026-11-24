"""Cookie do refresh token (RF-BE-001, "Cookie de refresh")."""

from fastapi import Response

COOKIE_NAME = "mn360_refresh"
COOKIE_PATH = "/api/v1/auth"  # so e enviado aos endpoints de autenticacao


def set_refresh_cookie(response: Response, value: str, *, max_age: int, secure: bool) -> None:
    response.set_cookie(
        COOKIE_NAME,
        value,
        max_age=max_age,
        path=COOKIE_PATH,
        httponly=True,
        secure=secure,
        samesite="strict",
    )


def clear_refresh_cookie(response: Response, *, secure: bool) -> None:
    response.delete_cookie(
        COOKIE_NAME, path=COOKIE_PATH, httponly=True, secure=secure, samesite="strict"
    )


def clear_cookie_header(*, secure: bool) -> dict[str, str]:
    """Cabecalho ``Set-Cookie`` que expira o cookie, para anexar a respostas de erro."""
    holder = Response()
    clear_refresh_cookie(holder, secure=secure)
    return {"set-cookie": holder.headers["set-cookie"]}
