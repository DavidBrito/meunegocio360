"""Seed de desenvolvimento (somente ``APP_ENV=dev``, RNF-BE-24). Idempotente.

Cria um usuario por perfil e NAO cria empresa (RN-08 do RF-BE-002).

As senhas vem de ``SEED_ADMIN_SENHA``, ``SEED_USUARIO_SENHA`` e ``SEED_FINANCEIRO_SENHA``;
nunca ficam no repositorio.
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
    financeiro_senha: SecretStr | None,
) -> None:
    agora = clock.now()
    candidatos = [
        ("Administrador", "admin@meunegocio360.com.br", Perfil.ADMIN, admin_senha),
        (
            "Operador Comercial",
            "usuario@meunegocio360.com.br",
            Perfil.OPERADOR_COMERCIAL,
            usuario_senha,
        ),
        (
            "Operador Financeiro",
            "financeiro@meunegocio360.com.br",
            Perfil.OPERADOR_FINANCEIRO,
            financeiro_senha,
        ),
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
