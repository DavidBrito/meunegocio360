"""Portas do dominio do cliente (RNF-010)."""

from typing import Protocol, Self
from uuid import UUID

from meunegocio360_core.cliente.domain.models import Cliente, SituacaoFiltro


class VerificadorVinculoCliente(Protocol):
    """Ponto de extensao da exclusao (RN-06, RNF-097).

    Cada requisito que criar um vinculo com o cliente (vendas, ordens de servico) registra
    uma implementacao com `registrar_verificador_vinculo`, SEM alterar a feature `cliente`.
    A implementacao NAO deve consultar tabelas de outra feature nem de outro servico: usa a
    interface publica da propria feature ou a API do servico (RNF-BE-05, RNF-090, RNF-092).
    """

    def existe_vinculo(self, cliente_id: UUID) -> bool: ...


class ClienteRepository(Protocol):
    """Toda consulta e filtrada por `empresa_id` (RNF-096): nada vaza entre empresas."""

    def get(
        self, empresa_id: UUID, cliente_id: UUID, *, for_update: bool = False
    ) -> Cliente | None: ...
    def documento_exists(
        self, empresa_id: UUID, documento: str, *, excluding: UUID | None = None
    ) -> bool: ...
    def search(
        self,
        empresa_id: UUID,
        *,
        q: str | None,
        situacao: SituacaoFiltro,
        offset: int,
        limit: int,
        sort_field: str,
        descending: bool,
    ) -> tuple[list[Cliente], int]: ...
    def add(self, cliente: Cliente) -> None: ...
    def save(self, cliente: Cliente) -> None: ...
    def delete(self, cliente: Cliente) -> None: ...


class ClienteUnitOfWork(Protocol):
    clientes: ClienteRepository

    def __enter__(self) -> Self: ...
    def __exit__(self, exc_type: object, exc: object, tb: object) -> None: ...
    def commit(self) -> None:
        """Confirma. Violacoes de unicidade do banco viram erros de dominio."""
