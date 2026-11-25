# Histórico de desenvolvimento

Registro do desenvolvimento assistido por IA deste fork do MeuNegocio360: **prompts usados, decisões tomadas (por quem) e pontos a repensar**. O objetivo é poder revisitar, com calma, cada escolha que pode impactar o futuro do projeto, e aprender com o próprio uso da IA (disciplina de desenvolvimento com IA).

- **Ferramenta:** Claude Code (CLI), modelo Claude Sonnet 5.5, com modo de plano (`/plan`) antes de cada requisito.
- **Autor humano:** responde pelo código (RNF-013). A IA propõe e implementa; o autor aprova, ajusta ou rejeita.
- **Fonte de verdade do comportamento:** `docs/requisitos/` (escritos para Java/Spring/MySQL). A tecnologia deste fork é adaptada pelos ADRs em [`docs/adr/`](./adr).
- **Como manter:** a cada requisito, acrescentar uma etapa (prompt, decisões, resultado) e novas decisões `D-nnn`. Não reescrever o passado: se uma decisão mudar, registrar uma nova e marcar a antiga como *substituída*.

Legenda de autoria: **[Usuário]** decisão do autor humano · **[IA]** proposta da IA aceita pelo autor (explícita ou por aprovação do plano) · **[IA, a confirmar]** escolha da IA onde o requisito é omisso, ainda sem objeção do autor.

---

## 1. Linha do tempo

| Data | Etapa | Resultado | Onde |
| --- | --- | --- | --- |
| 24/11/2026 | 0. Overview, stack e preparação | Stack definida; adaptação para Python/FastAPI + PostgreSQL | ADRs 0001–0005, README, avisos nos RF |
| 24/11/2026 | 1. RF-BE-001 — autenticação (backend) | Login, refresh rotativo, logout, `/me`, deny-by-default | PR #1 (mergeado) |
| 24/11/2026 | 2. Endurecimento de config (pós-revisão do RF-BE-001) | `APP_ENV` obrigatório; `hide_parameters` | branch `chore/endurecimento-config-e-historico` |
| 24/11/2026 | 3. RF-FE-001 — login (frontend) | Tela de login, sessão em memória, renovação single-flight | PR #2 (mergeado) |
| 24/11/2026 | 4. RF-BE-002 — empresa e perfis (backend) | Implementado, verificado e mergeado | PR #3 (chore) e PR #4 (RF-BE-002), mergeados |
| 24/11/2026 | 5. Adendo ao RF-BE-002: `GET /empresa/inativas` | Endpoint de empresas inativas (reativação), paginação compartilhada | branch `feat/rf-be-002-empresas-inativas` |
| 24/11/2026 | 6. RF-FE-002 — empresa, layout e guardas (frontend) | Implementado e verificado em Chrome headless (seção 3.7); PRs ainda não abertos | branch `feat/rf-fe-002-empresa` (empilhada na `feat/rf-be-002-empresas-inativas`) |

---

## 2. Prompts usados (literais)

Os prompts abaixo são reproduzidos como foram escritos. As menções `@arquivo` anexam o arquivo ao contexto da IA.

### P0 — Overview e preparação (modo `/plan`)
> estou iniciando um projeto de estudos baseado em uma disciplina onde perdi as primeiras aulas na qual os alunos estão implementando os requisitos não funcionais. Copiei alguns docs de requisitos, README do repo do projetos, assim como o AGENTS.md. Quero primeiro que faça um overview dos requisitos e stack nos documentos. Estou pensando em escolher uma stack mais próxima de python no backend. Me diga qual a stack definida. Como foi iniciado o meunegocio360-js? Quero preparar o terreno para seguir nas aulas.

### P1 — Confirmação da stack
> Sim, confirmo que o backend será em Python FastAPI. Leia os requisitos e me liste o que muda. Aguarde meu ok para começarmos a implementar os requisitos

### P2 — Decisões técnicas e documentação
> migrations: siga o recomendado. acesso ao banco: sincrono. Troque pelo PostgreSQL. APScheduler dentro do app. Swagger: manter na /docs eu quero que seja a principal forma de testar o backend. Atualize o README. RF precisam de algum indicativo de que existe essas mudanças. Garanta os ADRs.

### P3 — Implementar o RF-BE-001 (modo `/plan`)
> @docs/requisitos/GERAIS.md @docs/requisitos/backend/RNF-BE.md Estou desenvolvendo um projeto de estudo para desenvolvimento com IA chamado de MeuNegocio360.
>
> Atue como um desenvolvedor de software sênior.
> Implemente o requisito RF-BE-001 referente à funcionalidade de autenticação, considerando as especificações gerais do projeto e específicas da funcionalidade em questão.

