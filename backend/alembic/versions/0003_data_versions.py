"""data versions for the mobile cache

Revision ID: 0003_data_versions
Revises: 0002_public_pages
Create Date: 2026-10-01 18:00:00.000000

Versao dos dados de cada area (avisos, agenda, boletim, dependentes) por instituicao: o app guarda
as telas em disco e so as baixa de novo quando a versao muda. Tabela de instituicao, com RLS.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0003_data_versions'
down_revision: Union[str, Sequence[str], None] = '0002_public_pages'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

POLICY = "tenant_isolation"
CURRENT = "nullif(current_setting('app.institution_id', true), '')"
CONDITION = f"{CURRENT} IS NULL OR institution_id = {CURRENT}::uuid"


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('data_versions',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('area', sa.String(length=40), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('institution_id', 'area')
    )
    op.create_index(op.f('ix_data_versions_institution_id'), 'data_versions', ['institution_id'], unique=False)
    if op.get_bind().dialect.name == 'postgresql':
        op.execute("ALTER TABLE data_versions ENABLE ROW LEVEL SECURITY")
        op.execute("ALTER TABLE data_versions FORCE ROW LEVEL SECURITY")
        op.execute(f"CREATE POLICY {POLICY} ON data_versions USING ({CONDITION}) WITH CHECK ({CONDITION})")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_data_versions_institution_id'), table_name='data_versions')
    op.drop_table('data_versions')
