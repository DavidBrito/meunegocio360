# meunegocio360-js

Frontend único do MeuNegócio360 (React 19 + Vite + JavaScript + Bootstrap 5).
Arquitetura, estilos e regras: [`docs/requisitos/frontend/`](../docs/requisitos/frontend).

## Como rodar

Requer Node 22 LTS (Vite 8 e ESLint 10) e o backend em execução (ver [README da raiz](../README.md)).

```bash
cp .env.example .env.local
npm install
npm run dev        # http://localhost:5173 (a API em /api é repassada ao backend, vite.config.js)
```

| Comando                                   | Para quê                     |
| ----------------------------------------- | ---------------------------- |
| `npm run lint`                            | ESLint                       |
| `npm run format` / `npm run format:check` | Prettier                     |
| `npm run build`                           | Build de produção em `dist/` |
