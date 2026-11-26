"""Protect integration identities, public replies and persistent attachment contents."""
from alembic import op
import sqlalchemy as sa
revision = "0005_support_hardening"
down_revision = "0004_nexotiva_tickets"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("users", sa.Column("integration_identity", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.execute("UPDATE users SET integration_identity = true, is_active = false WHERE id IN (SELECT requests.requester_id FROM requests JOIN nexotiva_tickets ON nexotiva_tickets.request_id = requests.id)")
    op.add_column("comments", sa.Column("public_reply", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("comments", sa.Column("client_request_id", sa.String(36), nullable=True))
    op.create_unique_constraint("uq_comment_client_request", "comments", ["request_id", "client_request_id"])
    op.add_column("attachments", sa.Column("file_content", sa.LargeBinary(), nullable=True))
    op.add_column("attachments", sa.Column("shared_with_customer", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("attachments", sa.Column("client_request_id", sa.String(36), nullable=True))
    op.create_unique_constraint("uq_attachment_client_request","attachments",["request_id","client_request_id"])
    op.add_column("nexotiva_tickets",sa.Column("payload_hash",sa.String(64),nullable=True))
    op.add_column("requests", sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")))
    op.create_index("ix_nexotiva_ticket_company_module", "nexotiva_tickets", ["company_id", "module_slug"])

def downgrade():
    op.drop_index("ix_nexotiva_ticket_company_module", table_name="nexotiva_tickets")
    op.drop_column("requests","version")
    op.drop_column("nexotiva_tickets","payload_hash")
    op.drop_constraint("uq_attachment_client_request","attachments",type_="unique")
    op.drop_column("attachments","client_request_id")
    op.drop_column("attachments","shared_with_customer")
    op.drop_column("attachments","file_content")
    op.drop_constraint("uq_comment_client_request","comments",type_="unique")
    op.drop_column("comments","client_request_id")
    op.drop_column("comments","public_reply")
    op.drop_column("users","integration_identity")
