"""Hash de senha (bcrypt), JWT de acesso (HS256) e refresh token opaco."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import bcrypt
import jwt

from meunegocio360_core.auth.domain.models import Usuario
from meunegocio360_core.auth.domain.ports import GeneratedRefreshToken, IssuedAccessToken
from meunegocio360_core.shared.security import AccessClaims, InvalidAccessTokenError

ISSUER = "meunegocio360-core"
ALGORITHM = "HS256"


class BcryptPasswordHasher:
    """BCrypt com *salt* proprio (RNF-023). Senhas ate 72 bytes (RN-11)."""

    def __init__(self) -> None:
        # Hash fixo calculado na subida, para equalizar o tempo quando o usuario nao existe.
        self._dummy_hash = bcrypt.hashpw(secrets.token_bytes(16), bcrypt.gensalt())

    def hash(self, senha: str) -> str:
        return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("ascii")

    def verify(self, senha: str, senha_hash: str) -> bool:
        try:
            return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("ascii"))
        except ValueError:
            return False

    def verify_dummy(self, senha: str) -> None:
        try:
            bcrypt.checkpw(senha.encode("utf-8"), self._dummy_hash)
        except ValueError:
            pass


class Sha256RefreshTokenGenerator:
    """Valor opaco de 256 bits (``secrets``); so o SHA-256 vai para o banco (RN-06, RN-09)."""

    def generate(self) -> GeneratedRefreshToken:
        raw = secrets.token_urlsafe(32)
        return GeneratedRefreshToken(raw=raw, token_hash=self.hash_of(raw))

    def hash_of(self, raw: str) -> str:
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class JwtService:
    """Emite e valida o token de acesso. Implementa o emissor e o verificador do gate."""

    def __init__(self, secret: str, expiracao_minutos: int) -> None:
        self._secret = secret
        self._expiracao = timedelta(minutes=expiracao_minutos)

    def issue(self, usuario: Usuario, agora: datetime) -> IssuedAccessToken:
        payload = {
            "iss": ISSUER,
            "sub": str(usuario.id),
            "iat": agora,
            "exp": agora + self._expiracao,
            "jti": str(uuid4()),
            "perfil": usuario.perfil.value,
        }
        token = jwt.encode(payload, self._secret, algorithm=ALGORITHM)
        return IssuedAccessToken(token=token, expires_in=int(self._expiracao.total_seconds()))

    def verify(self, token: str) -> AccessClaims:
        try:
            claims = jwt.decode(
                token,
                self._secret,
                algorithms=[ALGORITHM],  # rejeita ``alg: none`` e qualquer outro algoritmo
                issuer=ISSUER,
                options={"require": ["exp", "iat", "iss", "sub", "jti"]},
            )
            return AccessClaims(
                user_id=UUID(claims["sub"]),
                perfil=str(claims["perfil"]),
                jti=str(claims["jti"]),
                expires_at=datetime.fromtimestamp(claims["exp"], UTC),
            )
        except (jwt.PyJWTError, ValueError, KeyError) as exc:
            raise InvalidAccessTokenError from exc
