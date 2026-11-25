# ADR 0006 — Busca sem distinção de acento e caixa no PostgreSQL

- **Status:** aceito (resolve a pendência "a validar no RF-BE-003" do [ADR 0002](./0002-banco-postgresql.md))
- **Data:** 24/11/2026
- **Relacionados:** [ADR 0002](./0002-banco-postgresql.md), RNF-BE-16, RNF-BE-26, RF-BE-003 (RF-BE-004 e RF-BE-005 reutilizam)

## Contexto

O RNF-BE-26 pede colunas de texto pesquisáveis com *collation* sem distinção de maiúsculas e acentos (`utf8mb4_0900_ai_ci` no MySQL), e o RF-BE-003 pede busca "contém" por nome. O ADR 0002 propôs uma *collation* ICU não determinística mais `unaccent`, marcando o ponto como risco a validar.

## Verificação (PostgreSQL 16.16, imagem `postgres:16-alpine`, em transações com `ROLLBACK`)

| Verificação | Resultado |
| --- | --- |
| *Collation* ICU não determinística `und-u-ks-level1`: igualdade `José = jose` | funciona (a *collation* padrão `en_US.utf8` dá `false`) |
| `ORDER BY` com essa *collation* | correto: Aaron, Álvaro, ana, João, José, Zélia (a padrão põe ana e Álvaro no fim) |
| `LIKE`, `ILIKE` e `strpos` com *collation* não determinística | **não suportados no PostgreSQL 16** (`nondeterministic collations are not supported for LIKE`) |
| `unaccent(text)` | `STABLE`: não serve em índice/coluna gerada; com *wrapper* `IMMUTABLE` serve |
| `lower(f_unaccent(nome)) LIKE …` sobre coluna com a *collation* ICU | falha (a expressão herda a *collation*); com `COLLATE "default"` explícito funciona |
| Parâmetro normalizado no banco (`lower(f_unaccent(:q))`) | `ÁLVARO` acha "Álvaro Souza" |
| `%` e `_` no termo | casam tudo/qualquer caractere: precisam de `ESCAPE` |
| Violação de unicidade | o erro traz o nome da restrição (traduzível em erro de negócio) |

## Decisão

- Coluna `nome` com a *collation* ICU `ci_ai` (`CREATE COLLATION ci_ai (provider = icu, locale = 'und-u-ks-level1', deterministic = false)`), usada para **ordenação e igualdade** sem acento/caixa (e para cumprir o RNF-BE-26).
- Busca "contém": `lower(f_unaccent(nome)) COLLATE "default" LIKE '%' || lower(f_unaccent(:q)) || '%' ESCAPE '\'`, com `:q` como **parâmetro vinculado** e os curingas (`\`, `%`, `_`) escapados (`shared/busca.py`).
- `f_unaccent(text)`: *wrapper* `IMMUTABLE` de `unaccent` criado na migration (reaproveitado por RF-BE-004/005).
- Busca por documento: prefixo dos dígitos informados, ignorando a máscara, quando o termo só tem dígitos e máscara.
- Sem índice *trigram* (`pg_trgm`) por ora: a instalação atende uma empresa e a tabela é pequena; o filtro por `empresa_id` já usa índice. Revisar com volume.

## Consequências

- A extensão `unaccent` e a *collation* ICU passam a ser pré-requisito do banco (migration `0005`). `unaccent` é uma extensão *trusted* a partir do PostgreSQL 13, então não exige superusuário; **não foi confirmado que o PostgreSQL gerenciado do Render permite `CREATE EXTENSION unaccent` e `CREATE COLLATION … icu`**: verificar no primeiro deploy.
- O PostgreSQL 18 passa a aceitar `LIKE` com *collation* não determinística; se o provedor oferecer essa versão, a busca pode ser simplificada.
- O `downgrade` da migration remove a função, a *collation* e a extensão.
