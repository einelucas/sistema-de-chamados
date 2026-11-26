from alembic import op
import sqlalchemy as sa
revision="0006_support_sync"
down_revision="0005_support_hardening"
branch_labels=None
depends_on=None
def upgrade():
    op.create_table("support_revisions",sa.Column("scope",sa.String(64),primary_key=True),sa.Column("revision",sa.String(36),nullable=False))
    op.create_table("support_outbox",sa.Column("id",sa.String(36),primary_key=True),sa.Column("company_id",sa.String(36),nullable=False),sa.Column("user_id",sa.String(36),nullable=False),sa.Column("ticket_id",sa.Integer(),nullable=False),sa.Column("kind",sa.String(30),nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),nullable=False),sa.Column("lease_until",sa.DateTime(timezone=True),nullable=True),sa.Column("delivered_at",sa.DateTime(timezone=True),nullable=True))
    op.create_index("ix_support_outbox_pending","support_outbox",["delivered_at","lease_until","created_at"])
def downgrade():
    op.drop_index("ix_support_outbox_pending",table_name="support_outbox")
    op.drop_table("support_outbox")
    op.drop_table("support_revisions")
