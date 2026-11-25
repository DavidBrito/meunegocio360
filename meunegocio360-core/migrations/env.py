"""Ambiente do Alembic: URL vinda das variaveis de ambiente, metadata dos modelos."""

from alembic import context
from sqlalchemy import create_engine

import meunegocio360_core.auth.infra.models  # noqa: F401 - registra os modelos no metadata
import meunegocio360_core.cliente.infra.models  # noqa: F401
import meunegocio360_core.empresa.infra.models  # noqa: F401
from meunegocio360_core.shared.config import get_settings
from meunegocio360_core.shared.db import Base

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=get_settings().database_url.render_as_string(hide_password=False),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(get_settings().database_url)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
