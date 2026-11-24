"""ajustar perfis do usuario (RF-BE-002, V3)

O perfil USUARIO deixa de existir: vira OPERADOR_COMERCIAL (RN-07). Os perfis validos
passam a ser ADMIN, OPERADOR_COMERCIAL e OPERADOR_FINANCEIRO. A ordem importa: o CHECK
antigo e removido antes do UPDATE e o novo so e criado depois (senao o UPDATE violaria um
dos dois).

Revision ID: 0003
Revises: 0002
"""

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("ck_usuario_perfil", "usuario", type_="check")
    op.execute("UPDATE usuario SET perfil = 'OPERADOR_COMERCIAL' WHERE perfil = 'USUARIO'")
    op.create_check_constraint(
        "ck_usuario_perfil",
        "usuario",
        "perfil IN ('ADMIN', 'OPERADOR_COMERCIAL', 'OPERADOR_FINANCEIRO')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_usuario_perfil", "usuario", type_="check")
    # Perda de informacao inevitavel: os dois perfis de operador voltam a ser USUARIO.
    op.execute(
        "UPDATE usuario SET perfil = 'USUARIO' "
        "WHERE perfil IN ('OPERADOR_COMERCIAL', 'OPERADOR_FINANCEIRO')"
    )
    op.create_check_constraint("ck_usuario_perfil", "usuario", "perfil IN ('ADMIN', 'USUARIO')")
