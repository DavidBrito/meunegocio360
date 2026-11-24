"""Engine e sessoes SQLAlchemy (acesso sincrono, ADR 0003)."""

from functools import lru_cache

from sqlalchemy import DateTime, MetaData, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from meunegocio360_core.shared.config import get_settings

# Datas sempre em UTC com fuso (TIMESTAMPTZ, ADR 0002, RNF-033).
UtcDateTime = DateTime(timezone=True)


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={"pk": "pk_%(table_name)s"})


@lru_cache
def get_engine() -> Engine:
    # hide_parameters: erros de banco nao incluem os valores dos parametros SQL (e-mail,
    # hashes, tokens), que iriam parar nos logs (RNF-023, RNF-025).
    return create_engine(
        get_settings().database_url,
        pool_pre_ping=True,
        hide_parameters=True,
        # Sessao sempre em UTC, independente do fuso do servidor (RNF-033).
        connect_args={"options": "-c timezone=UTC"},
    )


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False)
