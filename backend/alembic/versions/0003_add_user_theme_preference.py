"""Adiciona preferencia de tema visual ao usuario.

Revision ID: 0003_add_user_theme_preference
Revises: 0002_add_exclusao_history_action
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0003_add_user_theme_preference"
down_revision: str | None = "0002_add_exclusao_history_action"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "theme_preference",
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'light'"),
        ),
    )
    op.create_check_constraint(
        "ck_users_theme_preference",
        "users",
        "theme_preference IN ('light', 'dark')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_users_theme_preference", "users", type_="check")
    op.drop_column("users", "theme_preference")
