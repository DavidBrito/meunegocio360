"""Caso de uso: logout idempotente (RN-10)."""

from collections.abc import Callable

from meunegocio360_core.auth.domain.ports import RefreshTokenGenerator, UnitOfWork
from meunegocio360_core.shared.clock import Clock


class LogoutUseCase:
    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        refresh_generator: RefreshTokenGenerator,
        clock: Clock,
    ) -> None:
        self._uow_factory = uow_factory
        self._refresh_generator = refresh_generator
        self._clock = clock

    def execute(self, refresh_token_raw: str | None) -> None:
        """Revoga a familia do token apresentado; nunca falha (cookie ausente ou invalido)."""
        if not refresh_token_raw:
            return
        agora = self._clock.now()
        token_hash = self._refresh_generator.hash_of(refresh_token_raw)
        with self._uow_factory() as uow:
            token = uow.refresh_tokens.get_by_hash(token_hash)
            if token is None:
                return
            # Mesma ordem de travas do login e do refresh (usuario antes dos tokens).
            uow.usuarios.get_by_id(token.usuario_id, for_update=True)
            uow.refresh_tokens.revoke_family(token.familia_id, agora)
            uow.commit()
