"""add notification read_at

Revision ID: f1a2b3c4d5e1
Revises: e0f1a2b3c4d0
Create Date: 2026-10-01 09:00:00.000000

Pendencias da Fase 15: caixa de avisos de cada usuario (inclusive do
responsavel), com marcacao de leitura.

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e1'
down_revision: Union[str, Sequence[str], None] = 'e0f1a2b3c4d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('notification_events', sa.Column('read_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('notification_events', 'read_at')