### P4 — PR do RF-BE-001 e regra de branches
> Abre o PR, eu sou o DavidBrito. Faça os ajustes necessários. Lembrando que os requisitos precisam ser desenvolvidos em branchs e não devem sumir no merge.

### P5 — Revisão e impacto
> Quais itens eu especificamente preciso revisar?

> qual impacto desses dois ajustes? A versão atual do back está funcional?

### P6 — Implementar o RF-FE-001 (modo `/plan`)
> @docs/requisitos/GERAIS.md @docs/requisitos/backend/RNF-FE.md
>
> Atue como desenvolvedor de software sênior. Faça a limpeza do módulo react, removendo os arquivos do template vite. Para o favicon, use a imagem @assets/icone_meunegocio360.png.
>
> Implemente o requisito RF-FE-001, considerando as especificações gerais do projeto e específicas dessa funcionalidade. No formulário da tela de login, use a imagem @assets/logo_meunegocio360_v2_sem_fundo.png localizado acima dos campos de entrada. Explique as modificações aplicadas com referências à documentação de requisitos e liste 3 testes manuais a serem realizados no navegador que atendam os critérios de aceitação especificados..

*(Nota: o caminho `backend/RNF-FE.md` digitado no prompt não existe; o arquivo correto é `frontend/RNF-FE.md`. A IA localizou o correto.)*

### P7 — Fechamento do RF-FE-001
> Ok, pode fechar a FE-001 no repositório

> passo a passo para os testes

> faça o merge com merge commit.

### P8 — Implementar o RF-BE-002 (modo `/plan`)
> @docs/requisitos/GERAIS.md @docs/requisitos/backend/RNF-BE.md
>
> Atue como desenvolvedor de software sênior.
>
> Implemente o requisito RF-BE-002, considerando as especificações gerais do projeto e específicas dessa funcionalidade. Liste 3 testes manuais a serem realizados no navegador com swagger que atendam os critérios de aceitação especificados.

### P9 — Aprovação do plano e pedido de registro
> Adiciona APP_ENV e hide_parameters. Cria um arquivo chamado, histórico de desenvolvimento. Essas decisões suas e minhas precisam ficar registradas. Já que é uma disciplina de IA, eu quero posteriormente pensar com calma em cada ponto desse pois podem impactar no futuro. O prompt usado é interessante também. Segue o plano. Aceito suas decisões.

### P10 — Implementar o RF-FE-002 (modo `/plan`)
> Implemente o requisito RF-FE-002, considerando as especificações gerais do projeto e específicas dessa funcionalidade. No menu de navegação, use a imagem para a brand assets\logo_meunegocio360_v1_branca.png localizado à esquerda dos itens do menu, no caso de telas grandes; em telas de dispositivos móveis, incluir ao centro entre o ícone de hambúrguer e o ícone de pesquisar, respeitando a paleta de cores do sistema, definida em RNF-FE.md. Explique as modificações aplicadas com referências à documentação de requisitos e liste 3 testes manuais a serem realizados no navegador que atendam os critérios de aceitação especificados. Dê atenção a usabilidade e disposição dos itens no menu.

