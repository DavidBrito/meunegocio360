"""Validadores reutilizaveis entre features (RNF-BE-27)."""

import re

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PESOS_CNPJ_1 = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
_PESOS_CNPJ_2 = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)


def somente_digitos(value: str) -> str:
    """Remove tudo que nao e digito (mascara de CPF/CNPJ/telefone)."""
    return re.sub(r"\D", "", value)


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


def _digito_cpf(base: str) -> str:
    # pesos decrescentes a partir de len(base) + 1 (10 para o 1o digito, 11 para o 2o)
    soma = sum(
        int(digito) * peso for digito, peso in zip(base, range(len(base) + 1, 1, -1), strict=True)
    )
    resto = (soma * 10) % 11
    return "0" if resto == 10 else str(resto)


def is_valid_cpf(value: str) -> bool:
    """CPF so com digitos: 11 posicoes, digitos verificadores corretos e sem sequencia repetida."""
    if not re.fullmatch(r"\d{11}", value) or value == value[0] * 11:
        return False
    primeiro = _digito_cpf(value[:9])
    segundo = _digito_cpf(value[:9] + primeiro)
    return value[9:] == primeiro + segundo
