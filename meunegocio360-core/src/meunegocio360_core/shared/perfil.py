"""Perfis de acesso (RN-07 do RF-BE-002). Modulo puro: usado por varias features."""

from enum import StrEnum


class Perfil(StrEnum):
    ADMIN = "ADMIN"
    OPERADOR_COMERCIAL = "OPERADOR_COMERCIAL"
    OPERADOR_FINANCEIRO = "OPERADOR_FINANCEIRO"
