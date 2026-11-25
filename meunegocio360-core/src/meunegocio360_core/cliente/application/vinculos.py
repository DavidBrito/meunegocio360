"""Registro de verificadores de vinculo (RN-06): vendas/OS registram o seu sem tocar aqui."""

from meunegocio360_core.cliente.domain.ports import VerificadorVinculoCliente

_VERIFICADORES: list[VerificadorVinculoCliente] = []


def registrar_verificador_vinculo(verificador: VerificadorVinculoCliente) -> None:
    """Chamado na inicializacao pela feature que cria o vinculo (ex.: vendas)."""
    _VERIFICADORES.append(verificador)


def verificadores_registrados() -> tuple[VerificadorVinculoCliente, ...]:
    return tuple(_VERIFICADORES)
