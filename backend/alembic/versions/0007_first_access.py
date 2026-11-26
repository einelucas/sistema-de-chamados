from alembic import op
import sqlalchemy as sa
revision="0007_first_access"
down_revision="0006_support_sync"
branch_labels=None
depends_on=None
def upgrade():
    op.add_column("users",sa.Column("must_change_password",sa.Boolean(),server_default=sa.false(),nullable=False))
    op.add_column("users",sa.Column("session_version",sa.Integer(),server_default=sa.text("1"),nullable=False))
def downgrade():
    op.drop_column("users","session_version")
    op.drop_column("users","must_change_password")
