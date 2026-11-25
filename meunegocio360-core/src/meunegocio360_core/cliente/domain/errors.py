"""Erros de dominio do cliente (traduzidos para codigos estaveis na camada api, RNF-BE-15)."""


class ClienteError(Exception):
    """Base dos erros de negocio do cliente."""


class CustomerNotFoundError(ClienteError):
    """Cliente inexistente na empresa ativa (inclui clientes de outras empresas)."""


class CustomerDocumentDuplicateError(ClienteError):
    """Documento ja cadastrado na empresa, em cliente ativo ou inativo (RN-03)."""


class CustomerHasHistoryError(ClienteError):
    """Cliente com vinculo (venda, OS) nao pode ser excluido, apenas inativado (RN-05)."""


class VersionConflictError(ClienteError):
    """A `versao` enviada esta desatualizada (RNF-BE-28)."""
