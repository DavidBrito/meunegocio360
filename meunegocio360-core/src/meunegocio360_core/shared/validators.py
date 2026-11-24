"""Validadores reutilizaveis entre features (RNF-BE-27)."""

import re

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PESOS_CNPJ_1 = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
_PESOS_CNPJ_2 = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)


def is_valid_email(value: str) -> bool:
    return _EMAIL.match(value) is not None


def _digito_cnpj(base: str, pesos: tuple[int, ...]) -> str:
    resto = sum(int(digito) * peso for digito, peso in zip(base, pesos, strict=True)) % 11
    return "0" if resto < 2 else str(11 - resto)


def is_valid_cnpj(value: str) -> bool:
    """CNPJ so com digitos: 14 posicoes, dígitos verificadores corretos e sem sequencia repetida."""
    if not re.fullmatch(r"\d{14}", value) or value == value[0] * 14:
        return False
    primeiro = _digito_cnpj(value[:12], _PESOS_CNPJ_1)
    segundo = _digito_cnpj(value[:12] + primeiro, _PESOS_CNPJ_2)
    return value[12:] == primeiro + segundo
