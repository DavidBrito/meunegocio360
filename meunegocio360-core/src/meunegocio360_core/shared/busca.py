"""Apoio a buscas por texto (RNF-BE-16, RNF-BE-26). Ver ADR 0006."""


def escape_like(texto: str) -> str:
    """Escapa os curingas do ``LIKE`` (``\\``, ``%`` e ``_``) para uma busca literal.

    Sem isso, um ``q`` com ``%`` ou ``_`` casaria quase tudo. Use com ``ESCAPE '\\'``.
    """
    return texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
