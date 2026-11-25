"""Feature `cliente`.

API publica para as demais features: quem criar um vinculo com o cliente (vendas, OS)
registra um `VerificadorVinculoCliente` com `registrar_verificador_vinculo` (RN-06), sem
alterar esta feature. O restante da feature (repositorio, modelos) e privado (RNF-BE-05).
"""

from meunegocio360_core.cliente.application.vinculos import registrar_verificador_vinculo
from meunegocio360_core.cliente.domain.ports import VerificadorVinculoCliente

__all__ = ["VerificadorVinculoCliente", "registrar_verificador_vinculo"]
