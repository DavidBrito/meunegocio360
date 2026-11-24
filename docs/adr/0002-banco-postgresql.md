# ADR 0002 — PostgreSQL no lugar de MySQL

- **Status:** aceito
- **Data:** 24/11/2026
- **Relacionados:** [ADR 0001](./0001-backend-python-fastapi.md), [ADR 0003](./0003-sqlalchemy-sincrono-e-alembic.md)

## Contexto

Os requisitos adotam MySQL 8 (um banco por serviço, RNF-090). O Render, destino da implantação, oferece PostgreSQL gerenciado e **não** oferece MySQL gerenciado, o que obrigava a um serviço privado pago ou a um provedor externo (README, seção 7). PostgreSQL também é o par natural de SQLAlchemy/Alembic.

## Decisão

PostgreSQL (versão 16 ou superior; confirmar a versão disponível no Render na implantação), um banco por serviço, driver `psycopg` 3 (`psycopg[binary]`), imagem `postgres` no `compose.yaml`. URL de conexão no formato `postgresql+psycopg://…`.

### Mapeamento dos tipos e recursos citados nos requisitos

| Requisito (MySQL) | PostgreSQL |
| --- | --- |
| `BINARY(16)` (UUID) | `UUID` nativo |
| `DATETIME(6)` (UTC) | `TIMESTAMPTZ`, gravando e lendo sempre em UTC |
| `BOOLEAN`, `INT`, `BIGINT`, `VARCHAR(n)`, `CHAR(64)`, `NUMERIC` | iguais |
| `TINYINT` | `SMALLINT` ou `BOOLEAN`, conforme o caso |
| *Collation* `utf8mb4_0900_ai_ci` (sem diferença de caixa e acento, RNF-BE-26) | *collation* ICU não determinística (`CREATE COLLATION … (provider = icu, locale = 'und-u-ks-level1', deterministic = false)`) para unicidade e ordenação. Para busca parcial (`q`), `unaccent` + `ILIKE`. A forma exata (e o suporte a `LIKE` com *collation* não determinística na versão escolhida) deve ser **validada no RF-BE-003**, primeiro requisito que usa busca. |
| Coluna gerada `ativa_unica` com índice único (RF-BE-002) | Índice único **parcial**: `CREATE UNIQUE INDEX uk_empresa_ativa_unica ON empresa ((true)) WHERE ativa`. A garantia de "no máximo uma empresa ativa" continua no banco. |
| `UNIQUE (empresa_id, codigo)` aceitando vários `NULL` (RF-BE-005) | comportamento igual no PostgreSQL |
| `CHECK` de preço (RF-BE-005) | igual (`CHECK` é aplicado) |
| Testcontainers MySQL | testcontainers-python com PostgreSQL (RNF-BE-25) |

## Consequências

- Os arquivos `RF-BE-*` continuam descrevendo tabelas com tipos MySQL; devem ser lidos com esta tabela. Os nomes de tabelas, colunas e restrições (`pk_cliente`, `fk_cliente_empresa`, `uk_empresa_ativa_unica`…) permanecem.
- README: o banco gerenciado do Render passa a ser a opção de produção; `MYSQL_ROOT_PASSWORD` some do `.env.example`.
- Busca insensível a acento é o ponto de maior risco técnico da troca; fica registrado como verificação obrigatória do RF-BE-003.
