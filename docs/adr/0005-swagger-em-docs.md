# ADR 0005 — Swagger UI em `/docs` como principal forma de testar o backend

- **Status:** aceito
- **Data:** 24/11/2026
- **Relacionados:** [ADR 0001](./0001-backend-python-fastapi.md)

## Contexto

Os requisitos (RNF-030, README) indicam Swagger UI em `/swagger-ui.html` (springdoc). O FastAPI gera OpenAPI e Swagger UI nativamente, em `/docs` (e `/openapi.json`). Neste projeto a Swagger UI é a **principal forma de verificar manualmente** os critérios de aceite (o README ainda traz roteiros de Postman como alternativa).

## Decisão

- Manter os caminhos padrão do FastAPI: Swagger UI em `/docs` e esquema em `/openapi.json`. Onde os documentos dizem `/swagger-ui.html`, leia `/docs`.
- Disponíveis em `dev` e `test`; **desabilitados em `prod`** (RNF-030, RF-BE-001 "pontos de atenção").
- O esquema `Bearer` deve estar declarado no OpenAPI para que o botão **Authorize** da Swagger UI funcione com o `accessToken` do login.
- Cada endpoint declara exemplos de sucesso e de erro (`problem+json`) em `responses=` (RNF-030, RNF-BE-14).

## Consequências

- O cookie `mn360_refresh` tem `Path=/api/v1/auth` e `SameSite=Strict`; a Swagger UI servida pelo mesmo host (`http://localhost:8080/docs`) permite testar login/refresh/logout porque a origem é a mesma da API. Em `dev`, o cookie `Secure` pode ser desligado (RF-BE-001).
- O cabeçalho `Origin` enviado pela Swagger UI (`http://localhost:8080`) precisa constar em `CORS_ALLOWED_ORIGINS` no perfil `dev`, senão `/auth/refresh` e `/auth/logout` respondem `403 ORIGIN_NOT_ALLOWED`.
