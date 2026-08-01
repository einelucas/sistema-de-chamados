"""Migration inicial: cria as tabelas de usuarios, solicitacoes, comentarios, historico e anexos.

Os tipos ENUM nativos do PostgreSQL sao criados automaticamente pelo SQLAlchemy junto com a
primeira coluna que os utiliza (nao devem ser criados explicitamente aqui: isso causaria um
erro "type already exists" / DuplicateObject em um banco limpo). Ja a remocao nao e automatica
via op.drop_table, entao o downgrade() remove os tipos explicitamente apos remover as tabelas.

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-01 00:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_role = sa.Enum("ADMIN", "ANALYST", "USER", name="user_role")
request_category = sa.Enum(
    "TI", "MANUTENCAO", "RH", "COMPRAS", "ADMINISTRATIVO", "OUTROS", name="request_category"
)
request_priority = sa.Enum("BAIXA", "MEDIA", "ALTA", "CRITICA", name="request_priority")
request_status = sa.Enum(
    "ABERTA", "EM_ANDAMENTO", "AGUARDANDO", "CONCLUIDA", "CANCELADA", name="request_status"
)
history_action = sa.Enum(
    "CRIACAO", "ALTERACAO_STATUS", "ALTERACAO_PRIORIDADE", "MUDANCA_RESPONSAVEL",
    "EDICAO_DADOS", "CONCLUSAO", "CANCELAMENTO", "COMENTARIO_ADICIONADO", "ANEXO_ADICIONADO",
    name="history_action",
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("email", sa.String(200), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="USER"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", request_category, nullable=False),
        sa.Column("priority", request_priority, nullable=False, server_default="MEDIA"),
        sa.Column("status", request_status, nullable=False, server_default="ABERTA"),
        sa.Column("requester_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("assignee_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_requests_requester_id", "requests", ["requester_id"])
    op.create_index("ix_requests_assignee_id", "requests", ["assignee_id"])
    op.create_index("ix_requests_status_priority", "requests", ["status", "priority"])

    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("requests.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_comments_author_id", "comments", ["author_id"])
    op.create_index("ix_comments_request_id", "comments", ["request_id"])

    op.create_table(
        "request_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("requests.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action", history_action, nullable=False),
        sa.Column("previous_value", sa.String(500), nullable=True),
        sa.Column("new_value", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_request_history_request_id", "request_history", ["request_id"])

    op.create_table(
        "attachments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("requests.id"), nullable=False),
        sa.Column("uploaded_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("stored_filename", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(150), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("stored_filename", name="uq_attachments_stored_filename"),
    )
    op.create_index("ix_attachments_request_id", "attachments", ["request_id"])


def downgrade() -> None:
    # Ao contrario do SQLAlchemy Core puro (Table.drop()), o op.drop_table do Alembic NAO
    # remove automaticamente os tipos ENUM nativos do PostgreSQL associados as colunas.
    # Sem esta remocao explicita, um downgrade seguido de upgrade falharia com
    # "type ... already exists", pois o tipo ficaria orfao no banco.
    op.drop_table("attachments")
    op.drop_table("request_history")
    op.drop_table("comments")
    op.drop_table("requests")
    op.drop_table("users")

    bind = op.get_bind()
    history_action.drop(bind, checkfirst=True)
    request_status.drop(bind, checkfirst=True)
    request_priority.drop(bind, checkfirst=True)
    request_category.drop(bind, checkfirst=True)
    user_role.drop(bind, checkfirst=True)
