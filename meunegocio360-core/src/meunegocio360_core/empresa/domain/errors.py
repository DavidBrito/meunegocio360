"""Erros de dominio da empresa (traduzidos para codigos estaveis na camada api, RNF-BE-15)."""


class EmpresaError(Exception):
    """Base dos erros de negocio da empresa."""


class CompanyNotRegisteredError(EmpresaError):
    """Nao existe empresa ativa (consulta)."""


class CompanyNotFoundError(EmpresaError):
    """O id informado nao corresponde a nenhuma empresa."""


class CompanyCnpjDuplicateError(EmpresaError):
    """CNPJ ja cadastrado (RN-01): vale para empresas ativas e inativas."""


class CompanyAlreadyActiveError(EmpresaError):
    """Ja existe uma empresa ativa (RN-02)."""


class VersionConflictError(EmpresaError):
    """A `versao` enviada esta desatualizada (RNF-BE-28)."""


class CompanyNotActiveError(EmpresaError):
    """Operacao de negocio sem empresa ativa (RN-04, RNF-096)."""
