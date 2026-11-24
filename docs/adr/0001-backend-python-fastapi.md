# ADR 0001 — Backend em Python com FastAPI

- **Status:** aceito
- **Data:** 24/11/2026
- **Decide:** stack do backend (substitui Java 17 + Spring Boot 4 + Maven descritos nos requisitos originais)
- **Relacionados:** [ADR 0002](./0002-banco-postgresql.md), [ADR 0003](./0003-sqlalchemy-sincrono-e-alembic.md), [ADR 0004](./0004-apscheduler-no-app.md), [ADR 0005](./0005-swagger-em-docs.md)

## Contexto

Os requisitos originais (`docs/requisitos/`) foram escritos para Java 17+ e Spring Boot. Este fork é um projeto de estudos cujo autor prefere Python no backend. O frontend (React + Vite) e todos os **contratos de API** (caminhos, payloads, códigos de erro, cookie `mn360_refresh`, claims do JWT, regras de negócio e critérios de aceite) não mudam, de modo que o frontend das aulas continua funcionando contra este backend.

## Decisão

- **Linguagem e framework:** Python 3.12+ e FastAPI (servidor ASGI: uvicorn).
- **Gerenciador de pacotes:** `uv`; `pyproject.toml` e `uv.lock` substituem `pom.xml` como fonte da verdade das versões.
- **Validação e DTOs:** Pydantic v2, com *alias* `camelCase` (RNF-BE-11).
- **Persistência:** SQLAlchemy 2.x, síncrono, e Alembic ([ADR 0003](./0003-sqlalchemy-sincrono-e-alembic.md)) sobre PostgreSQL ([ADR 0002](./0002-banco-postgresql.md)).
- **Configuração:** `pydantic-settings` (falha na inicialização se faltar variável obrigatória).
- **Segurança:** PyJWT (HS256 com algoritmo fixado) e `bcrypt`.
- **Qualidade:** Ruff (formatação e lint) no lugar do Spotless.
- **Testes (fase de testes):** pytest, `TestClient`/httpx, testcontainers-python, `import-linter` (no lugar do ArchUnit) e coverage.py (no lugar do JaCoCo).
- **Estrutura:** `meunegocio360-core/src/meunegocio360_core/<feature>/{api,application,domain,infra}` e `shared/`, mantendo RNF-010/011 e RNF-BE-05.

### Equivalências (como ler os requisitos originais)

| Nos requisitos (Java/Spring) | Neste projeto (Python) |
| --- | --- |
| `pom.xml`, Maven Wrapper, `./mvnw verify` | `pyproject.toml`, `uv`, comando único de verificação (`uv run ruff format --check . && uv run ruff check .`, ampliado na fase de testes) |
| Spotless (google-java-format) | Ruff (`ruff format` e `ruff check`) |
| Spring MVC, controller | FastAPI, *router* (fino, RNF-BE-01) |
| DTO `record` | Modelo Pydantic v2 |
| Entidade JPA / `@Version` / `@Transactional` | Modelo SQLAlchemy / `version_id_col` / transação gerenciada na camada `application` (Unit of Work) |
| Injeção por construtor, `@Autowired` | Dependências no `__init__` dos casos de uso; `Depends()` nos *routers* |
| `@RestControllerAdvice` | `exception_handler` único em `shared`; o 422 padrão do FastAPI é convertido em `400 VALIDATION_ERROR` com `errors[]` |
| `SecurityFilterChain` *deny-by-default* | Dependência de autenticação aplicada ao *router* raiz, com lista explícita de rotas públicas (RNF-021, RNF-BE-40) |
| `@PreAuthorize` | Dependência de autorização por perfil (`Depends`), com `403 ACCESS_DENIED` (RNF-BE-47) |
| `DelegatingPasswordEncoder` (`{bcrypt}…`) | `bcrypt` direto; o prefixo `{bcrypt}` na coluna `senha_hash` é dispensável |
| Nimbus `JwtEncoder`/resource-server | PyJWT, com `algorithms=["HS256"]`, validação de `iss` e `exp` e rejeição de `alg: none` |
| `SecureRandom` | `secrets` |
| `Clock` injetável | Objeto/`Callable` de relógio injetado nos casos de uso |
| Filtro + MDC (`X-Request-Id`) | Middleware ASGI + `contextvars` + `logging.Filter` (RNF-BE-43) |
| Logs estruturados nativos do Boot | Formatador JSON da biblioteca padrão (`logging`), sem dependência nova (RNF-BE-44) |
| CORS por *bean* | `CORSMiddleware` (sem `*`, com credenciais) |
| Cabeçalhos do Spring Security | Middleware próprio com os mesmos cabeçalhos (RNF-BE-41) |
| `application-{perfil}.yaml`, `spring.config.import` | Variável `APP_ENV` (`dev`, `test`, `prod`) e `.env` lido apenas em `dev` (RNF-BE-31) |
| `server.port: ${PORT:8080}` | `PORT` (padrão 8080) |
| springdoc, `/swagger-ui.html` | OpenAPI nativo do FastAPI, Swagger UI em `/docs` ([ADR 0005](./0005-swagger-em-docs.md)) |
| Actuator `/actuator/health` | Rota própria `/actuator/health` (mantida para RNF-051 e RNF-104), sem detalhes |
| `@Scheduled` | APScheduler dentro do app ([ADR 0004](./0004-apscheduler-no-app.md)) |
| Flyway `V<n>__x.sql`, `ddl-auto=validate` | Alembic ([ADR 0003](./0003-sqlalchemy-sincrono-e-alembic.md)); `alembic check` no lugar do `validate` |
| MockMvc, Testcontainers, JUnit/Mockito | `TestClient`, testcontainers-python, pytest/`unittest.mock` |
| `Dockerfile` Temurin JDK/JRE | `Dockerfile` *multi-stage* Python (RNF-100), usuário não-root, escutando em `$PORT` |

## Consequências

- Os requisitos permanecem como fonte da verdade do **comportamento**. Onde citam Java/Spring/MySQL, vale a equivalência acima e o [ADR 0002](./0002-banco-postgresql.md). Cada arquivo de requisito de backend traz um aviso apontando para estes ADRs.
- A lista "Dependências introduzidas" do RF-BE-001 foi reescrita para Python (RNF-015); o que não estiver lá não deve ser adicionado.
- A segurança *deny-by-default* deixa de ser um padrão do framework: esquecer a dependência numa rota nova a deixaria pública. Mitigação: o *router* raiz já a aplica e, na fase de testes, um teste percorre todas as rotas.
- O professor/turma usa Java; divergências futuras entre os requisitos e este fork devem ser registradas em novo ADR.
