"""Caso de uso: remocao de refresh tokens expirados ou revogados ha mais de 30 dias."""

import logging
from collections.abc import Callable
from datetime import timedelta

from meunegocio360_core.auth.domain.ports import UnitOfWork
from meunegocio360_core.shared.clock import Clock

logger = logging.getLogger(__name__)

RETENCAO_DIAS = 30


class CleanupRefreshTokensUseCase:
    def __init__(self, uow_factory: Callable[[], UnitOfWork], clock: Clock) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    def execute(self) -> int:
        limite = self._clock.now() - timedelta(days=RETENCAO_DIAS)
        with self._uow_factory() as uow:
            removidos = uow.refresh_tokens.delete_older_than(limite)
            uow.commit()
        logger.info("refresh_tokens_limpos", extra={"event": "limpeza", "removidos": removidos})
        return removidos
