"""criar tabela usuario (RF-BE-001, V1)

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "usuario",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("email", sa.String(160), nullable=False),
        sa.Column("senha_hash", sa.String(100), nullable=False),
        sa.Column("perfil", sa.String(20), nullable=False),
        sa.Column("ativo", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("tentativas_falhas", sa.Integer(), server_default="0", nullable=False),
        sa.Column("bloqueado_ate", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ultimo_login_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("versao", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_usuario"),
        sa.UniqueConstraint("email", name="uk_usuario_email"),
        sa.CheckConstraint("perfil IN ('ADMIN', 'USUARIO')", name="ck_usuario_perfil"),
    )


def downgrade() -> None:
    op.drop_table("usuario")
