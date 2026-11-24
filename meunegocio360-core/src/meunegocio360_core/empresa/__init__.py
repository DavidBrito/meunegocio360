"""Feature `empresa`.

API publica para as demais features (RNF-BE-05, RNF-096): elas NUNCA acessam o repositorio
nem os modelos da empresa; usam somente a dependencia `empresa_ativa_id`, que resolve o
`empresa_id` no servidor e responde `422 COMPANY_NOT_ACTIVE` quando nao ha empresa ativa.
"""

from meunegocio360_core.empresa.api.dependencies import EMPRESA_ATIVA_RESPONSES, empresa_ativa_id

__all__ = ["EMPRESA_ATIVA_RESPONSES", "empresa_ativa_id"]
