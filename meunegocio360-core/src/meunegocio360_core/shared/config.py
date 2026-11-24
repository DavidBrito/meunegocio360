"""Configuracao por variaveis de ambiente (12-factor, RNF-052, RNF-BE-31/32).

Em desenvolvimento (``APP_ENV=dev``) o ``.env`` da raiz do repositorio e lido; nos
demais ambientes as variaveis vem do ambiente do processo.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict
from sqlalchemy.engine import URL, make_url

_ROOT_ENV_FILE = Path(__file__).resolve().parents[4] / ".env"
_ENV_FILE = _ROOT_ENV_FILE if os.getenv("APP_ENV", "dev") == "dev" else None

JWT_SECRET_MIN_BYTES = 32
PASSWORD_MIN = 8
PASSWORD_MAX = 72


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE, extra="ignore", case_sensitive=False, hide_input_in_errors=True
    )

    app_env: Literal["dev", "test", "prod"] = "dev"
    port: int = 8080

    db_url: str
    db_user: str
    db_password: SecretStr

    jwt_secret: SecretStr
    cors_allowed_origins: Annotated[list[str], NoDecode]
    app_auth_cookie_secure: bool = True
    app_auth_max_tentativas: int = 5
    app_auth_bloqueio_minutos: int = 15
    app_auth_jwt_expiracao_minutos: int = 15
    app_auth_refresh_expiracao_dias: int = 7

    seed_admin_senha: SecretStr | None = None
    seed_usuario_senha: SecretStr | None = None

    scheduler_enabled: bool = True

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("cors_allowed_origins")
    @classmethod
    def _origins_sem_curinga(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("CORS_ALLOWED_ORIGINS nao pode ser vazio")
        if "*" in value:
            raise ValueError("CORS_ALLOWED_ORIGINS nao pode conter '*' (RNF-BE-42)")
        return value

    @field_validator("jwt_secret")
    @classmethod
    def _jwt_secret_forte(cls, value: SecretStr) -> SecretStr:
        if len(value.get_secret_value().encode("utf-8")) < JWT_SECRET_MIN_BYTES:
            raise ValueError(f"JWT_SECRET deve ter pelo menos {JWT_SECRET_MIN_BYTES} bytes")
        return value

    @field_validator("seed_admin_senha", "seed_usuario_senha", mode="before")
    @classmethod
    def _seed_vazio_vira_none(cls, value: object) -> object:
        return None if value == "" else value

    @field_validator("seed_admin_senha", "seed_usuario_senha")
    @classmethod
    def _seed_tamanho(cls, value: SecretStr | None) -> SecretStr | None:
        if value is not None:
            size = len(value.get_secret_value())
            if not PASSWORD_MIN <= size <= PASSWORD_MAX:
                raise ValueError(
                    f"senha de seed deve ter de {PASSWORD_MIN} a {PASSWORD_MAX} caracteres"
                )
        return value

    @model_validator(mode="after")
    def _cookie_inseguro_somente_em_dev(self) -> "Settings":
        if not self.app_auth_cookie_secure and self.app_env != "dev":
            raise ValueError("APP_AUTH_COOKIE_SECURE=false so e permitido com APP_ENV=dev")
        return self

    @property
    def is_dev(self) -> bool:
        return self.app_env == "dev"

    @property
    def is_prod(self) -> bool:
        return self.app_env == "prod"

    @property
    def docs_enabled(self) -> bool:
        """Swagger UI e OpenAPI ficam desligados em producao (RNF-030, ADR 0005)."""
        return not self.is_prod

    @property
    def database_url(self) -> URL:
        return make_url(self.db_url).set(
            username=self.db_user, password=self.db_password.get_secret_value()
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # campos obrigatorios vem do ambiente
