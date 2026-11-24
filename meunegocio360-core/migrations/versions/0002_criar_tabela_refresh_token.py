"""criar tabela refresh_token (RF-BE-001, V2)

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "refresh_token",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("familia_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.CHAR(64), nullable=False),
        sa.Column("expira_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revogado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_refresh_token"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuario.id"], name="fk_refresh_token_usuario"),
        sa.UniqueConstraint("token_hash", name="uk_refresh_token_hash"),
    )
    op.create_index("ix_refresh_token_usuario_id", "refresh_token", ["usuario_id"])
    op.create_index("ix_refresh_token_familia_id", "refresh_token", ["familia_id"])


def downgrade() -> None:
    op.drop_index("ix_refresh_token_familia_id", table_name="refresh_token")
    op.drop_index("ix_refresh_token_usuario_id", table_name="refresh_token")
    op.drop_table("refresh_token")
