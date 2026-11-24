"""Erros de dominio da autenticacao."""


class InvalidCredentialsError(Exception):
    """E-mail inexistente, senha incorreta ou usuario inativo (resposta unica, RN-03)."""


class AccountLockedError(Exception):
    def __init__(self, retry_after_seconds: int) -> None:
        super().__init__("conta temporariamente bloqueada")
        self.retry_after_seconds = retry_after_seconds


class InvalidRefreshTokenError(Exception):
    """Refresh token ausente, desconhecido, expirado, revogado ou de usuario inapto."""


class UserNotAuthenticatedError(Exception):
    """Token de acesso valido, mas o usuario nao existe mais ou esta inativo."""
