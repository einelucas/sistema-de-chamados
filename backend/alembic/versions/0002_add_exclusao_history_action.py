"""Adiciona o valor EXCLUSAO ao enum history_action.

Corretiva: o modelo HistoryAction ganhou um novo valor (EXCLUSAO) para que a exclusao
(logica) de uma solicitacao passe a ser registrada no historico de auditoria, assim como
as demais acoes relevantes (criacao, mudanca de status, conclusao, cancelamento etc.).

No PostgreSQL 12+, ALTER TYPE ... ADD VALUE pode ser executado dentro de uma transacao,
desde que o novo valor nao seja utilizado na mesma transacao em que foi adicionado -- o que
e o caso aqui, pois esta migration apenas adiciona o valor ao catalogo do banco.

Revision ID: 0002_add_exclusao_history_action
Revises: 0001_initial
Create Date: 2026-07-31 00:00:00

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0002_add_exclusao_history_action"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE history_action ADD VALUE IF NOT EXISTS 'EXCLUSAO'")


def downgrade() -> None:
    # PostgreSQL nao permite remover um valor de um tipo ENUM diretamente (DROP VALUE nao
    # existe). Para reverter de forma segura, seria necessario recriar o tipo sem o valor e
    # migrar a coluna, o que exige garantir que nenhuma linha use 'EXCLUSAO'. Como esta e uma
    # migration aditiva e nao-destrutiva, o downgrade documenta a limitacao em vez de arriscar
    # perda de dados silenciosa.
    raise NotImplementedError(
        "Downgrade nao suportado: PostgreSQL nao permite remover valores de um tipo ENUM "
        "sem recriar o tipo. Se for necessario reverter, trate manualmente garantindo que "
        "nenhum registro em request_history utiliza o valor 'EXCLUSAO'."
    )