*(Respostas do autor às perguntas do plano: ícone de pesquisar = placeholder desabilitado; reativação = acrescentar endpoint no backend; PRs #3 e #4 mergeados na `main`, usar a `main` como base.)*

### Padrão observado nos prompts (para reaproveitar)
1. **Contexto fixo por `@`:** `GERAIS.md` + `RNF-BE.md` (ou `RNF-FE.md`) em todo pedido de requisito; o RF é citado pelo ID.
2. **Papel + objetivo:** "Atue como desenvolvedor de software sênior" + "implemente o RF-XX considerando as especificações gerais e específicas".
3. **Plano antes do código:** `/plan` (alinha com a regra 2 do `AGENTS.md`); a IA só executa após aprovação.
4. **Entregáveis explícitos:** "explique as modificações com referências aos requisitos" e "liste 3 testes manuais" (ancora a verificação nos critérios de aceite).
5. **Regras de processo ditas na conversa:** branch por requisito, branch não some no merge, merge commit.
6. **Perguntas de revisão** ("o que preciso revisar?", "qual o impacto?") forçam a IA a separar o que está verificado do que não está.

---

## 3. Registro de decisões

Cada decisão tem **autor**, **alternativas** e **ponto para repensar** (impacto futuro). A coluna *Reversível?* estima o custo de mudar depois (**fácil**, **médio**, **difícil**).

### 3.1 Fundação (etapa 0)

| ID | Decisão | Autor | Alternativas / contexto | Ponto para repensar | Reversível? |
| --- | --- | --- | --- | --- | --- |
| D-001 | Backend em **Python/FastAPI** (os requisitos pedem Java/Spring). | Usuário (IA recomendou FastAPI + SQLAlchemy + Alembic + Pydantic + PyJWT + bcrypt + Ruff) | Outras opções em Python (Django REST, Flask) **não foram avaliadas**; a IA propôs só FastAPI. | A turma e a avaliação podem esperar Java/Spring; cada RF exige "traduzir" o texto original. Vale confirmar com o professor. | Difícil (reescrita) |
| D-002 | Manter o **texto original dos RF/RNF** e adaptar a tecnologia por **ADRs + avisos** no topo dos documentos (em vez de reescrevê-los). | IA, aceito pelo usuário (que pediu "um indicativo") | Reescrever os RF em Python. | Leitura dupla (texto Java + equivalência); risco de divergência entre o RF e o código ao longo do tempo. | Médio |
| D-003 | **Alembic padrão** (revisões em Python numeradas `0001_…`); `V<n>` dos RF = revisão `000n`. | IA recomendou, usuário aceitou | Alembic com SQL à mão em arquivos `V<n>__x.sql`; Flyway CLI. | Revisões em Python permitem `op.execute` de SQL específico (índice parcial), mas fogem do formato do RNF-BE-20. | Médio |
| D-004 | Acesso ao banco **síncrono** (SQLAlchemy + psycopg 3). | Usuário (IA recomendou) | `async` (asyncmy/asyncpg). | Concorrência/escala: rotas `def` rodam em *threadpool*. Migrar para `async` mexe em sessões e testes. | Difícil |
| D-005 | **PostgreSQL** no lugar de MySQL. | Usuário (motivo: Render oferece PostgreSQL gerenciado) | Manter MySQL (serviço privado pago ou externo). | Busca sem acento (collation ICU/`unaccent`) **não validada**: risco do RF-BE-003. Tipos MySQL dos RF precisam de tradução (ADR 0002). | Difícil |
| D-006 | **APScheduler dentro do app** para a limpeza de tokens. | Usuário | Cron/job externo. | Com várias instâncias, a tarefa roda em todas (idempotente, mas redundante). | Fácil |
| D-007 | **Swagger UI em `/docs`** como principal forma de testar; desligado em `prod`. | Usuário | `/swagger-ui.html` como no RNF-030. | O cookie `SameSite=Strict` e o `Origin` da Swagger exigem `http://localhost:8080` em `CORS_ALLOWED_ORIGINS`. | Fácil |
| D-008 | ADRs 0001–0005, README e `AGENTS.md` atualizados; RF com aviso de adaptação. | Usuário pediu; IA executou | — | Manter ADRs em sincronia quando algo mudar (ver regra no topo). | Fácil |

### 3.2 Processo e Git

| ID | Decisão | Autor | Alternativas / contexto | Ponto para repensar | Reversível? |
| --- | --- | --- | --- | --- | --- |
| D-009 | Commitar os docs na `main` **antes** de criar a branch do RF. | IA recomendou, usuário aceitou | Levar os docs junto na branch do RF. | O PR do RF fica limpo; mas a `main` recebeu commit direto. | Fácil |
| D-010 | **Uma branch por RF; branches não são excluídas; merge com *merge commit* (não *squash*).** | Usuário | O README original manda *squash* e `main` protegida. | Diverge do fluxo do instrutor; preserva o histórico do requisito (objetivo do autor). | Fácil |
| D-011 | A IA fez **push direto da `main`** (commit dos docs) para o PR do RF ficar só com o RF. | IA (a `main` não estava protegida) | Deixar os docs no PR do RF. | Contraria "`main` protegida: nada é enviado diretamente". Rever se o repositório passar a ter proteção. | Fácil |
| D-012 | O `origin` é o repositório do próprio usuário (`DavidBrito/meunegocio360`), **não um fork**; PRs são branch→`main` no mesmo repositório. | Usuário (esclareceu) | Fork + `upstream` do instrutor (README). | Sem `upstream`, não há sincronização com o repositório do instrutor. | Médio |
| D-013 | **Commits pequenos** (Conventional Commits + `[RF-…]`) e trailer `Co-Authored-By` da IA. | IA (segue README/instruções) | — | O histórico mostra que houve IA; útil para o "registro de uso de IA" do PR. | Fácil |
| D-014 | Itens de **endurecimento** (APP_ENV, hide_parameters) e este histórico vão em **branch própria** (`chore/…`), fora dos PRs de RF; o RF-BE-002 é empilhado sobre ela. | IA, aceito | Misturar no PR do RF-BE-002 (a regra diz "um PR não mistura RF"). | O PR do RF-BE-002 só deve ser mergeado **depois** do PR chore. | Fácil |

### 3.3 RF-BE-001 — Autenticação (backend)

| ID | Decisão | Autor | Alternativas / contexto | Ponto para repensar | Reversível? |
| --- | --- | --- | --- | --- | --- |
| D-020 | **Deny-by-default por middleware** com lista pública explícita (`PUBLIC_ROUTES`), inclusive para rotas inexistentes (401 em vez de 404). | IA | Dependência de autenticação por router (esquecer em uma rota nova a deixaria pública). | Toda rota nova pública precisa entrar na lista de propósito. Um teste que percorra todas as rotas é desejável na fase de testes. | Médio |
| D-021 | Camadas `domain` (dataclasses + Protocols) / `application` (casos de uso + Unit of Work) / `infra` (SQLAlchemy) / `api`. | IA (por RNF-010/BE-01..05) | Usar o ORM direto nos casos de uso (menos código). | Mais código e mapeamento domínio↔modelo; ganho em testabilidade e regra de dependência. | Difícil |
| D-022 | **Refresh com ordem de travas usuário → token** (`SELECT … FOR UPDATE`); renovações simultâneas do mesmo usuário se serializam; reuso revoga a família e faz `commit` **antes** de levantar o erro. | IA | Lock só no token (risco de deadlock com o login). | Pontos de maior risco de bug sutil; revisar com atenção. | Médio |
| D-023 | **Login:** a 5ª falha consecutiva bloqueia, zera o contador, revoga as sessões e **ainda responde 401**; o `429` começa na tentativa seguinte (como no README). Usuário inativo **não** incrementa o contador. | IA | Responder `429` já na 5ª. | UX e segurança: o RF permite as duas leituras. | Fácil |
| D-024 | **`/me` devolve 401 se o usuário foi desativado** (RN-02). | IA, aceito (listado no PR) | Devolver os dados do token. | O RF não especifica. | Fácil |
| D-025 | Senha limitada a **72 bytes** UTF-8, além de 8–72 caracteres (limite do bcrypt). | IA | Só contar caracteres. | Senhas com acentos podem ser recusadas antes do que o usuário espera. | Fácil |
| D-026 | **Sem `email-validator`**: regex própria para o e-mail (a lista de dependências do RF não o inclui). | IA (RNF-015) | Adicionar a dependência. | Regex simples aceita menos casos que a biblioteca. | Fácil |
| D-027 | Erros de validação saem como **400** (não 422) e o `422` padrão foi **removido do OpenAPI**; o valor recebido nunca é ecoado. | IA (RNF-BE-14) | Manter o 422 do FastAPI. | Consistência com o RF; mensagens em pt-BR mapeadas à mão (cobertura parcial dos tipos de erro do Pydantic). | Fácil |
| D-028 | **Seed no `lifespan`** em `dev` (idempotente), senhas só por variável de ambiente. | IA | Comando separado. | O app faz escritas no banco ao subir em dev. | Fácil |
| D-029 | A IA **gerou o `.env` local** com segredos aleatórios (não versionado) para testar, sem mostrá-los. | IA | Pedir ao usuário. | Rever se algum segredo foi exposto em logs/terminais da sessão (os valores não foram impressos de propósito). | Fácil |
| D-030 | **JWT HS256** com a claim `perfil` confiada até a expiração (15 min). | RF (decisão do requisito) | RS256/JWKS (RNF-094, exigido antes de um 2º serviço validar tokens). | Mudança de perfil/desativação só vale após a renovação; migrar para RS256 quando houver outro serviço. | Médio |
| D-031 | `Dockerfile` roda `alembic upgrade head` **na subida do contêiner**. | IA | Etapa de release separada. | Com várias instâncias, duas migrations podem competir. | Fácil |
| D-032 | O `uv init` gravou o **e-mail do git** em `pyproject.toml`; a IA **removeu antes do commit** (privacidade). | IA | — | Conferir que nenhum dado pessoal foi parar nos arquivos versionados. | Fácil |

### 3.4 Endurecimento pós-revisão (etapa 2)

| ID | Decisão | Autor | Alternativas / contexto | Ponto para repensar | Reversível? |
| --- | --- | --- | --- | --- | --- |
| D-040 | **`APP_ENV` obrigatório**, sem padrão. O `.env` da raiz é lido **se existir** (não depende mais de `APP_ENV=dev`); variáveis do processo prevalecem. | Usuário pediu; IA implementou | Padrão `prod` (exigiria `APP_ENV=dev` no shell, quebrando o fluxo do README). | Antes, esquecer `APP_ENV` num deploy subia como `dev` (seed, Swagger, cookie sem `Secure`): a falha era "aberta". Agora falha ao iniciar. Depende de o `.env` nunca existir na imagem (`.dockerignore`). | Fácil |
| D-041 | **`hide_parameters=True`** no engine. | Usuário pediu; IA implementou | Filtrar parâmetros nos logs. | Verificado: antes o e-mail aparecia na mensagem de erro do banco; agora não. Debug de erros de banco perde os valores. | Fácil |

### 3.5 RF-FE-001 — Login (frontend)

| ID | Decisão | Autor | Alternativas / contexto | Ponto para repensar | Reversível? |
| --- | --- | --- | --- | --- | --- |
| D-050 | **Node 22 LTS** via nvm (o ambiente tinha Node 18; Vite 8 / ESLint 10 / `react-router` 8 exigem ≥ 20.19/22.22). | Usuário (IA recomendou) | Manter Node 18 (não roda). | `engines` no `package.json`; README diz Node 22. | Fácil |
| D-051 | Branch do FE saiu da branch do BE; após o merge do PR #1, da `main`. | Usuário | Sempre da `main`. | O PR do FE trouxe só commits do FE. | Fácil |
| D-052 | Versões instaladas **mais novas que o conhecimento da IA** (React Router 8, Zod 4, RHF 7, `@hookform/resolvers` 7): APIs conferidas no `node_modules`/changelog (regra 6 do `AGENTS.md`). | IA | — | Risco de a IA "inventar" API; sempre conferir a versão instalada. | — |
| D-053 | Lógica de sessão numa **closure fora do React** (`sessionManager`), com `AuthProvider` fino. | IA | Hooks/`useEffect` espalhados. | Facilita a fase de testes e o StrictMode; foge do exemplo "tudo em hooks". | Médio |
| D-054 | **Só um `401` na renovação encerra a sessão**; falha de rede mantém a sessão. | IA | Qualquer falha de renovação encerra (leitura literal do RF). | Mais tolerante; pode manter sessão "morta" até o próximo 401. | Fácil |
| D-055 | O redirecionamento pós-login é feito pelo **`PublicOnly`**, não pelo formulário. | IA | `navigate()` no `onSuccess`. | Evita corrida entre dois redirecionamentos. | Fácil |
| D-056 | Nome do produto no login vem do **logo** (com `alt`); único `h1` é "Entrar". | IA | Texto visível extra. | O RF cita "nome do produto"; confirmar com o autor. | Fácil |
| D-057 | **Favicon/logo reduzidos** com ImageMagick (32/192/180 px; logo 480 px, PNG8). | IA | Usar os originais (315 kB/259 kB). | Qualidade do logo conferida visualmente. | Fácil |
| D-058 | Verificação ponta a ponta por **scripts descartáveis** (Chrome headless via DevTools Protocol), **fora do repositório**. | IA (regra 9: sem testes automatizados fora da fase) | Versionar os scripts. | Os resultados não são reproduzíveis por outras pessoas; na fase de testes viram Vitest/MSW/Playwright. | Fácil |
| D-059 | `npm audit fix` alterou dependências **de desenvolvimento** do template. | IA | Deixar 3 avisos moderados. | O `package-lock.json` mudou além das dependências do RF. | Fácil |

### 3.6 RF-BE-002 — Empresa e perfis (plano aprovado e implementado)

| ID | Decisão | Autor | Alternativas / contexto | Ponto para repensar | Reversível? |
| --- | --- | --- | --- | --- | --- |
| D-060 | O `Location` do `201` aponta para `/api/v1/empresa` (não existe `GET /empresa/{id}`). | IA, aceito pelo usuário | `/api/v1/empresa/{id}`. | Se um `GET /empresa/{id}` surgir, ajustar. | Fácil |
| D-061 | `PUT`/`PATCH` com `id` inexistente → **`404 COMPANY_NOT_FOUND`** (código novo, não previsto no RF). | IA, aceito | Reutilizar `COMPANY_NOT_REGISTERED`. | Novo `code` entra no contrato com o frontend (RF-FE-002). | Fácil |
| D-062 | `PUT` permitido em empresa **inativa**; `PATCH` sem mudança de situação é **idempotente** (200, sem incrementar a versão). | IA, aceito | Proibir edição de inativa; sempre incrementar. | Regra de negócio não especificada. | Fácil |
| D-063 | A claim `perfil` é confiada por até 15 min: token emitido com `USUARIO` recebe `403` nas escritas até renovar. | IA, aceito | Reler o perfil no banco a cada requisição. | Custo de uma consulta por requisição vs. janela de inconsistência (relacionado a D-030). | Médio |
| D-064 | `Perfil` passa a ficar em **`shared`** (importado por `auth` e `empresa`), com a dependência `require_perfis`. | IA | Duplicar o enum ou `empresa` importar de `auth`. | RNF-BE-05 (uma feature não acessa internals de outra). | Médio |
| D-065 | `EmpresaAtiva` é a **única** interface de `empresa` para outras features. | RF | — | RF-BE-003/004/005 devem usar só ela. | Difícil |
| D-066 | **CNPJ duplicado é verificado antes de "já existe ativa"** no cadastro. | IA (para atender ao cenário "CNPJ duplicado" do RF) | Inverter a ordem. | O RF não diz a precedência; o cenário de aceite só passa com esta. | Fácil |
| D-067 | Corridas (dois cadastros simultâneos) são resolvidas **pelo banco** (índice único parcial e `uk_empresa_cnpj`); a infra **traduz o nome da restrição** violada em erro de negócio. | IA (pontos de atenção do RF) | Só `if` na aplicação (condição de corrida). | Depende de o nome da restrição vir no erro do driver (psycopg 3): verificado com 2 POSTs simultâneos. | Médio |
| D-068 | `versao` **começa em 0** (contrato do RF) via `version_id_generator`; a comparação com a versão enviada é explícita (lock `FOR UPDATE`) e o ORM é a segunda barreira. | IA | Padrão do SQLAlchemy (começa em 1, como `usuario`). | `usuario` começa em 1 e `empresa` em 0: inconsistência entre tabelas (RNF-BE-22 não fixa o valor inicial). | Médio |
| D-069 | **CNPJ só com 14 dígitos, sem máscara** (RNF-BE-27); com máscara → 400. | IA | Aceitar máscara e normalizar (o RF-BE-003 pede aceitar máscara em documentos). | Contrato diferente entre empresa e cliente. | Fácil |
| D-070 | Campos opcionais em branco viram `null`; fuso validado por `ZoneInfo` (com filtro de chave); `moeda` só `BRL`. | IA | Validar contra `available_timezones()`. | A validação IANA depende do `tzdata` do sistema (confirmado na imagem Docker slim). | Fácil |
| D-071 | `CamelModel`, `bearer_scheme`, `Perfil`, `require_perfis` e os validadores foram movidos para `shared` (refactors mínimos em `auth`). | IA | Duplicar em cada feature. | `shared` cresce; deve conter só o que é técnico/transversal (RNF-093). | Médio |
| D-072 | Conexão com o banco em **UTC** (`-c timezone=UTC`) e respostas convertidas para UTC. | IA (RNF-033) | Confiar no fuso do servidor. | — | Fácil |
| D-073 | O `downgrade` da migration `0003` é **com perda** (os dois perfis de operador voltam a `USUARIO`). | IA | Não oferecer downgrade. | Verificado num roundtrip no banco de dev (e restaurado à mão). | Fácil |

### 3.7 Adendo ao RF-BE-002 e RF-FE-002 — empresas inativas, layout e guardas

| ID | Decisão | Autor | Alternativas / contexto | Ponto para repensar | Reversível? |
| --- | --- | --- | --- | --- | --- |
| D-080 | **Ícone de pesquisar = placeholder desabilitado**, só no mobile (nenhum RF define busca global). | Usuário (entre 3 opções propostas pela IA) | Campo de busca sem função; placeholder também no desktop. | Reserva o lugar no layout; vira função quando existir busca global. | Fácil |
| D-081 | **Novo endpoint `GET /empresa/inativas`** (ADMIN, paginado) para permitir a reativação após recarregar. É um **adendo ao RF-BE-002** (contrato que o requisito original não tem). | Usuário (a IA apontou a lacuna e ofereceu "reativar só na mesma sessão" como alternativa) | Guardar `id`/`versao` em memória (perde-se ao recarregar). | O fork passa a divergir do contrato original; documentado como adendo em `RF-BE-002.md`. | Médio |
| D-082 | A listagem usa uma **paginação compartilhada** (`shared/pagination.py`: `page`, `size` ≤ 100, `sort` com lista permitida, `Page`), já pensada para RF-BE-003/004/005. | IA | Paginação só nesta rota. | O padrão do RNF-BE-13/16 fica definido uma vez; `AppError` ganhou `errors[]`. | Médio |
| D-083 | A Parte A (backend) vai em **PR próprio, antes** do PR do frontend; a branch do FE sai dela (empilhada). | IA, aceito (plano aprovado) | Incluir o endpoint no PR do FE (mistura RF). | Ordem de merge: backend primeiro. | Fácil |
| D-084 | **Logo branca sobre o laranja** da marca na barra, como o autor pediu, mesmo com o contraste de 3,7:1 (logotipo é isento de contraste de texto no WCAG 1.4.3). | Usuário pediu; IA avaliou o risco | Usar a logo preta; mudar o fundo da barra. | Conferido em captura (desktop e 360 px): legível, com traço grosso preenchido de branco. O RNF-FE 2.2 proíbe *texto* branco sobre o laranja; a logo é imagem. | Fácil |
| D-085 | Navbar: texto, links e ícones **Pretos** (variáveis `$navbar-light-*` no tema); item ativo com **negrito + sublinhado + `aria-current`** (não só cor); hover sublinha. | IA (RNF-FE 2.2) | `navbar-dark`/texto branco (proibido). | Pequeno CSS próprio no tema (`.navbar-botao-icone`, `.navbar-empresa`). | Fácil |
| D-086 | Mobile: `[☰][logo centralizado][🔍]` com os dois botões **do mesmo tamanho** (44 px) e a logo com `mx-auto`; menu empilhado que **fecha ao navegar**; `$nav-link-padding-y` ampliado (alvos ≥ 44 px). | IA | Logo à esquerda no mobile (não pedido). | Centralização depende de os botões terem a mesma largura (verificado: ±6 px). | Fácil |
| D-087 | `EmpresaProvider` **bloqueia a renderização** (carregando/erro) para todas as rotas protegidas, em vez de só `RequireEmpresa` tratar o erro; a tela de erro tem **Tentar novamente** e **Sair**. | IA | Tratar o estado de erro só em `RequireEmpresa` (como diz o RF). | Evita *flash* e mantém uma única consulta; `/empresa` também fica coberta. | Médio |
| D-088 | `GET /empresa` 404 vira **estado `ausente`**, não erro; após Inativar o cache vai a `null`, e as guardas redirecionam o ADMIN. | IA (RF-FE-002) | Tratar como erro genérico (ponto de atenção do RF). | — | Fácil |
| D-089 | **Reativação pela lista** de inativas na tela de cadastro (sem confirmação extra; o RF só exige confirmar a inativação). | IA | Modal também na reativação. | Ação reversível (basta inativar de novo). | Fácil |
| D-090 | O destino pós-sucesso (`/` após cadastrar, `/empresa` após reativar) é guardado em **estado do React antes da requisição**, pois o cache atualiza antes de o envio resolver. | IA | `ref` (proibido ler `ref.current` em render pelo lint do React 19). | Detalhe sutil de ordem de eventos; revisar. | Fácil |
| D-091 | O campo **Moeda** é um `select` desabilitado **fora do formulário** (valor `BRL` fixo no payload), pois o RHF devolve `undefined` para campos `disabled`. | IA | Registrar o campo desabilitado. | Quando houver outras moedas, vira campo registrado. | Fácil |
| D-092 | CNPJ e telefone usam `Controller` + `MaskedInput` (valor mascarado no estado, **só dígitos no payload**); funções únicas em `shared/lib/documentos.js`. | IA (RNF-FE-28, RNF-015) | Biblioteca de máscara (proibida pelo RF). | O algoritmo do CNPJ existe em Python e em JavaScript: manter sincronizados. | Médio |
| D-093 | O menu é uma lista (`app/menu.js`) com os perfis de cada item; os RF seguintes só acrescentam linhas. | IA | `if` por perfil no JSX. | — | Fácil |
| D-094 | `RequireRole` mostra **"Acesso negado" sem redirecionar** e fica em `features/auth` (concerne a perfil, não à empresa). | IA | Redirecionar ao início. | A guarda do cadastro fica abaixo do `EmpresaProvider`: a consulta da empresa (feita uma vez por sessão para a barra) acontece mesmo em "Acesso negado"; a **página** não faz requisição. | Fácil |
| D-095 | **Correção de um bug de UX encontrado nos testes:** após **Sair**, o próximo usuário era levado à última página do anterior; agora a saída voluntária não preserva `from` (flag `saiu`). | IA (achado ao testar) | Limpar `from` no login. | Visitante sem sessão e sessão expirada continuam preservando a rota (RF-FE-001). | Fácil |

---

## 4. Uso da IA: acertos, erros e lições

| Observação | Tipo | Registro |
| --- | --- | --- |
| A IA propôs `APP_ENV` com padrão `dev` (falha "aberta"); só a revisão apontou o risco. | Erro da IA | Corrigido em D-040. Lição: perguntar "o que acontece se esta variável faltar em produção?". |
| Mensagens de erro do SQLAlchemy incluíam parâmetros (e-mail) por padrão; a IA não habilitou `hide_parameters` de início. | Omissão | Corrigido em D-041; demonstrado antes/depois. |
| A IA listou o risco do `.env`/`APP_ENV` e do `hide_parameters` **na revisão pedida pelo autor**, não ao implementar. | Processo | A pergunta "o que preciso revisar?" revelou riscos que o plano não destacava. |
| O `uv init` gravou o e-mail pessoal no `pyproject.toml`. | Quase-vazamento | Removido antes do commit (D-032). Lição: revisar o *diff* de arquivos gerados por ferramentas. |
| Versões de bibliotecas posteriores ao conhecimento da IA. | Risco | Conferidas no `node_modules`/`uv` (D-052). |
| Os scripts de verificação ponta a ponta não estão no repositório. | Limitação | D-058. |
| Um servidor antigo ficou ocupando a porta 8080 e o novo falhou ao subir (o `seed` rodou, o bind falhou): a primeira verificação do RF-BE-002 bateu no código velho (500 no login do operador). | Falha de ambiente | Detectado pelo `500` e pelo log (`address already in use`); resolvido matando o processo pelo PID. Lição: conferir qual processo atende a porta antes de verificar. |
| `aoSalvar?.(await salvar.mutateAsync(...))`: com `aoSalvar` indefinido o JavaScript **não avalia o argumento**; a requisição de cadastro nunca saía e nenhum erro aparecia. | Erro da IA | Achado pelo teste ponta a ponta (sem requisição no *backend*) e corrigido (`await` em variável antes). Lição: **verificar o efeito no servidor**, não só a tela. |
| Usei a classe `border-lg-0`, que **não existe** no Bootstrap (uma linha escura apareceu no desktop). | Erro da IA | Visto na captura de tela; trocado por `<hr class="d-lg-none">`. Lição: conferir utilitários na documentação da versão. |
| O lint do React 19 (`react-hooks/refs`) rejeitou o `field` do `Controller` e o `ref` lido dentro do callback do `handleSubmit`. | Regra do projeto | Adaptado (`MaskedInput` recebe props soltas; guarda de envio no *handler* do evento). |
| Dois servidores Vite (portas 5173 e 5174) e Chrome de execuções anteriores ficaram vivos; testes de timing falsos (React mantém a tela antiga durante o carregamento *lazy*). | Falha de ambiente/teste | Esperar a tela estabilizar antes de ler o texto; encerrar processos por PID/porta. |
| `pkill -f` com o padrão presente na própria linha de comando derrubou o shell **de novo**. | Falha de ferramenta | Usar PID/porta (já anotado). |
| Um comando `pkill -f` derrubou o próprio shell da sessão (padrão contido na linha de comando). | Falha de ferramenta | Sem impacto no repositório; passou a matar por PID/porta. |
| Divergência de fluxo: o README manda *squash* e `main` protegida; o autor optou por merge commit e branches mantidas. | Decisão consciente | D-010, D-011. |

---

## 5. Pendências e pontos em aberto

1. **Alinhar com o professor/turma** que o backend é Python/FastAPI + PostgreSQL (D-001, D-005).
2. **Validar a busca sem acento no PostgreSQL** (collation ICU não determinística + `unaccent`) no RF-BE-003 (ADR 0002).
3. **RS256/JWKS** antes de qualquer segundo serviço validar tokens (D-030, RNF-094).
4. **Rodar axe/Lighthouse** e registrar o resultado no PR do RF-FE-001 (não foi verificado).
5. **Validar o deploy** no Render/Netlify (Dockerfile e rewrite de `/api` não testados em produção).
6. **Decidir se os scripts de verificação** entram no repositório antes da fase de testes (D-058).
7. **Revisar linha a linha** o código gerado (RNF-013): `refresh.py`, `login.py`, `shared/security.py`, `shared/errors.py`, `sessionManager.js`, `client.js`.
8. **Rever D-063/D-030**: reler o perfil no banco ou aceitar a janela de 15 min.
9. **Ordem de merge atual:** PR do adendo `feat/rf-be-002-empresas-inativas` primeiro; depois o PR `feat/rf-fe-002-empresa` (empilhado).
10. **Contrato do CNPJ:** decidir se empresa e cliente aceitam máscara (D-069) e se `versao` deve começar sempre em 0 (D-068).
12. **Rodar axe/Lighthouse** na barra, no formulário e nas páginas de acesso negado/aguardando (RF-FE-002; não medido).
13. **Sincronizar** as duas implementações de CNPJ (Python e JavaScript) se uma mudar (D-092).
11. **Validar com o autor** os códigos novos (`COMPANY_NOT_FOUND`) antes de o RF-FE-002 depender deles (D-061).
