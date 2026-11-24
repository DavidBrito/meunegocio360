"""Caso de uso: renovacao de sessao com refresh token rotativo (RN-07, RN-08, RN-13)."""

import logging
from collections.abc import Callable
from datetime import timedelta
from uuid import uuid4

from meunegocio360_core.auth.application.dto import AuthConfig, AuthResult, UsuarioDados
from meunegocio360_core.auth.domain.errors import InvalidRefreshTokenError
from meunegocio360_core.auth.domain.models import RefreshToken
from meunegocio360_core.auth.domain.ports import (
    AccessTokenIssuer,
    RefreshTokenGenerator,
    UnitOfWork,
)
from meunegocio360_core.shared.clock import Clock

logger = logging.getLogger(__name__)


class RefreshUseCase:
    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        token_issuer: AccessTokenIssuer,
        refresh_generator: RefreshTokenGenerator,
        clock: Clock,
        config: AuthConfig,
    ) -> None:
        self._uow_factory = uow_factory
        self._token_issuer = token_issuer
        self._refresh_generator = refresh_generator
        self._clock = clock
        self._config = config

    def execute(self, refresh_token_raw: str | None) -> AuthResult:
        if not refresh_token_raw:
            raise InvalidRefreshTokenError
        agora = self._clock.now()
        token_hash = self._refresh_generator.hash_of(refresh_token_raw)

        with self._uow_factory() as uow:
            token = uow.refresh_tokens.get_by_hash(token_hash)
            if token is None:
                raise InvalidRefreshTokenError

            # Ordem de travas igual a do login (usuario -> token): evita deadlock e
            # serializa renovacoes simultaneas do mesmo usuario.
            usuario = uow.usuarios.get_by_id(token.usuario_id, for_update=True)
            token = uow.refresh_tokens.get_by_hash_for_update(token_hash)
            if usuario is None or token is None:
                raise InvalidRefreshTokenError

            if token.revogado:
                # Reuso de token ja rotacionado: toda a familia e revogada (RN-08).
                uow.refresh_tokens.revoke_family(token.familia_id, agora)
                uow.commit()
                logger.warning(
                    "refresh_reuso_detectado",
                    extra={"event": "refresh_reuso_detectado", "usuarioId": str(usuario.id)},
                )
                raise InvalidRefreshTokenError

            if token.expirado(agora):
                raise InvalidRefreshTokenError

            if not usuario.ativo or usuario.esta_bloqueado(agora):
                uow.refresh_tokens.revoke_family(token.familia_id, agora)
                uow.commit()
                raise InvalidRefreshTokenError

            token.revogar(agora)
            uow.refresh_tokens.save(token)

            gerado = self._refresh_generator.generate()
            uow.refresh_tokens.add(
                RefreshToken(
                    id=uuid4(),
                    usuario_id=usuario.id,
                    familia_id=token.familia_id,
                    token_hash=gerado.token_hash,
                    expira_em=agora + timedelta(days=self._config.refresh_expiracao_dias),
                    criado_em=agora,
                )
            )
            acesso = self._token_issuer.issue(usuario, agora)
            uow.commit()

        return AuthResult(
            access_token=acesso.token,
            expires_in=acesso.expires_in,
            usuario=UsuarioDados.de(usuario),
            refresh_token=gerado.raw,
            refresh_max_age_seconds=int(
                timedelta(days=self._config.refresh_expiracao_dias).total_seconds()
            ),
        )
