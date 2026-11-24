"""Caso de uso: login (RN-01 a RN-06, RN-11 a RN-13)."""

import logging
import math
from collections.abc import Callable
from datetime import timedelta
from uuid import uuid4

from meunegocio360_core.auth.application.dto import AuthConfig, AuthResult, UsuarioDados
from meunegocio360_core.auth.domain.errors import AccountLockedError, InvalidCredentialsError
from meunegocio360_core.auth.domain.models import RefreshToken
from meunegocio360_core.auth.domain.ports import (
    AccessTokenIssuer,
    PasswordHasher,
    RefreshTokenGenerator,
    UnitOfWork,
)
from meunegocio360_core.shared.clock import Clock

logger = logging.getLogger(__name__)


class LoginUseCase:
    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        hasher: PasswordHasher,
        token_issuer: AccessTokenIssuer,
        refresh_generator: RefreshTokenGenerator,
        clock: Clock,
        config: AuthConfig,
    ) -> None:
        self._uow_factory = uow_factory
        self._hasher = hasher
        self._token_issuer = token_issuer
        self._refresh_generator = refresh_generator
        self._clock = clock
        self._config = config

    def execute(self, email: str, senha: str) -> AuthResult:
        agora = self._clock.now()
        with self._uow_factory() as uow:
            # Linha travada: o contador de tentativas nao sofre condicao de corrida.
            usuario = uow.usuarios.get_by_email(email, for_update=True)

            if usuario is None:
                self._hasher.verify_dummy(senha)
                logger.info("login_falha", extra={"event": "login_falha", "motivo": "desconhecido"})
                raise InvalidCredentialsError

            if usuario.esta_bloqueado(agora):
                assert usuario.bloqueado_ate is not None
                restante = (usuario.bloqueado_ate - agora).total_seconds()
                logger.warning(
                    "login_bloqueado",
                    extra={"event": "login_bloqueado", "usuarioId": str(usuario.id)},
                )
                raise AccountLockedError(max(1, math.ceil(restante)))

            senha_correta = self._hasher.verify(senha, usuario.senha_hash)

            if not senha_correta:
                if usuario.ativo:
                    bloqueou = usuario.registrar_falha(
                        agora, self._config.max_tentativas, self._config.bloqueio_minutos
                    )
                    if bloqueou:
                        uow.refresh_tokens.revoke_active_of_user(usuario.id, agora)  # RN-13
                    uow.usuarios.save(usuario)
                    uow.commit()
                    logger.warning(
                        "conta_bloqueada" if bloqueou else "login_falha",
                        extra={
                            "event": "conta_bloqueada" if bloqueou else "login_falha",
                            "usuarioId": str(usuario.id),
                        },
                    )
                raise InvalidCredentialsError

            if not usuario.ativo:
                raise InvalidCredentialsError

            usuario.registrar_sucesso(agora)
            uow.usuarios.save(usuario)

            gerado = self._refresh_generator.generate()
            expira_em = agora + timedelta(days=self._config.refresh_expiracao_dias)
            uow.refresh_tokens.add(
                RefreshToken(
                    id=uuid4(),
                    usuario_id=usuario.id,
                    familia_id=uuid4(),
                    token_hash=gerado.token_hash,
                    expira_em=expira_em,
                    criado_em=agora,
                )
            )
            acesso = self._token_issuer.issue(usuario, agora)
            uow.commit()

        logger.info("login_sucesso", extra={"event": "login_sucesso", "usuarioId": str(usuario.id)})
        return AuthResult(
            access_token=acesso.token,
            expires_in=acesso.expires_in,
            usuario=UsuarioDados.de(usuario),
            refresh_token=gerado.raw,
            refresh_max_age_seconds=int(
                timedelta(days=self._config.refresh_expiracao_dias).total_seconds()
            ),
        )
