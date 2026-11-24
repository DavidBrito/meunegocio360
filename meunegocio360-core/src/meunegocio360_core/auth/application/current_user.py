"""Caso de uso: dados do usuario autenticado (GET /auth/me)."""

from collections.abc import Callable
from uuid import UUID

from meunegocio360_core.auth.application.dto import UsuarioDados
from meunegocio360_core.auth.domain.errors import UserNotAuthenticatedError
from meunegocio360_core.auth.domain.ports import UnitOfWork


class GetCurrentUserUseCase:
    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def execute(self, usuario_id: UUID) -> UsuarioDados:
        with self._uow_factory() as uow:
            usuario = uow.usuarios.get_by_id(usuario_id)
        if usuario is None or not usuario.ativo:  # RN-02
            raise UserNotAuthenticatedError
        return UsuarioDados.de(usuario)
