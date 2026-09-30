"""add institutions multi-tenant

Revision ID: a0b1c2d3e4f5
Revises: c6d7e8f9a0b1
Create Date: 2026-09-30 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "a0b1c2d3e4f5"
down_revision = "c6d7e8f9a0b1"
branch_labels = None
depends_on = None


TENANT_TABLES = [
    "organizations",
    "courses",
    "learning_paths",
    "locations",
    "class_offerings",
    "billing_plans",
    "documents",
    "notification_templates",
    "certificates",
]

institution_type = sa.Enum("school", "university", "vocational", "corporate", "mixed", name="institutiontype")
institution_status = sa.Enum("active", "suspended", "archived", name="institutionstatus")
user_role = postgresql.ENUM(name="userrole", create_type=False)


def upgrade() -> None:
    with op.get_context().autocommit_block():
        for role in ("super_admin", "institution_admin", "secretary", "guardian"):
            op.execute(f"ALTER TYPE userrole ADD VALUE IF NOT EXISTS '{role}'")

    op.create_table(
        "institutions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("legal_name", sa.String(length=200), nullable=True),
        sa.Column("document", sa.String(length=50), nullable=True),
        sa.Column("type", institution_type, nullable=False, server_default="mixed"),
        sa.Column("status", institution_status, nullable=False, server_default="active"),
        sa.Column("settings", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("branding", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_institutions_slug"), "institutions", ["slug"], unique=True)
    op.create_index(op.f("ix_institutions_document"), "institutions", ["document"], unique=False)

    op.create_table(
        "institution_memberships",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("institution_id", "user_id"),
    )
    op.create_index(op.f("ix_institution_memberships_institution_id"), "institution_memberships", ["institution_id"], unique=False)
    op.create_index(op.f("ix_institution_memberships_user_id"), "institution_memberships", ["user_id"], unique=False)

    op.create_table(
        "campuses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("institution_id", sa.Integer(), sa.ForeignKey("institutions.id"), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(op.f("ix_campuses_institution_id"), "campuses", ["institution_id"], unique=False)

    op.execute(
        "INSERT INTO institutions (slug, name, type, status) "
        "VALUES ('default', 'Instituicao Padrao', 'mixed', 'active')"
    )

    for table in TENANT_TABLES:
        op.add_column(table, sa.Column("institution_id", sa.Integer(), nullable=True))
        op.execute(f"UPDATE {table} SET institution_id = (SELECT id FROM institutions WHERE slug = 'default')")
        op.alter_column(table, "institution_id", nullable=False)
        op.create_foreign_key(f"fk_{table}_institution_id", table, "institutions", ["institution_id"], ["id"])
        op.create_index(op.f(f"ix_{table}_institution_id"), table, ["institution_id"], unique=False)

    op.add_column("locations", sa.Column("campus_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_locations_campus_id", "locations", "campuses", ["campus_id"], ["id"])
    op.create_index(op.f("ix_locations_campus_id"), "locations", ["campus_id"], unique=False)

    # Unicidade passa a valer dentro de cada instituicao.
    op.drop_index("ix_organizations_name", table_name="organizations")
    op.create_index(op.f("ix_organizations_name"), "organizations", ["name"], unique=False)
    op.create_unique_constraint("uq_organizations_institution_id_name", "organizations", ["institution_id", "name"])
    op.drop_constraint("billing_plans_name_key", "billing_plans", type_="unique")
    op.create_unique_constraint("uq_billing_plans_institution_id_name", "billing_plans", ["institution_id", "name"])
    op.drop_constraint("notification_templates_key_channel_key", "notification_templates", type_="unique")
    op.create_unique_constraint(
        "uq_notification_templates_institution_id_key_channel",
        "notification_templates",
        ["institution_id", "key", "channel"],
    )

    op.execute(
        "INSERT INTO institution_memberships (institution_id, user_id, role, is_active) "
        "SELECT (SELECT id FROM institutions WHERE slug = 'default'), id, role, is_active FROM users"
    )


def downgrade() -> None:
    op.drop_constraint("uq_notification_templates_institution_id_key_channel", "notification_templates", type_="unique")
    op.create_unique_constraint("notification_templates_key_channel_key", "notification_templates", ["key", "channel"])
    op.drop_constraint("uq_billing_plans_institution_id_name", "billing_plans", type_="unique")
    op.create_unique_constraint("billing_plans_name_key", "billing_plans", ["name"])
    op.drop_constraint("uq_organizations_institution_id_name", "organizations", type_="unique")
    op.drop_index(op.f("ix_organizations_name"), table_name="organizations")
    op.create_index("ix_organizations_name", "organizations", ["name"], unique=True)

    op.drop_index(op.f("ix_locations_campus_id"), table_name="locations")
    op.drop_constraint("fk_locations_campus_id", "locations", type_="foreignkey")
    op.drop_column("locations", "campus_id")

    for table in reversed(TENANT_TABLES):
        op.drop_index(op.f(f"ix_{table}_institution_id"), table_name=table)
        op.drop_constraint(f"fk_{table}_institution_id", table, type_="foreignkey")
        op.drop_column(table, "institution_id")

    op.drop_index(op.f("ix_campuses_institution_id"), table_name="campuses")
    op.drop_table("campuses")
    op.drop_index(op.f("ix_institution_memberships_user_id"), table_name="institution_memberships")
    op.drop_index(op.f("ix_institution_memberships_institution_id"), table_name="institution_memberships")
    op.drop_table("institution_memberships")
    op.drop_index(op.f("ix_institutions_document"), table_name="institutions")
    op.drop_index(op.f("ix_institutions_slug"), table_name="institutions")
    op.drop_table("institutions")
    institution_status.drop(op.get_bind(), checkfirst=True)
    institution_type.drop(op.get_bind(), checkfirst=True)
    # Valores adicionados ao enum userrole nao sao removidos (PostgreSQL nao suporta DROP VALUE).
