"""Seed de desenvolvimento (somente ``APP_ENV=dev``, RNF-BE-24). Idempotente.

As senhas vem de ``SEED_ADMIN_SENHA`` e ``SEED_USUARIO_SENHA``; nunca ficam no repositorio.
"""

import logging
from collections.abc import Callable
from uuid import uuid4

from pydantic import SecretStr

from meunegocio360_core.auth.domain.models import Perfil, Usuario
from meunegocio360_core.auth.domain.ports import PasswordHasher, UnitOfWork
from meunegocio360_core.shared.clock import Clock

logger = logging.getLogger(__name__)


def seed_dev_users(
    uow_factory: Callable[[], UnitOfWork],
    hasher: PasswordHasher,
    clock: Clock,
    *,
    admin_senha: SecretStr | None,
    usuario_senha: SecretStr | None,
) -> None:
    agora = clock.now()
    candidatos = [
        ("Administrador", "admin@meunegocio360.com.br", Perfil.ADMIN, admin_senha),
        ("Usuário", "usuario@meunegocio360.com.br", Perfil.USUARIO, usuario_senha),
    ]
    with uow_factory() as uow:
        for nome, email, perfil, senha in candidatos:
            if uow.usuarios.get_by_email(email) is not None:
                continue
            if senha is None:
                logger.warning("seed_ignorado_sem_senha", extra={"perfil": perfil.value})
                continue
            uow.usuarios.add(
                Usuario(
                    id=uuid4(),
                    nome=nome,
                    email=email,
                    senha_hash=hasher.hash(senha.get_secret_value()),
                    perfil=perfil,
                    ativo=True,
                    criado_em=agora,
                    atualizado_em=agora,
                )
            )
            logger.info("seed_usuario_criado", extra={"perfil": perfil.value})
        uow.commit()
