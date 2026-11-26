"""Add the Nexotiva ticket mapping without modifying existing requests."""
from alembic import op
import sqlalchemy as sa

revision = "0004_nexotiva_tickets"
down_revision = "0003_add_user_theme_preference"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("nexotiva_tickets",
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("requests.id"), primary_key=True),
        sa.Column("company_id", sa.String(36), nullable=False),
        sa.Column("company_name", sa.String(150), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("user_name", sa.String(150), nullable=False),
        sa.Column("user_email", sa.String(254), nullable=False),
        sa.Column("module_slug", sa.String(100), nullable=False),
        sa.Column("module_name", sa.String(120), nullable=False),
        sa.Column("client_request_id", sa.String(36), nullable=False),
        sa.UniqueConstraint("company_id", "user_id", "client_request_id", name="uq_nexotiva_ticket_request"),
    )
    op.create_index("ix_nexotiva_ticket_scope", "nexotiva_tickets", ["company_id", "user_id"])

def downgrade():
    op.drop_index("ix_nexotiva_ticket_scope", table_name="nexotiva_tickets")
    op.drop_table("nexotiva_tickets")
