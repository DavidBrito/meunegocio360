# ADR 0004 — Tarefas agendadas com APScheduler dentro do app

- **Status:** aceito
- **Data:** 24/11/2026
- **Relacionados:** [ADR 0001](./0001-backend-python-fastapi.md)

## Contexto

O RF-BE-001 exige a remoção periódica de refresh tokens expirados ou revogados há mais de 30 dias (`@Scheduled` no original). Não há cron separado na implantação prevista (Render, plano simples).

## Decisão

APScheduler (`BackgroundScheduler`) iniciado e encerrado no *lifespan* do FastAPI, com a tarefa de limpeza diária. A dependência é introduzida no RF-BE-001 (RNF-015).

## Consequências

- Com mais de uma instância do serviço, a tarefa rodaria em todas. É aceitável aqui porque a limpeza é idempotente; se houver escala horizontal, rever (por exemplo, job externo).
- O agendador deve poder ser desligado por configuração (útil em testes).
- A tarefa não registra e-mail, token nem IP (RNF-025, RNF-BE-44).
