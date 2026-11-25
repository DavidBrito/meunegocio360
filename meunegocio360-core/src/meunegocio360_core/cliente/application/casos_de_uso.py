"""Casos de uso do cliente (RN-01 a RN-09). Transacoes na camada application (RNF-BE-04)."""

from collections.abc import Callable, Sequence
from uuid import UUID, uuid4

from meunegocio360_core.cliente.domain.errors import (
    CustomerDocumentDuplicateError,
    CustomerHasHistoryError,
    CustomerNotFoundError,
    VersionConflictError,
)
from meunegocio360_core.cliente.domain.models import Cliente, DadosCliente, SituacaoFiltro
from meunegocio360_core.cliente.domain.ports import ClienteUnitOfWork, VerificadorVinculoCliente
from meunegocio360_core.shared.clock import Clock

UowFactory = Callable[[], ClienteUnitOfWork]


class ListarClientes:
    def __init__(self, uow_factory: UowFactory) -> None:
        self._uow_factory = uow_factory

    def execute(
        self,
        empresa_id: UUID,
        *,
        q: str | None,
        situacao: SituacaoFiltro,
        offset: int,
        limit: int,
        sort_field: str,
        descending: bool,
    ) -> tuple[list[Cliente], int]:
        with self._uow_factory() as uow:
            return uow.clientes.search(
                empresa_id,
                q=q,
                situacao=situacao,
                offset=offset,
                limit=limit,
                sort_field=sort_field,
                descending=descending,
            )


class ObterCliente:
    def __init__(self, uow_factory: UowFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self, empresa_id: UUID, cliente_id: UUID) -> Cliente:
        with self._uow_factory() as uow:
            cliente = uow.clientes.get(empresa_id, cliente_id)
        if cliente is None:
            raise CustomerNotFoundError
        return cliente


class CadastrarCliente:
    def __init__(self, uow_factory: UowFactory, clock: Clock) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    def execute(self, empresa_id: UUID, dados: DadosCliente) -> Cliente:
        agora = self._clock.now()
        with self._uow_factory() as uow:
            if uow.clientes.documento_exists(empresa_id, dados.documento):
                raise CustomerDocumentDuplicateError
            cliente = Cliente(
                id=uuid4(),
                empresa_id=empresa_id,
                tipo_pessoa=dados.tipo_pessoa,
                nome=dados.nome,
                documento=dados.documento,
                email=dados.email,
                telefone=dados.telefone,
                ativo=True,
                criado_em=agora,
                atualizado_em=agora,
                versao=0,
            )
            uow.clientes.add(cliente)
            # Corrida entre cadastros simultaneos: o banco decide (restricao traduzida no commit).
            uow.commit()
        return cliente


class AtualizarCliente:
    def __init__(self, uow_factory: UowFactory, clock: Clock) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    def execute(
        self, empresa_id: UUID, cliente_id: UUID, dados: DadosCliente, versao: int
    ) -> Cliente:
        agora = self._clock.now()
        with self._uow_factory() as uow:
            cliente = uow.clientes.get(empresa_id, cliente_id, for_update=True)
            if cliente is None:
                raise CustomerNotFoundError
            if cliente.versao != versao:
                raise VersionConflictError
            if uow.clientes.documento_exists(empresa_id, dados.documento, excluding=cliente.id):
                raise CustomerDocumentDuplicateError
            cliente.atualizar(dados, agora)
            uow.clientes.save(cliente)
            uow.commit()
        return cliente


class AlterarSituacaoCliente:
    def __init__(self, uow_factory: UowFactory, clock: Clock) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    def execute(self, empresa_id: UUID, cliente_id: UUID, ativo: bool, versao: int) -> Cliente:
        agora = self._clock.now()
        with self._uow_factory() as uow:
            cliente = uow.clientes.get(empresa_id, cliente_id, for_update=True)
            if cliente is None:
                raise CustomerNotFoundError
            if cliente.versao != versao:
                raise VersionConflictError
            if cliente.ativo == ativo:
                return cliente  # idempotente (RN-07): nada muda e a versao nao e incrementada
            cliente.definir_situacao(ativo, agora)
            uow.clientes.save(cliente)
            uow.commit()
        return cliente


class ExcluirCliente:
    """Exclusao condicionada (RN-05/RN-06): consulta TODOS os verificadores registrados."""

    def __init__(
        self, uow_factory: UowFactory, verificadores: Sequence[VerificadorVinculoCliente]
    ) -> None:
        self._uow_factory = uow_factory
        self._verificadores = verificadores

    def execute(self, empresa_id: UUID, cliente_id: UUID) -> None:
        with self._uow_factory() as uow:
            cliente = uow.clientes.get(empresa_id, cliente_id, for_update=True)
            if cliente is None:
                raise CustomerNotFoundError
            if any(v.existe_vinculo(cliente.id) for v in self._verificadores):
                raise CustomerHasHistoryError
            uow.clientes.delete(cliente)
            uow.commit()
