"""``EmpresaAtiva``: unica interface de `empresa` para as demais features (RNF-096, RNF-BE-05).

As demais features NUNCA recebem `empresa_id` do cliente: obtem-no aqui, no servidor. Sem
empresa ativa, a operacao de negocio e recusada (`CompanyNotActiveError`, `422`, RN-04).
"""

from collections.abc import Callable
from uuid import UUID

from meunegocio360_core.empresa.domain.errors import CompanyNotActiveError
from meunegocio360_core.empresa.domain.ports import EmpresaUnitOfWork


class EmpresaAtiva:
    def __init__(self, uow_factory: Callable[[], EmpresaUnitOfWork]) -> None:
        self._uow_factory = uow_factory

    def id(self) -> UUID:
        with self._uow_factory() as uow:
            empresa = uow.empresas.get_active()
        if empresa is None:
            raise CompanyNotActiveError
        return empresa.id
