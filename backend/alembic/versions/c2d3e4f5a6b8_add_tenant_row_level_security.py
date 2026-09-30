"""add tenant row level security

Revision ID: c2d3e4f5a6b8
Revises: b1c2d3e4f5a6
Create Date: 2026-09-30 00:00:02.000000

Politica `tenant_isolation` em toda tabela com `institution_id` (exceto os
vinculos usuario-instituicao, consultados antes de a instituicao ser escolhida).
Mantida em sincronia com app/core/tenant_rls.py.
"""

from alembic import op
import sqlalchemy as sa


revision = "c2d3e4f5a6b8"
down_revision = "b1c2d3e4f5a6"
branch_labels = None
depends_on = None

POLICY = "tenant_isolation"
CURRENT = "nullif(current_setting('app.institution_id', true), '')"
CONDITION = f"{CURRENT} IS NULL OR institution_id = {CURRENT}::int"
EXCLUDED = {"institution_memberships"}


def _tenant_tables() -> list[str]:
    rows = op.get_bind().execute(sa.text(
        "SELECT table_name FROM information_schema.columns "
        "WHERE table_schema = current_schema() AND column_name = 'institution_id' ORDER BY table_name"
    ))
    return [row[0] for row in rows if row[0] not in EXCLUDED]


def upgrade() -> None:
    for table in _tenant_tables():
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(f"DROP POLICY IF EXISTS {POLICY} ON {table}")
        op.execute(f"CREATE POLICY {POLICY} ON {table} USING ({CONDITION}) WITH CHECK ({CONDITION})")


def downgrade() -> None:
    for table in _tenant_tables():
        op.execute(f"DROP POLICY IF EXISTS {POLICY} ON {table}")
        op.execute(f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
