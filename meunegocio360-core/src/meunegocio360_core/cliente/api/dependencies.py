"""Composicao das dependencias da feature cliente."""

from meunegocio360_core.cliente.application.casos_de_uso import (
    AlterarSituacaoCliente,
    AtualizarCliente,
    CadastrarCliente,
    ExcluirCliente,
    ListarClientes,
    ObterCliente,
)
from meunegocio360_core.cliente.application.vinculos import verificadores_registrados
from meunegocio360_core.cliente.infra.repositories import SqlAlchemyClienteUnitOfWork
from meunegocio360_core.shared.clock import SystemClock
from meunegocio360_core.shared.db import get_session_factory


def uow_factory() -> SqlAlchemyClienteUnitOfWork:
    return SqlAlchemyClienteUnitOfWork(get_session_factory())


def get_listar_clientes() -> ListarClientes:
    return ListarClientes(uow_factory)


def get_obter_cliente() -> ObterCliente:
    return ObterCliente(uow_factory)


def get_cadastrar_cliente() -> CadastrarCliente:
    return CadastrarCliente(uow_factory, SystemClock())


def get_atualizar_cliente() -> AtualizarCliente:
    return AtualizarCliente(uow_factory, SystemClock())


def get_alterar_situacao_cliente() -> AlterarSituacaoCliente:
    return AlterarSituacaoCliente(uow_factory, SystemClock())


def get_excluir_cliente() -> ExcluirCliente:
    # Os verificadores sao lidos a cada chamada: quem registrar depois (vendas) tambem vale.
    return ExcluirCliente(uow_factory, verificadores_registrados())
