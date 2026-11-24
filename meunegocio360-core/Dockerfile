# Build multi-stage (RNF-100). Contexto: pasta meunegocio360-core.
FROM python:3.12-slim AS build
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY alembic.ini ./
COPY migrations migrations
COPY src src
RUN uv sync --frozen --no-dev

FROM python:3.12-slim
WORKDIR /app
COPY --from=build /app /app
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
USER 1001
CMD ["sh", "-c", "alembic upgrade head && uvicorn meunegocio360_core.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
