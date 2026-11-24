# ADR 0003 — SQLAlchemy síncrono e migrations com Alembic

- **Status:** aceito
- **Data:** 24/11/2026
- **Relacionados:** [ADR 0001](./0001-backend-python-fastapi.md), [ADR 0002](./0002-banco-postgresql.md)

## Contexto

O requisito RNF-BE-20 pede migrations versionadas e imutáveis (Flyway, `V<n>__descricao.sql`), e o RNF-BE-21 pede que o schema não seja gerado pelo ORM (`ddl-auto=validate`). É preciso escolher o modo de acesso ao banco e a ferramenta equivalente em Python.

## Decisão

- **Acesso síncrono:** SQLAlchemy 2.x com `psycopg` 3 e rotas FastAPI declaradas com `def` (executadas em *threadpool*). É mais simples de raciocinar sobre transações, bloqueios (`SELECT … FOR UPDATE` na rotação do refresh token, RN-07/RN-08) e testes. O desempenho exigido (RNF-053) não justifica `async`.
- **Migrations:** Alembic no formato padrão (revisões em Python, com `op.*`), em `meunegocio360-core/migrations/versions/`, nomeadas com prefixo numérico sequencial e descrição (`0001_criar_tabela_usuario.py`). As revisões já aplicadas nunca são editadas (RNF-BE-20).
- **Schema nunca criado pelo ORM:** `Base.metadata.create_all` é proibido. O equivalente do `validate` é `alembic check` (detecta divergência entre modelos e migrations) na rotina de verificação.
- **Numeração dos requisitos:** as menções a `V1__criar_tabela_usuario.sql`, `V2`, `V3` etc. correspondem, em ordem, às revisões `0001`, `0002`, `0003`…
- **Seed:** comando/rotina de *seed* separado, executado só com `APP_ENV=dev` (RNF-BE-24).

## Consequências

- Revisões em Python permitem usar `op.execute` para SQL específico do PostgreSQL (índice parcial, *collation*).
- Controle otimista (`versao`, RNF-BE-28): `version_id_col` do SQLAlchemy mapeado para `409 VERSION_CONFLICT`.
- Migrar para `async` no futuro é possível, mas exigiria trocar driver e sessões; não é objetivo deste projeto.
