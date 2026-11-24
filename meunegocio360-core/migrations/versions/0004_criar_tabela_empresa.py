"""criar tabela empresa (RF-BE-002, V4)

A tabela `empresa` e a unica sem `empresa_id`. "No maximo uma empresa ativa" e garantido
pelo banco com um indice unico PARCIAL (no MySQL era uma coluna gerada; ver ADR 0002).

Revision ID: 0004
Revises: 0003
"""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "empresa",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("razao_social", sa.String(150), nullable=False),
        sa.Column("nome_fantasia", sa.String(150), nullable=True),
        sa.Column("cnpj", sa.CHAR(14), nullable=False),
        sa.Column("email", sa.String(160), nullable=True),
        sa.Column("telefone", sa.String(11), nullable=True),
        sa.Column(
            "fuso_horario", sa.String(50), server_default="America/Sao_Paulo", nullable=False
        ),
        sa.Column("moeda", sa.CHAR(3), server_default="BRL", nullable=False),
        sa.Column("ativa", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("versao", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_empresa"),
        sa.UniqueConstraint("cnpj", name="uk_empresa_cnpj"),
        sa.CheckConstraint("cnpj ~ '^[0-9]{14}$'", name="ck_empresa_cnpj_formato"),
    )
    op.create_index(
        "uk_empresa_ativa_unica",
        "empresa",
        [sa.text("(true)")],
        unique=True,
        postgresql_where=sa.text("ativa"),
    )


def downgrade() -> None:
    op.drop_index("uk_empresa_ativa_unica", table_name="empresa")
    op.drop_table("empresa")
