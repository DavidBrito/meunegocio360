"""criar tabela cliente e apoio a busca sem acento/caixa (RF-BE-003, V5)

Resultado da checagem do ADR 0002 (ver ADR 0006), PostgreSQL 16:
- collation ICU nao determinista `ci_ai`: serve para IGUALDADE e ORDENACAO sem acento/caixa,
  mas NAO suporta LIKE/ILIKE/strpos;
- por isso a busca "contem" usa `lower(f_unaccent(nome)) COLLATE "default" LIKE ...`;
- `unaccent` e STABLE; `f_unaccent` e o *wrapper* IMMUTABLE (reaproveitado por RF-BE-004/005).

Revision ID: 0005
Revises: 0004
"""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
    op.execute(
        "CREATE COLLATION ci_ai (provider = icu, locale = 'und-u-ks-level1', deterministic = false)"
    )
    op.execute(
        "CREATE FUNCTION f_unaccent(text) RETURNS text LANGUAGE sql IMMUTABLE PARALLEL SAFE STRICT "
        "AS $$ SELECT public.unaccent('public.unaccent', $1) $$"
    )
    op.create_table(
        "cliente",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("tipo_pessoa", sa.String(10), nullable=False),
        sa.Column("nome", sa.String(150, collation="ci_ai"), nullable=False),
        sa.Column("documento", sa.String(14), nullable=False),
        sa.Column("email", sa.String(160), nullable=True),
        sa.Column("telefone", sa.String(11), nullable=True),
        sa.Column("ativo", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("versao", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_cliente"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresa.id"], name="fk_cliente_empresa"),
        sa.UniqueConstraint("empresa_id", "documento", name="uk_cliente_empresa_documento"),
        sa.CheckConstraint("tipo_pessoa IN ('FISICA', 'JURIDICA')", name="ck_cliente_tipo_pessoa"),
        sa.CheckConstraint(
            "(tipo_pessoa = 'FISICA' AND documento ~ '^[0-9]{11}$') "
            "OR (tipo_pessoa = 'JURIDICA' AND documento ~ '^[0-9]{14}$')",
            name="ck_cliente_documento",
        ),
    )
    op.create_index("idx_cliente_empresa_nome", "cliente", ["empresa_id", "nome"])
    op.create_index("idx_cliente_empresa_ativo", "cliente", ["empresa_id", "ativo"])


def downgrade() -> None:
    op.drop_index("idx_cliente_empresa_ativo", table_name="cliente")
    op.drop_index("idx_cliente_empresa_nome", table_name="cliente")
    op.drop_table("cliente")
    op.execute("DROP FUNCTION f_unaccent(text)")
    op.execute("DROP COLLATION ci_ai")
    op.execute("DROP EXTENSION IF EXISTS unaccent")
