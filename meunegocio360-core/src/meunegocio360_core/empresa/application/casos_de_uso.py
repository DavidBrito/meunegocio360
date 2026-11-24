"""Casos de uso da empresa (RN-01 a RN-06). Transacoes na camada application (RNF-BE-04)."""

from collections.abc import Callable
from uuid import UUID, uuid4

from meunegocio360_core.empresa.domain.errors import (
    CompanyAlreadyActiveError,
    CompanyCnpjDuplicateError,
    CompanyNotFoundError,
    CompanyNotRegisteredError,
    VersionConflictError,
)
from meunegocio360_core.empresa.domain.models import DadosEmpresa, Empresa
from meunegocio360_core.empresa.domain.ports import EmpresaUnitOfWork
from meunegocio360_core.shared.clock import Clock

UowFactory = Callable[[], EmpresaUnitOfWork]


class ObterEmpresaAtiva:
    def __init__(self, uow_factory: UowFactory) -> None:
        self._uow_factory = uow_factory

    def execute(self) -> Empresa:
        with self._uow_factory() as uow:
            empresa = uow.empresas.get_active()
        if empresa is None:
            raise CompanyNotRegisteredError
        return empresa


class CadastrarEmpresa:
    def __init__(self, uow_factory: UowFactory, clock: Clock) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    def execute(self, dados: DadosEmpresa) -> Empresa:
        agora = self._clock.now()
        with self._uow_factory() as uow:
            # O CNPJ duplicado vem antes de "ja existe ativa": e o erro mais especifico.
            if uow.empresas.cnpj_exists(dados.cnpj):
                raise CompanyCnpjDuplicateError
            if uow.empresas.has_active():
                raise CompanyAlreadyActiveError
            empresa = Empresa(
                id=uuid4(),
                razao_social=dados.razao_social,
                nome_fantasia=dados.nome_fantasia,
                cnpj=dados.cnpj,
                email=dados.email,
                telefone=dados.telefone,
                fuso_horario=dados.fuso_horario,
                moeda=dados.moeda,
                ativa=True,
                criado_em=agora,
                atualizado_em=agora,
                versao=0,
            )
            uow.empresas.add(empresa)
            # Corridas entre cadastros simultaneos sao barradas pelo banco (indices unicos)
            # e traduzidas no commit para os mesmos erros de dominio.
            uow.commit()
        return empresa


class AtualizarEmpresa:
    def __init__(self, uow_factory: UowFactory, clock: Clock) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    def execute(self, empresa_id: UUID, dados: DadosEmpresa, versao: int) -> Empresa:
        agora = self._clock.now()
        with self._uow_factory() as uow:
            empresa = uow.empresas.get_by_id(empresa_id, for_update=True)
            if empresa is None:
                raise CompanyNotFoundError
            if empresa.versao != versao:
                raise VersionConflictError
            if uow.empresas.cnpj_exists(dados.cnpj, excluding=empresa.id):
                raise CompanyCnpjDuplicateError
            empresa.atualizar(dados, agora)
            uow.empresas.save(empresa)
            uow.commit()
        return empresa


class AlterarSituacaoEmpresa:
    def __init__(self, uow_factory: UowFactory, clock: Clock) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    def execute(self, empresa_id: UUID, ativa: bool, versao: int) -> Empresa:
        agora = self._clock.now()
        with self._uow_factory() as uow:
            empresa = uow.empresas.get_by_id(empresa_id, for_update=True)
            if empresa is None:
                raise CompanyNotFoundError
            if empresa.versao != versao:
                raise VersionConflictError
            if empresa.ativa == ativa:
                return empresa  # idempotente: nada muda, a versao nao e incrementada
            if ativa and uow.empresas.has_active(excluding=empresa.id):
                raise CompanyAlreadyActiveError  # RN-02 tambem na reativacao
            empresa.definir_situacao(ativa, agora)
            uow.empresas.save(empresa)
            uow.commit()
        return empresa
