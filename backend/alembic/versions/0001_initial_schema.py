"""initial schema with uuid ids

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-01 12:03:12.615182

Esquema completo com ids UUID (versao 7, gerados pela aplicacao em app/core/ids.py).
Substitui as migrations anteriores, de ids inteiros; o banco foi recriado na homologacao.

Inclui os papeis por vinculo (`institution_member_roles`: a pessoa pode ser aluno e professor na mesma
instituicao). Alem das tabelas: instituicao padrao, tabela local do salario minimo (serie 1619 do SGS
do Banco Central, desde 2000) e a politica `tenant_isolation` (RLS) nas tabelas de dados da
instituicao (models com TenantMixin; ficam de fora os vinculos usuario-instituicao e as tabelas
da plataforma, como assinatura e faturas SaaS). Mantida em sincronia com app/core/tenant_rls.py.
"""
from typing import Sequence, Union
from datetime import date, datetime, timezone
import os
import time
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_initial'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

POLICY = "tenant_isolation"
CURRENT = "nullif(current_setting('app.institution_id', true), '')"
CONDITION = f"{CURRENT} IS NULL OR institution_id = {CURRENT}::uuid"
TENANT_TABLES = [
    'academic_declarations', 'academic_terms', 'academic_units', 'access_role_assignments', 'access_roles',
    'admission_applications', 'admission_calls', 'agenda_items', 'application_documents', 'assessment_items',
    'assignment_submissions', 'attendance', 'attendance_records', 'benefit_deliveries', 'benefit_items',
    'benefit_stock_entries', 'billing_plans', 'calendar_events', 'campuses', 'certificates', 'charges',
    'chat_conversations', 'chat_messages', 'checkin_tokens', 'class_diary_entries', 'class_enrollments',
    'class_group_members', 'class_groups', 'class_offerings', 'complementary_activities', 'contract_templates',
    'course_completion_rules', 'course_modules', 'course_prerequisites', 'courses', 'credit_transfers', 'curricula',
    'curriculum_components', 'diary_attendance', 'document_versions', 'documents', 'enrollment_contracts',
    'enrollments', 'final_projects', 'forum_posts', 'forum_threads', 'funding_sources', 'grade_entries',
    'grading_periods', 'grading_schemes', 'internship_logs', 'internships',
    'learning_path_courses', 'learning_paths', 'lessons', 'locations', 'material_request_lines',
    'material_requests', 'notification_events', 'notification_templates', 'offering_period_closures',
    'offering_time_slots', 'organizations', 'period_results', 'practical_assessment_records',
    'program_enrollment_events', 'program_enrollments', 'programs', 'progress', 'quiz_attempts', 'quiz_questions',
    'quizzes', 'registration_windows', 'rooms', 'scheduled_meetings', 'sessions', 'student_discounts',
    'student_guardians', 'student_occurrences', 'subject_equivalences', 'subject_prerequisites', 'subjects',
    'subscriptions', 'term_registrations', 'tuition_plans', 'waitlist_entries', 'warehouse_entries',
    'warehouse_items',
]
ENUM_TYPES = [
    'academicunitkind', 'activitycategory', 'admissioncallstatus', 'agendaitemkind', 'applicationstatus',
    'assessmentkind', 'assignmentsubmissionstatus', 'attendancemethod', 'attendancestatus', 'averageformula',
    'benefitkind', 'billingperiod', 'calendareventkind', 'chargestatus', 'classenrollmentresult',
    'classenrollmentstatus', 'classstatus', 'componentkind', 'contractkind', 'contractstatus', 'coursemodality',
    'credittransferorigin', 'credittransferstatus', 'curriculumstatus', 'declarationkind', 'discountkind',
    'documentreview', 'documentstatus', 'documenttype', 'enrollmenteventkind', 'entryorigin', 'finalprojectstatus',
    'fundingkind', 'gradingperiodstatus', 'gradingscale', 'guardianrelationship', 'institutionstatus',
    'institutiontype', 'internshipstatus', 'lessontype', 'materialkind', 'meetingtype', 'notificationchannel',
    'notificationeventtype', 'notificationstatus', 'occurrencekind', 'occurrenceseverity', 'paymentmethod',
    'platforminvoicestatus', 'practicalassessmentstatus', 'programenrollmentstatus', 'programlevel',
    'programstatus', 'progressstatus', 'requeststatus', 'reviewstatus', 'saassubscriptionstatus', 'schooling',
    'seatkind', 'selectionmethod', 'shift', 'stockorigin', 'subscriptionstatus', 'termkind', 'termstatus',
    'tuitionbasis', 'userrole',
]

# Mudancas de valor da serie 1619 do SGS (consultadas em 2026-10-01); maio/1999 cobre o inicio de 2000.
KNOWN_VALUES = [
    (date(1999, 5, 1), 13600),
    (date(2000, 4, 1), 15100),
    (date(2001, 4, 1), 18000),
    (date(2002, 4, 1), 20000),
    (date(2003, 4, 1), 24000),
    (date(2004, 5, 1), 26000),
    (date(2005, 5, 1), 30000),
    (date(2006, 4, 1), 35000),
    (date(2007, 4, 1), 38000),
    (date(2008, 3, 1), 41500),
    (date(2009, 2, 1), 46500),
    (date(2010, 1, 1), 51000),
    (date(2011, 1, 1), 54000),
    (date(2011, 3, 1), 54500),
    (date(2012, 1, 1), 62200),
    (date(2013, 1, 1), 67800),
    (date(2014, 1, 1), 72400),
    (date(2015, 1, 1), 78800),
    (date(2016, 1, 1), 88000),
    (date(2017, 1, 1), 93700),
    (date(2018, 1, 1), 95400),
    (date(2019, 1, 1), 99800),
    (date(2020, 1, 1), 103900),
    (date(2020, 2, 1), 104500),
    (date(2021, 1, 1), 110000),
    (date(2022, 1, 1), 121200),
    (date(2023, 1, 1), 130200),
    (date(2023, 5, 1), 132000),
    (date(2024, 1, 1), 141200),
    (date(2025, 1, 1), 151800),
    (date(2026, 1, 1), 162100),
]


def _uuid7() -> uuid.UUID:
    """Mesmo formato de app/core/ids.py, sem importar a aplicacao na migration."""
    millis = time.time_ns() // 1_000_000 & ((1 << 48) - 1)
    rand = int.from_bytes(os.urandom(10), "big")
    value = millis << 80 | 0x7 << 76 | ((rand >> 62) & 0xFFF) << 64 | 0b10 << 62 | (rand & ((1 << 62) - 1))
    return uuid.UUID(int=value)


def _is_postgres() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def _seed(institutions: sa.Table, minimum_wages: sa.Table) -> None:
    synced_at = datetime(2026, 10, 1, tzinfo=timezone.utc)
    op.bulk_insert(institutions, [{
        "id": _uuid7(), "slug": "default", "name": "Instituicao Padrao", "type": "mixed", "status": "active",
        "settings": {}, "branding": {}, "created_at": synced_at,
    }])
    op.bulk_insert(minimum_wages, [
        {"id": _uuid7(), "valid_from": valid_from, "cents": cents, "source": "seed", "synced_at": synced_at}
        for valid_from, cents in KNOWN_VALUES
    ])


def _enable_row_level_security() -> None:
    for table in TENANT_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(f"CREATE POLICY {POLICY} ON {table} USING ({CONDITION}) WITH CHECK ({CONDITION})")


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    institutions = op.create_table('institutions',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('slug', sa.String(length=80), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('legal_name', sa.String(length=200), nullable=True),
    sa.Column('document', sa.String(length=50), nullable=True),
    sa.Column('type', sa.Enum('school', 'university', 'vocational', 'corporate', 'mixed', name='institutiontype'), nullable=False),
    sa.Column('status', sa.Enum('active', 'suspended', 'archived', name='institutionstatus'), nullable=False),
    sa.Column('settings', sa.JSON(), nullable=False),
    sa.Column('branding', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_institutions_document'), 'institutions', ['document'], unique=False)
    op.create_index(op.f('ix_institutions_slug'), 'institutions', ['slug'], unique=True)
    minimum_wages = op.create_table('minimum_wage_values',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('valid_from', sa.Date(), nullable=False),
    sa.Column('cents', sa.Integer(), nullable=False),
    sa.Column('source', sa.String(length=20), nullable=False),
    sa.Column('synced_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_minimum_wage_values_valid_from'), 'minimum_wage_values', ['valid_from'], unique=True)
    op.create_table('saas_plans',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('monthly_price_cents', sa.Integer(), nullable=False),
    sa.Column('max_students', sa.Integer(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('academic_terms',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('kind', sa.Enum('year', 'semester', 'quarter', 'module', name='termkind'), nullable=False),
    sa.Column('starts_on', sa.Date(), nullable=False),
    sa.Column('ends_on', sa.Date(), nullable=False),
    sa.Column('status', sa.Enum('planned', 'open', 'closed', name='termstatus'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('institution_id', 'name')
    )
    op.create_index(op.f('ix_academic_terms_institution_id'), 'academic_terms', ['institution_id'], unique=False)
    op.create_table('academic_units',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('parent_id', sa.Uuid(), nullable=True),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('kind', sa.Enum('segment', 'faculty', 'department', 'axis', 'other', name='academicunitkind'), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['parent_id'], ['academic_units.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_academic_units_institution_id'), 'academic_units', ['institution_id'], unique=False)
    op.create_index(op.f('ix_academic_units_parent_id'), 'academic_units', ['parent_id'], unique=False)
    op.create_table('access_roles',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('permissions', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('institution_id', 'name')
    )
    op.create_index(op.f('ix_access_roles_institution_id'), 'access_roles', ['institution_id'], unique=False)
    op.create_table('benefit_items',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('kind', sa.Enum('snack', 'material', 'uniform', 'transport', 'stipend', 'other', name='benefitkind'), nullable=False),
    sa.Column('unit', sa.String(length=40), nullable=False),
    sa.Column('unit_cost_cents', sa.Integer(), nullable=False),
    sa.Column('requires_attendance', sa.Boolean(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_benefit_items_institution_id'), 'benefit_items', ['institution_id'], unique=False)
    op.create_table('billing_plans',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('price_cents', sa.Integer(), nullable=False),
    sa.Column('currency', sa.String(length=10), nullable=False),
    sa.Column('billing_period', sa.Enum('one_time', 'monthly', 'quarterly', 'yearly', name='billingperiod'), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('institution_id', 'name')
    )
    op.create_index(op.f('ix_billing_plans_institution_id'), 'billing_plans', ['institution_id'], unique=False)
    op.create_index(op.f('ix_billing_plans_name'), 'billing_plans', ['name'], unique=False)
    op.create_table('campuses',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campuses_institution_id'), 'campuses', ['institution_id'], unique=False)
    op.create_table('contract_templates',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('kind', sa.Enum('enrollment', 'reenrollment', name='contractkind'), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contract_templates_institution_id'), 'contract_templates', ['institution_id'], unique=False)
    op.create_table('courses',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('modality', sa.Enum('online', 'in_person', 'hybrid', name='coursemodality'), nullable=False),
    sa.Column('agent_id', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_courses_institution_id'), 'courses', ['institution_id'], unique=False)
    op.create_table('funding_sources',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('kind', sa.Enum('agreement', 'government', 'system_s', 'parliamentary', 'donation', 'own', 'other', name='fundingkind'), nullable=False),
    sa.Column('agreement_number', sa.String(length=80), nullable=True),
    sa.Column('amount_cents', sa.Integer(), nullable=True),
    sa.Column('starts_on', sa.Date(), nullable=False),
    sa.Column('ends_on', sa.Date(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_funding_sources_institution_id'), 'funding_sources', ['institution_id'], unique=False)
    op.create_table('grading_schemes',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('scale', sa.Enum('numeric', 'concept', name='gradingscale'), nullable=False),
    sa.Column('min_value', sa.Float(), nullable=False),
    sa.Column('max_value', sa.Float(), nullable=False),
    sa.Column('passing_grade', sa.Float(), nullable=False),
    sa.Column('formula', sa.Enum('arithmetic', 'weighted', name='averageformula'), nullable=False),
    sa.Column('recovery_enabled', sa.Boolean(), nullable=False),
    sa.Column('min_attendance', sa.Float(), nullable=False),
    sa.Column('concepts', sa.JSON(), nullable=False),
    sa.Column('is_default', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('institution_id', 'name')
    )
    op.create_index(op.f('ix_grading_schemes_institution_id'), 'grading_schemes', ['institution_id'], unique=False)
    op.create_table('institution_subscriptions',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.Column('plan_id', sa.Uuid(), nullable=False),
    sa.Column('status', sa.Enum('trial', 'active', 'past_due', 'cancelled', name='saassubscriptionstatus'), nullable=False),
    sa.Column('started_on', sa.Date(), nullable=False),
    sa.Column('trial_ends_on', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['plan_id'], ['saas_plans.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_institution_subscriptions_institution_id'), 'institution_subscriptions', ['institution_id'], unique=True)
    op.create_index(op.f('ix_institution_subscriptions_plan_id'), 'institution_subscriptions', ['plan_id'], unique=False)
    op.create_table('learning_paths',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learning_paths_institution_id'), 'learning_paths', ['institution_id'], unique=False)
    op.create_table('notification_templates',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('key', sa.String(length=120), nullable=False),
    sa.Column('channel', sa.Enum('internal', 'whatsapp', 'email', 'push', name='notificationchannel'), nullable=False),
    sa.Column('title_template', sa.String(length=200), nullable=False),
    sa.Column('body_template', sa.Text(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('institution_id', 'key', 'channel')
    )
    op.create_index(op.f('ix_notification_templates_institution_id'), 'notification_templates', ['institution_id'], unique=False)
    op.create_index(op.f('ix_notification_templates_key'), 'notification_templates', ['key'], unique=False)
    op.create_table('organizations',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('legal_name', sa.String(length=200), nullable=True),
    sa.Column('document', sa.String(length=50), nullable=True),
    sa.Column('contact_email', sa.String(length=200), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('institution_id', 'name')
    )
    op.create_index(op.f('ix_organizations_document'), 'organizations', ['document'], unique=False)
    op.create_index(op.f('ix_organizations_institution_id'), 'organizations', ['institution_id'], unique=False)
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=False)
    op.create_table('warehouse_items',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('category', sa.String(length=80), nullable=True),
    sa.Column('kind', sa.Enum('consumable', 'durable', name='materialkind'), nullable=False),
    sa.Column('unit', sa.String(length=40), nullable=False),
    sa.Column('min_stock', sa.Integer(), nullable=False),
    sa.Column('location', sa.String(length=120), nullable=True),
    sa.Column('unit_cost_cents', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_warehouse_items_institution_id'), 'warehouse_items', ['institution_id'], unique=False)
    op.create_table('calendar_events',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('term_id', sa.Uuid(), nullable=True),
    sa.Column('kind', sa.Enum('school_day', 'holiday', 'recess', 'exam', 'event', name='calendareventkind'), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('starts_on', sa.Date(), nullable=False),
    sa.Column('ends_on', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['term_id'], ['academic_terms.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_calendar_events_institution_id'), 'calendar_events', ['institution_id'], unique=False)
    op.create_index(op.f('ix_calendar_events_starts_on'), 'calendar_events', ['starts_on'], unique=False)
    op.create_index(op.f('ix_calendar_events_term_id'), 'calendar_events', ['term_id'], unique=False)
    op.create_table('course_completion_rules',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('course_id', sa.Uuid(), nullable=False),
    sa.Column('require_lessons_complete', sa.Boolean(), nullable=False),
    sa.Column('minimum_progress_percent', sa.Integer(), nullable=False),
    sa.Column('require_quiz', sa.Boolean(), nullable=False),
    sa.Column('minimum_quiz_score', sa.Integer(), nullable=False),
    sa.Column('require_attendance', sa.Boolean(), nullable=False),
    sa.Column('minimum_attendance_percent', sa.Integer(), nullable=False),
    sa.Column('auto_issue', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('course_id')
    )
    op.create_index(op.f('ix_course_completion_rules_course_id'), 'course_completion_rules', ['course_id'], unique=False)
    op.create_index(op.f('ix_course_completion_rules_institution_id'), 'course_completion_rules', ['institution_id'], unique=False)
    op.create_table('course_modules',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('course_id', sa.Uuid(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_course_modules_course_id'), 'course_modules', ['course_id'], unique=False)
    op.create_index(op.f('ix_course_modules_institution_id'), 'course_modules', ['institution_id'], unique=False)
    op.create_table('course_prerequisites',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('course_id', sa.Uuid(), nullable=False),
    sa.Column('prerequisite_course_id', sa.Uuid(), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['prerequisite_course_id'], ['courses.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('course_id', 'prerequisite_course_id')
    )
    op.create_index(op.f('ix_course_prerequisites_course_id'), 'course_prerequisites', ['course_id'], unique=False)
    op.create_index(op.f('ix_course_prerequisites_institution_id'), 'course_prerequisites', ['institution_id'], unique=False)
    op.create_index(op.f('ix_course_prerequisites_prerequisite_course_id'), 'course_prerequisites', ['prerequisite_course_id'], unique=False)
    op.create_table('grading_periods',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('term_id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.Column('starts_on', sa.Date(), nullable=False),
    sa.Column('ends_on', sa.Date(), nullable=False),
    sa.Column('weight', sa.Float(), nullable=False),
    sa.Column('status', sa.Enum('open', 'closed', name='gradingperiodstatus'), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['term_id'], ['academic_terms.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('term_id', 'order')
    )
    op.create_index(op.f('ix_grading_periods_institution_id'), 'grading_periods', ['institution_id'], unique=False)
    op.create_index(op.f('ix_grading_periods_term_id'), 'grading_periods', ['term_id'], unique=False)
    op.create_table('learning_path_courses',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('learning_path_id', sa.Uuid(), nullable=False),
    sa.Column('course_id', sa.Uuid(), nullable=False),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['learning_path_id'], ['learning_paths.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('learning_path_id', 'course_id')
    )
    op.create_index(op.f('ix_learning_path_courses_course_id'), 'learning_path_courses', ['course_id'], unique=False)
    op.create_index(op.f('ix_learning_path_courses_institution_id'), 'learning_path_courses', ['institution_id'], unique=False)
    op.create_index(op.f('ix_learning_path_courses_learning_path_id'), 'learning_path_courses', ['learning_path_id'], unique=False)
    op.create_table('locations',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('campus_id', sa.Uuid(), nullable=True),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['campus_id'], ['campuses.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_locations_campus_id'), 'locations', ['campus_id'], unique=False)
    op.create_index(op.f('ix_locations_institution_id'), 'locations', ['institution_id'], unique=False)
    op.create_table('platform_invoices',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.Column('subscription_id', sa.Uuid(), nullable=False),
    sa.Column('plan_name', sa.String(length=120), nullable=False),
    sa.Column('period_start', sa.Date(), nullable=False),
    sa.Column('period_end', sa.Date(), nullable=False),
    sa.Column('amount_cents', sa.Integer(), nullable=False),
    sa.Column('due_on', sa.Date(), nullable=False),
    sa.Column('status', sa.Enum('pending', 'paid', 'cancelled', name='platforminvoicestatus'), nullable=False),
    sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['subscription_id'], ['institution_subscriptions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('subscription_id', 'period_start')
    )
    op.create_index(op.f('ix_platform_invoices_institution_id'), 'platform_invoices', ['institution_id'], unique=False)
    op.create_index(op.f('ix_platform_invoices_subscription_id'), 'platform_invoices', ['subscription_id'], unique=False)
    op.create_table('programs',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('unit_id', sa.Uuid(), nullable=True),
    sa.Column('code', sa.String(length=40), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('level', sa.Enum('basic', 'technical', 'undergraduate', 'graduate', 'free', name='programlevel'), nullable=False),
    sa.Column('degree', sa.String(length=120), nullable=True),
    sa.Column('duration_terms', sa.Integer(), nullable=True),
    sa.Column('total_hours', sa.Integer(), nullable=True),
    sa.Column('total_credits', sa.Integer(), nullable=True),
    sa.Column('complementary_hours', sa.Integer(), nullable=True),
    sa.Column('internship_hours', sa.Integer(), nullable=True),
    sa.Column('requires_final_project', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('status', sa.Enum('draft', 'active', 'inactive', name='programstatus'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['unit_id'], ['academic_units.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('institution_id', 'code')
    )
    op.create_index(op.f('ix_programs_institution_id'), 'programs', ['institution_id'], unique=False)
    op.create_index(op.f('ix_programs_unit_id'), 'programs', ['unit_id'], unique=False)
    op.create_table('subjects',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('code', sa.String(length=40), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('syllabus', sa.Text(), nullable=True),
    sa.Column('hours', sa.Integer(), nullable=False),
    sa.Column('credits', sa.Integer(), nullable=True),
    sa.Column('course_id', sa.Uuid(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('institution_id', 'code')
    )
    op.create_index(op.f('ix_subjects_course_id'), 'subjects', ['course_id'], unique=False)
    op.create_index(op.f('ix_subjects_institution_id'), 'subjects', ['institution_id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('email', sa.String(length=200), nullable=False),
    sa.Column('password_hash', sa.String(length=200), nullable=False),
    sa.Column('role', sa.Enum('student', 'instructor', 'coordinator', 'company_manager', 'admin', 'super_admin', 'institution_admin', 'secretary', 'guardian', name='userrole'), nullable=False),
    sa.Column('organization_id', sa.Uuid(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_organization_id'), 'users', ['organization_id'], unique=False)
    op.create_table('access_role_assignments',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('role_id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['access_roles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('role_id', 'user_id')
    )
    op.create_index(op.f('ix_access_role_assignments_institution_id'), 'access_role_assignments', ['institution_id'], unique=False)
    op.create_index(op.f('ix_access_role_assignments_role_id'), 'access_role_assignments', ['role_id'], unique=False)
    op.create_index(op.f('ix_access_role_assignments_user_id'), 'access_role_assignments', ['user_id'], unique=False)
    op.create_table('benefit_stock_entries',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('item_id', sa.Uuid(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('unit_cost_cents', sa.Integer(), nullable=False),
    sa.Column('origin', sa.Enum('purchase', 'donation', name='stockorigin'), nullable=False),
    sa.Column('funding_source_id', sa.Uuid(), nullable=True),
    sa.Column('received_on', sa.Date(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_by_id', sa.Uuid(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['funding_source_id'], ['funding_sources.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['item_id'], ['benefit_items.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_benefit_stock_entries_funding_source_id'), 'benefit_stock_entries', ['funding_source_id'], unique=False)
    op.create_index(op.f('ix_benefit_stock_entries_institution_id'), 'benefit_stock_entries', ['institution_id'], unique=False)
    op.create_index(op.f('ix_benefit_stock_entries_item_id'), 'benefit_stock_entries', ['item_id'], unique=False)
    op.create_table('certificates',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('course_id', sa.Uuid(), nullable=False),
    sa.Column('validation_code', sa.String(length=120), nullable=False),
    sa.Column('issued_by_id', sa.Uuid(), nullable=True),
    sa.Column('issued_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('revoked_reason', sa.Text(), nullable=True),
    sa.Column('pdf_url', sa.String(length=500), nullable=True),
    sa.Column('signature_algorithm', sa.String(length=80), nullable=True),
    sa.Column('signature_hash', sa.String(length=128), nullable=True),
    sa.Column('signed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['issued_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('student_id', 'course_id')
    )
    op.create_index(op.f('ix_certificates_course_id'), 'certificates', ['course_id'], unique=False)
    op.create_index(op.f('ix_certificates_institution_id'), 'certificates', ['institution_id'], unique=False)
    op.create_index(op.f('ix_certificates_issued_by_id'), 'certificates', ['issued_by_id'], unique=False)
    op.create_index(op.f('ix_certificates_student_id'), 'certificates', ['student_id'], unique=False)
    op.create_index(op.f('ix_certificates_validation_code'), 'certificates', ['validation_code'], unique=True)
    op.create_table('chat_conversations',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('course_id', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('instructor_id', sa.Uuid(), nullable=True),
    sa.Column('subject', sa.String(length=200), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['instructor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('course_id', 'student_id', 'instructor_id')
    )
    op.create_index(op.f('ix_chat_conversations_course_id'), 'chat_conversations', ['course_id'], unique=False)
    op.create_index(op.f('ix_chat_conversations_institution_id'), 'chat_conversations', ['institution_id'], unique=False)
    op.create_index(op.f('ix_chat_conversations_instructor_id'), 'chat_conversations', ['instructor_id'], unique=False)
    op.create_index(op.f('ix_chat_conversations_student_id'), 'chat_conversations', ['student_id'], unique=False)
    op.create_table('class_groups',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('program_id', sa.Uuid(), nullable=False),
    sa.Column('term_id', sa.Uuid(), nullable=False),
    sa.Column('curriculum_term_number', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('shift', sa.Enum('morning', 'afternoon', 'evening', 'full_time', name='shift'), nullable=False),
    sa.Column('capacity', sa.Integer(), nullable=True),
    sa.Column('homeroom_teacher_id', sa.Uuid(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['homeroom_teacher_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ),
    sa.ForeignKeyConstraint(['term_id'], ['academic_terms.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('term_id', 'name')
    )
    op.create_index(op.f('ix_class_groups_homeroom_teacher_id'), 'class_groups', ['homeroom_teacher_id'], unique=False)
    op.create_index(op.f('ix_class_groups_institution_id'), 'class_groups', ['institution_id'], unique=False)
    op.create_index(op.f('ix_class_groups_program_id'), 'class_groups', ['program_id'], unique=False)
    op.create_index(op.f('ix_class_groups_term_id'), 'class_groups', ['term_id'], unique=False)
    op.create_table('curricula',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('program_id', sa.Uuid(), nullable=False),
    sa.Column('version', sa.String(length=40), nullable=False),
    sa.Column('valid_from', sa.Date(), nullable=True),
    sa.Column('status', sa.Enum('draft', 'active', 'archived', name='curriculumstatus'), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('program_id', 'version')
    )
    op.create_index(op.f('ix_curricula_institution_id'), 'curricula', ['institution_id'], unique=False)
    op.create_index(op.f('ix_curricula_program_id'), 'curricula', ['program_id'], unique=False)
    op.create_table('enrollments',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('course_id', sa.Uuid(), nullable=False),
    sa.Column('enrolled_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('student_id', 'course_id')
    )
    op.create_index(op.f('ix_enrollments_course_id'), 'enrollments', ['course_id'], unique=False)
    op.create_index(op.f('ix_enrollments_institution_id'), 'enrollments', ['institution_id'], unique=False)
    op.create_index(op.f('ix_enrollments_student_id'), 'enrollments', ['student_id'], unique=False)
    op.create_table('forum_threads',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('course_id', sa.Uuid(), nullable=False),
    sa.Column('author_id', sa.Uuid(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_forum_threads_author_id'), 'forum_threads', ['author_id'], unique=False)
    op.create_index(op.f('ix_forum_threads_course_id'), 'forum_threads', ['course_id'], unique=False)
    op.create_index(op.f('ix_forum_threads_institution_id'), 'forum_threads', ['institution_id'], unique=False)
    op.create_table('institution_memberships',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('role', sa.Enum('student', 'instructor', 'coordinator', 'company_manager', 'admin', 'super_admin', 'institution_admin', 'secretary', 'guardian', name='userrole'), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('institution_id', 'user_id')
    )
    op.create_index(op.f('ix_institution_memberships_institution_id'), 'institution_memberships', ['institution_id'], unique=False)
    op.create_index(op.f('ix_institution_memberships_user_id'), 'institution_memberships', ['user_id'], unique=False)
    op.create_table('institution_member_roles',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('membership_id', sa.Uuid(), nullable=False),
    sa.Column('role', sa.Enum('student', 'instructor', 'coordinator', 'company_manager', 'admin', 'super_admin', 'institution_admin', 'secretary', 'guardian', name='userrole'), nullable=False),
    sa.ForeignKeyConstraint(['membership_id'], ['institution_memberships.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('membership_id', 'role')
    )
    op.create_index(op.f('ix_institution_member_roles_membership_id'), 'institution_member_roles', ['membership_id'], unique=False)
    op.create_table('instructor_profiles',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('specialties', sa.Text(), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('rating', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_instructor_profiles_student_id'), 'instructor_profiles', ['student_id'], unique=True)
    op.create_table('lessons',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('course_id', sa.Uuid(), nullable=False),
    sa.Column('module_id', sa.Uuid(), nullable=True),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('text', 'video', 'pdf', 'live', 'in_person', 'voice', 'assessment', name='lessontype'), nullable=False),
    sa.Column('video_url', sa.String(length=500), nullable=True),
    sa.Column('video_path', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['module_id'], ['course_modules.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lessons_course_id'), 'lessons', ['course_id'], unique=False)
    op.create_index(op.f('ix_lessons_institution_id'), 'lessons', ['institution_id'], unique=False)
    op.create_index(op.f('ix_lessons_module_id'), 'lessons', ['module_id'], unique=False)
    op.create_table('registration_windows',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('term_id', sa.Uuid(), nullable=False),
    sa.Column('program_id', sa.Uuid(), nullable=True),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('opens_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('closes_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('min_credits', sa.Integer(), nullable=True),
    sa.Column('max_credits', sa.Integer(), nullable=True),
    sa.Column('allow_waitlist', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ),
    sa.ForeignKeyConstraint(['term_id'], ['academic_terms.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_registration_windows_institution_id'), 'registration_windows', ['institution_id'], unique=False)
    op.create_index(op.f('ix_registration_windows_program_id'), 'registration_windows', ['program_id'], unique=False)
    op.create_index(op.f('ix_registration_windows_term_id'), 'registration_windows', ['term_id'], unique=False)
    op.create_table('rooms',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('location_id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('capacity', sa.Integer(), nullable=False),
    sa.Column('resources', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rooms_institution_id'), 'rooms', ['institution_id'], unique=False)
    op.create_index(op.f('ix_rooms_location_id'), 'rooms', ['location_id'], unique=False)
    op.create_table('student_guardians',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('guardian_id', sa.Uuid(), nullable=False),
    sa.Column('relationship_kind', sa.Enum('mother', 'father', 'legal_guardian', 'grandparent', 'other', name='guardianrelationship'), nullable=False),
    sa.Column('is_financial', sa.Boolean(), nullable=False),
    sa.Column('can_pick_up', sa.Boolean(), nullable=False),
    sa.Column('is_primary', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['guardian_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('student_id', 'guardian_id')
    )
    op.create_index(op.f('ix_student_guardians_guardian_id'), 'student_guardians', ['guardian_id'], unique=False)
    op.create_index(op.f('ix_student_guardians_institution_id'), 'student_guardians', ['institution_id'], unique=False)
    op.create_index(op.f('ix_student_guardians_student_id'), 'student_guardians', ['student_id'], unique=False)
    op.create_table('student_profiles',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('phone', sa.String(length=50), nullable=True),
    sa.Column('document', sa.String(length=50), nullable=True),
    sa.Column('position', sa.String(length=120), nullable=True),
    sa.Column('department', sa.String(length=120), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_student_profiles_document'), 'student_profiles', ['document'], unique=False)
    op.create_index(op.f('ix_student_profiles_student_id'), 'student_profiles', ['student_id'], unique=True)
    op.create_table('subject_equivalences',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('subject_id', sa.Uuid(), nullable=False),
    sa.Column('equivalent_subject_id', sa.Uuid(), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['equivalent_subject_id'], ['subjects.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('subject_id', 'equivalent_subject_id')
    )
    op.create_index(op.f('ix_subject_equivalences_equivalent_subject_id'), 'subject_equivalences', ['equivalent_subject_id'], unique=False)
    op.create_index(op.f('ix_subject_equivalences_institution_id'), 'subject_equivalences', ['institution_id'], unique=False)
    op.create_index(op.f('ix_subject_equivalences_subject_id'), 'subject_equivalences', ['subject_id'], unique=False)
    op.create_table('subject_prerequisites',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('subject_id', sa.Uuid(), nullable=False),
    sa.Column('required_subject_id', sa.Uuid(), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['required_subject_id'], ['subjects.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('subject_id', 'required_subject_id')
    )
    op.create_index(op.f('ix_subject_prerequisites_institution_id'), 'subject_prerequisites', ['institution_id'], unique=False)
    op.create_index(op.f('ix_subject_prerequisites_required_subject_id'), 'subject_prerequisites', ['required_subject_id'], unique=False)
    op.create_index(op.f('ix_subject_prerequisites_subject_id'), 'subject_prerequisites', ['subject_id'], unique=False)
    op.create_table('subscriptions',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('billing_plan_id', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=True),
    sa.Column('organization_id', sa.Uuid(), nullable=True),
    sa.Column('status', sa.Enum('active', 'paused', 'cancelled', 'overdue', 'completed', name='subscriptionstatus'), nullable=False),
    sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=False),
    sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=False),
    sa.Column('next_billing_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('gateway_name', sa.String(length=50), nullable=True),
    sa.Column('gateway_customer_id', sa.String(length=120), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.CheckConstraint('student_id IS NOT NULL OR organization_id IS NOT NULL', name='subscription_customer_check'),
    sa.ForeignKeyConstraint(['billing_plan_id'], ['billing_plans.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('billing_plan_id', 'organization_id'),
    sa.UniqueConstraint('billing_plan_id', 'student_id')
    )
    op.create_index(op.f('ix_subscriptions_billing_plan_id'), 'subscriptions', ['billing_plan_id'], unique=False)
    op.create_index(op.f('ix_subscriptions_institution_id'), 'subscriptions', ['institution_id'], unique=False)
    op.create_index(op.f('ix_subscriptions_organization_id'), 'subscriptions', ['organization_id'], unique=False)
    op.create_index(op.f('ix_subscriptions_student_id'), 'subscriptions', ['student_id'], unique=False)
    op.create_table('warehouse_entries',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('item_id', sa.Uuid(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('unit_cost_cents', sa.Integer(), nullable=False),
    sa.Column('origin', sa.Enum('purchase', 'donation', name='entryorigin'), nullable=False),
    sa.Column('funding_source_id', sa.Uuid(), nullable=True),
    sa.Column('received_on', sa.Date(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_by_id', sa.Uuid(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['funding_source_id'], ['funding_sources.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['item_id'], ['warehouse_items.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_warehouse_entries_funding_source_id'), 'warehouse_entries', ['funding_source_id'], unique=False)
    op.create_index(op.f('ix_warehouse_entries_institution_id'), 'warehouse_entries', ['institution_id'], unique=False)
    op.create_index(op.f('ix_warehouse_entries_item_id'), 'warehouse_entries', ['item_id'], unique=False)
    op.create_table('assignment_submissions',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('lesson_id', sa.Uuid(), nullable=False),
    sa.Column('course_id', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('file_path', sa.String(length=500), nullable=True),
    sa.Column('file_name', sa.String(length=255), nullable=True),
    sa.Column('file_size', sa.Integer(), nullable=True),
    sa.Column('status', sa.Enum('submitted', 'reviewed', 'returned', name='assignmentsubmissionstatus'), nullable=False),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('feedback', sa.Text(), nullable=True),
    sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('reviewed_by_id', sa.Uuid(), nullable=True),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ),
    sa.ForeignKeyConstraint(['reviewed_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('lesson_id', 'student_id')
    )
    op.create_index(op.f('ix_assignment_submissions_course_id'), 'assignment_submissions', ['course_id'], unique=False)
    op.create_index(op.f('ix_assignment_submissions_institution_id'), 'assignment_submissions', ['institution_id'], unique=False)
    op.create_index(op.f('ix_assignment_submissions_lesson_id'), 'assignment_submissions', ['lesson_id'], unique=False)
    op.create_index(op.f('ix_assignment_submissions_reviewed_by_id'), 'assignment_submissions', ['reviewed_by_id'], unique=False)
    op.create_index(op.f('ix_assignment_submissions_student_id'), 'assignment_submissions', ['student_id'], unique=False)
    op.create_table('chat_messages',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('conversation_id', sa.Uuid(), nullable=False),
    sa.Column('sender_id', sa.Uuid(), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['conversation_id'], ['chat_conversations.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_messages_conversation_id'), 'chat_messages', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_chat_messages_institution_id'), 'chat_messages', ['institution_id'], unique=False)
    op.create_index(op.f('ix_chat_messages_sender_id'), 'chat_messages', ['sender_id'], unique=False)
    op.create_table('class_offerings',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('course_id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('starts_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('ends_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('capacity', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('draft', 'open', 'closed', 'completed', 'cancelled', name='classstatus'), nullable=False),
    sa.Column('location_id', sa.Uuid(), nullable=True),
    sa.Column('room_id', sa.Uuid(), nullable=True),
    sa.Column('instructor_id', sa.Uuid(), nullable=True),
    sa.Column('term_id', sa.Uuid(), nullable=True),
    sa.Column('subject_id', sa.Uuid(), nullable=True),
    sa.Column('class_group_id', sa.Uuid(), nullable=True),
    sa.Column('grading_scheme_id', sa.Uuid(), nullable=True),
    sa.Column('funding_source_id', sa.Uuid(), nullable=True),
    sa.Column('max_absence_percent', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['class_group_id'], ['class_groups.id'], ),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.ForeignKeyConstraint(['funding_source_id'], ['funding_sources.id'], ),
    sa.ForeignKeyConstraint(['grading_scheme_id'], ['grading_schemes.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['instructor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
    sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ),
    sa.ForeignKeyConstraint(['term_id'], ['academic_terms.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_class_offerings_class_group_id'), 'class_offerings', ['class_group_id'], unique=False)
    op.create_index(op.f('ix_class_offerings_course_id'), 'class_offerings', ['course_id'], unique=False)
    op.create_index(op.f('ix_class_offerings_funding_source_id'), 'class_offerings', ['funding_source_id'], unique=False)
    op.create_index(op.f('ix_class_offerings_grading_scheme_id'), 'class_offerings', ['grading_scheme_id'], unique=False)
    op.create_index(op.f('ix_class_offerings_institution_id'), 'class_offerings', ['institution_id'], unique=False)
    op.create_index(op.f('ix_class_offerings_instructor_id'), 'class_offerings', ['instructor_id'], unique=False)
    op.create_index(op.f('ix_class_offerings_location_id'), 'class_offerings', ['location_id'], unique=False)
    op.create_index(op.f('ix_class_offerings_room_id'), 'class_offerings', ['room_id'], unique=False)
    op.create_index(op.f('ix_class_offerings_subject_id'), 'class_offerings', ['subject_id'], unique=False)
    op.create_index(op.f('ix_class_offerings_term_id'), 'class_offerings', ['term_id'], unique=False)
    op.create_table('curriculum_components',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('curriculum_id', sa.Uuid(), nullable=False),
    sa.Column('subject_id', sa.Uuid(), nullable=False),
    sa.Column('term_number', sa.Integer(), nullable=False),
    sa.Column('kind', sa.Enum('mandatory', 'elective', 'optional', name='componentkind'), nullable=False),
    sa.Column('hours', sa.Integer(), nullable=True),
    sa.Column('credits', sa.Integer(), nullable=True),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['curriculum_id'], ['curricula.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('curriculum_id', 'subject_id')
    )
    op.create_index(op.f('ix_curriculum_components_curriculum_id'), 'curriculum_components', ['curriculum_id'], unique=False)
    op.create_index(op.f('ix_curriculum_components_institution_id'), 'curriculum_components', ['institution_id'], unique=False)
    op.create_index(op.f('ix_curriculum_components_subject_id'), 'curriculum_components', ['subject_id'], unique=False)
    op.create_table('forum_posts',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('thread_id', sa.Uuid(), nullable=False),
    sa.Column('author_id', sa.Uuid(), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['thread_id'], ['forum_threads.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_forum_posts_author_id'), 'forum_posts', ['author_id'], unique=False)
    op.create_index(op.f('ix_forum_posts_institution_id'), 'forum_posts', ['institution_id'], unique=False)
    op.create_index(op.f('ix_forum_posts_thread_id'), 'forum_posts', ['thread_id'], unique=False)
    op.create_table('instructor_availability',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('instructor_profile_id', sa.Uuid(), nullable=False),
    sa.Column('day_of_week', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.String(length=5), nullable=False),
    sa.Column('end_time', sa.String(length=5), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['instructor_profile_id'], ['instructor_profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_instructor_availability_instructor_profile_id'), 'instructor_availability', ['instructor_profile_id'], unique=False)
    op.create_table('instructor_ratings',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('instructor_profile_id', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('score', sa.Integer(), nullable=False),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['instructor_profile_id'], ['instructor_profiles.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_instructor_ratings_instructor_profile_id'), 'instructor_ratings', ['instructor_profile_id'], unique=False)
    op.create_index(op.f('ix_instructor_ratings_student_id'), 'instructor_ratings', ['student_id'], unique=False)
    op.create_table('program_enrollments',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('program_id', sa.Uuid(), nullable=False),
    sa.Column('curriculum_id', sa.Uuid(), nullable=False),
    sa.Column('entry_term_id', sa.Uuid(), nullable=True),
    sa.Column('registration_number', sa.String(length=40), nullable=False),
    sa.Column('status', sa.Enum('active', 'locked', 'graduated', 'dropped', 'transferred', 'cancelled', name='programenrollmentstatus'), nullable=False),
    sa.Column('enrolled_on', sa.Date(), nullable=False),
    sa.Column('status_changed_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('transferred_from_id', sa.Uuid(), nullable=True),
    sa.Column('concluded_on', sa.Date(), nullable=True),
    sa.Column('ceremony_on', sa.Date(), nullable=True),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['curriculum_id'], ['curricula.id'], ),
    sa.ForeignKeyConstraint(['entry_term_id'], ['academic_terms.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['transferred_from_id'], ['program_enrollments.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('institution_id', 'registration_number')
    )
    op.create_index(op.f('ix_program_enrollments_curriculum_id'), 'program_enrollments', ['curriculum_id'], unique=False)
    op.create_index(op.f('ix_program_enrollments_entry_term_id'), 'program_enrollments', ['entry_term_id'], unique=False)
    op.create_index(op.f('ix_program_enrollments_institution_id'), 'program_enrollments', ['institution_id'], unique=False)
    op.create_index(op.f('ix_program_enrollments_program_id'), 'program_enrollments', ['program_id'], unique=False)
    op.create_index(op.f('ix_program_enrollments_student_id'), 'program_enrollments', ['student_id'], unique=False)
    op.create_index(op.f('ix_program_enrollments_transferred_from_id'), 'program_enrollments', ['transferred_from_id'], unique=False)
    op.create_table('progress',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('lesson_id', sa.Uuid(), nullable=False),
    sa.Column('status', sa.Enum('pending', 'in_progress', 'done', name='progressstatus'), nullable=False),
    sa.Column('content_consumed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('student_id', 'lesson_id')
    )
    op.create_index(op.f('ix_progress_institution_id'), 'progress', ['institution_id'], unique=False)
    op.create_index(op.f('ix_progress_lesson_id'), 'progress', ['lesson_id'], unique=False)
    op.create_index(op.f('ix_progress_student_id'), 'progress', ['student_id'], unique=False)
    op.create_table('quizzes',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('lesson_id', sa.Uuid(), nullable=False),
    sa.Column('passing_score', sa.Integer(), nullable=False),
    sa.Column('max_attempts', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quizzes_institution_id'), 'quizzes', ['institution_id'], unique=False)
    op.create_index(op.f('ix_quizzes_lesson_id'), 'quizzes', ['lesson_id'], unique=True)
    op.create_table('sessions',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('lesson_id', sa.Uuid(), nullable=False),
    sa.Column('bevox_session_id', sa.String(length=100), nullable=True),
    sa.Column('transcript', sa.Text(), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sessions_bevox_session_id'), 'sessions', ['bevox_session_id'], unique=False)
    op.create_index(op.f('ix_sessions_institution_id'), 'sessions', ['institution_id'], unique=False)
    op.create_index(op.f('ix_sessions_lesson_id'), 'sessions', ['lesson_id'], unique=False)
    op.create_index(op.f('ix_sessions_student_id'), 'sessions', ['student_id'], unique=False)
    op.create_table('student_occurrences',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('class_group_id', sa.Uuid(), nullable=True),
    sa.Column('kind', sa.Enum('behavior', 'lateness', 'material', 'health', 'merit', 'other', name='occurrencekind'), nullable=False),
    sa.Column('severity', sa.Enum('low', 'medium', 'high', name='occurrenceseverity'), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('occurred_on', sa.Date(), nullable=False),
    sa.Column('reported_by_id', sa.Uuid(), nullable=True),
    sa.Column('acknowledged_by_id', sa.Uuid(), nullable=True),
    sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['acknowledged_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['class_group_id'], ['class_groups.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['reported_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_student_occurrences_class_group_id'), 'student_occurrences', ['class_group_id'], unique=False)
    op.create_index(op.f('ix_student_occurrences_institution_id'), 'student_occurrences', ['institution_id'], unique=False)
    op.create_index(op.f('ix_student_occurrences_occurred_on'), 'student_occurrences', ['occurred_on'], unique=False)
    op.create_index(op.f('ix_student_occurrences_student_id'), 'student_occurrences', ['student_id'], unique=False)
    op.create_table('tuition_plans',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('basis', sa.Enum('program', 'class_group', 'credit', name='tuitionbasis'), nullable=False),
    sa.Column('term_id', sa.Uuid(), nullable=False),
    sa.Column('program_id', sa.Uuid(), nullable=True),
    sa.Column('class_group_id', sa.Uuid(), nullable=True),
    sa.Column('amount_cents', sa.Integer(), nullable=False),
    sa.Column('installments', sa.Integer(), nullable=False),
    sa.Column('first_due_on', sa.Date(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['class_group_id'], ['class_groups.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ),
    sa.ForeignKeyConstraint(['term_id'], ['academic_terms.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tuition_plans_class_group_id'), 'tuition_plans', ['class_group_id'], unique=False)
    op.create_index(op.f('ix_tuition_plans_institution_id'), 'tuition_plans', ['institution_id'], unique=False)
    op.create_index(op.f('ix_tuition_plans_program_id'), 'tuition_plans', ['program_id'], unique=False)
    op.create_index(op.f('ix_tuition_plans_term_id'), 'tuition_plans', ['term_id'], unique=False)
    op.create_table('academic_declarations',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('program_enrollment_id', sa.Uuid(), nullable=False),
    sa.Column('kind', sa.Enum('enrollment', 'attendance', 'completion', name='declarationkind'), nullable=False),
    sa.Column('term_id', sa.Uuid(), nullable=True),
    sa.Column('validation_code', sa.String(length=40), nullable=False),
    sa.Column('title', sa.String(length=120), nullable=False),
    sa.Column('lines', sa.JSON(), nullable=False),
    sa.Column('issued_by_id', sa.Uuid(), nullable=True),
    sa.Column('issued_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('signature_hash', sa.String(length=128), nullable=False),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('revoked_reason', sa.Text(), nullable=True),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['issued_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['program_enrollment_id'], ['program_enrollments.id'], ),
    sa.ForeignKeyConstraint(['term_id'], ['academic_terms.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_academic_declarations_institution_id'), 'academic_declarations', ['institution_id'], unique=False)
    op.create_index(op.f('ix_academic_declarations_program_enrollment_id'), 'academic_declarations', ['program_enrollment_id'], unique=False)
    op.create_index(op.f('ix_academic_declarations_validation_code'), 'academic_declarations', ['validation_code'], unique=True)
    op.create_table('admission_calls',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('class_offering_id', sa.Uuid(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('method', sa.Enum('first_come', 'lottery', 'review', name='selectionmethod'), nullable=False),
    sa.Column('seats', sa.Integer(), nullable=False),
    sa.Column('reserved_seats', sa.Integer(), nullable=False),
    sa.Column('reserved_label', sa.String(length=200), nullable=True),
    sa.Column('opens_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('closes_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('confirmation_days', sa.Integer(), nullable=False),
    sa.Column('min_age', sa.Integer(), nullable=True),
    sa.Column('max_age', sa.Integer(), nullable=True),
    sa.Column('min_schooling', sa.Enum('none', 'elementary_incomplete', 'elementary', 'high_school_incomplete', 'high_school', 'higher_incomplete', 'higher', name='schooling'), nullable=True),
    sa.Column('max_income_per_capita_cents', sa.Integer(), nullable=True),
    sa.Column('required_city', sa.String(length=120), nullable=True),
    sa.Column('required_documents', sa.JSON(), nullable=False),
    sa.Column('status', sa.Enum('draft', 'open', 'closed', 'selected', name='admissioncallstatus'), nullable=False),
    sa.Column('lottery_seed', sa.String(length=64), nullable=True),
    sa.Column('selected_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['class_offering_id'], ['class_offerings.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admission_calls_class_offering_id'), 'admission_calls', ['class_offering_id'], unique=False)
    op.create_index(op.f('ix_admission_calls_institution_id'), 'admission_calls', ['institution_id'], unique=False)
    op.create_table('agenda_items',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('class_group_id', sa.Uuid(), nullable=False),
    sa.Column('class_offering_id', sa.Uuid(), nullable=True),
    sa.Column('kind', sa.Enum('homework', 'test', 'event', 'notice', name='agendaitemkind'), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('due_on', sa.Date(), nullable=False),
    sa.Column('created_by_id', sa.Uuid(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['class_group_id'], ['class_groups.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['class_offering_id'], ['class_offerings.id'], ),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agenda_items_class_group_id'), 'agenda_items', ['class_group_id'], unique=False)
    op.create_index(op.f('ix_agenda_items_class_offering_id'), 'agenda_items', ['class_offering_id'], unique=False)
    op.create_index(op.f('ix_agenda_items_due_on'), 'agenda_items', ['due_on'], unique=False)
    op.create_index(op.f('ix_agenda_items_institution_id'), 'agenda_items', ['institution_id'], unique=False)
    op.create_table('assessment_items',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('class_offering_id', sa.Uuid(), nullable=False),
    sa.Column('grading_period_id', sa.Uuid(), nullable=True),
    sa.Column('name', sa.String(length=160), nullable=False),
    sa.Column('kind', sa.Enum('test', 'assignment', 'quiz', 'practical', 'participation', name='assessmentkind'), nullable=False),
    sa.Column('weight', sa.Float(), nullable=False),
    sa.Column('max_score', sa.Float(), nullable=False),
    sa.Column('quiz_id', sa.Uuid(), nullable=True),
    sa.Column('due_on', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['class_offering_id'], ['class_offerings.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['grading_period_id'], ['grading_periods.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_assessment_items_class_offering_id'), 'assessment_items', ['class_offering_id'], unique=False)
    op.create_index(op.f('ix_assessment_items_grading_period_id'), 'assessment_items', ['grading_period_id'], unique=False)
    op.create_index(op.f('ix_assessment_items_institution_id'), 'assessment_items', ['institution_id'], unique=False)
    op.create_index(op.f('ix_assessment_items_quiz_id'), 'assessment_items', ['quiz_id'], unique=False)
    op.create_table('attendance',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('lesson_id', sa.Uuid(), nullable=False),
    sa.Column('session_id', sa.Uuid(), nullable=True),
    sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ),
    sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_attendance_institution_id'), 'attendance', ['institution_id'], unique=False)
    op.create_index(op.f('ix_attendance_lesson_id'), 'attendance', ['lesson_id'], unique=False)
    op.create_index(op.f('ix_attendance_student_id'), 'attendance', ['student_id'], unique=False)
    op.create_table('charges',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('billing_plan_id', sa.Uuid(), nullable=True),
    sa.Column('subscription_id', sa.Uuid(), nullable=True),
    sa.Column('student_id', sa.Uuid(), nullable=True),
    sa.Column('organization_id', sa.Uuid(), nullable=True),
    sa.Column('course_id', sa.Uuid(), nullable=True),
    sa.Column('class_offering_id', sa.Uuid(), nullable=True),
    sa.Column('amount_cents', sa.Integer(), nullable=False),
    sa.Column('currency', sa.String(length=10), nullable=False),
    sa.Column('payment_method', sa.Enum('pix', 'card', 'boleto', 'manual', name='paymentmethod'), nullable=False),
    sa.Column('status', sa.Enum('pending', 'paid', 'failed', 'cancelled', 'refunded', name='chargestatus'), nullable=False),
    sa.Column('gateway_name', sa.String(length=50), nullable=True),
    sa.Column('gateway_customer_id', sa.String(length=120), nullable=True),
    sa.Column('gateway_reference', sa.String(length=120), nullable=True),
    sa.Column('gateway_status', sa.String(length=80), nullable=True),
    sa.Column('checkout_url', sa.String(length=500), nullable=True),
    sa.Column('bank_slip_url', sa.String(length=500), nullable=True),
    sa.Column('pix_qr_code_payload', sa.Text(), nullable=True),
    sa.Column('pix_qr_code_image', sa.Text(), nullable=True),
    sa.Column('due_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('program_enrollment_id', sa.Uuid(), nullable=True),
    sa.Column('tuition_plan_id', sa.Uuid(), nullable=True),
    sa.Column('installment_number', sa.Integer(), nullable=True),
    sa.Column('payer_id', sa.Uuid(), nullable=True),
    sa.Column('gross_amount_cents', sa.Integer(), nullable=True),
    sa.Column('discount_cents', sa.Integer(), server_default='0', nullable=False),
    sa.Column('punctuality_discount_cents', sa.Integer(), server_default='0', nullable=False),
    sa.Column('fine_cents', sa.Integer(), server_default='0', nullable=False),
    sa.Column('interest_cents', sa.Integer(), server_default='0', nullable=False),
    sa.Column('amount_paid_cents', sa.Integer(), nullable=True),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['billing_plan_id'], ['billing_plans.id'], ),
    sa.ForeignKeyConstraint(['class_offering_id'], ['class_offerings.id'], ),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
    sa.ForeignKeyConstraint(['payer_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['program_enrollment_id'], ['program_enrollments.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ),
    sa.ForeignKeyConstraint(['tuition_plan_id'], ['tuition_plans.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('program_enrollment_id', 'tuition_plan_id', 'installment_number', name='uq_charges_tuition_installment')
    )
    op.create_index(op.f('ix_charges_billing_plan_id'), 'charges', ['billing_plan_id'], unique=False)
    op.create_index(op.f('ix_charges_class_offering_id'), 'charges', ['class_offering_id'], unique=False)
    op.create_index(op.f('ix_charges_course_id'), 'charges', ['course_id'], unique=False)
    op.create_index(op.f('ix_charges_gateway_reference'), 'charges', ['gateway_reference'], unique=False)
    op.create_index(op.f('ix_charges_institution_id'), 'charges', ['institution_id'], unique=False)
    op.create_index(op.f('ix_charges_organization_id'), 'charges', ['organization_id'], unique=False)
    op.create_index(op.f('ix_charges_payer_id'), 'charges', ['payer_id'], unique=False)
    op.create_index(op.f('ix_charges_program_enrollment_id'), 'charges', ['program_enrollment_id'], unique=False)
    op.create_index(op.f('ix_charges_student_id'), 'charges', ['student_id'], unique=False)
    op.create_index(op.f('ix_charges_subscription_id'), 'charges', ['subscription_id'], unique=False)
    op.create_index(op.f('ix_charges_tuition_plan_id'), 'charges', ['tuition_plan_id'], unique=False)
    op.create_table('class_enrollments',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('class_offering_id', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('status', sa.Enum('active', 'cancelled', 'completed', name='classenrollmentstatus'), nullable=False),
    sa.Column('enrolled_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('final_grade', sa.Float(), nullable=True),
    sa.Column('recovery_score', sa.Float(), nullable=True),
    sa.Column('attendance_rate', sa.Float(), nullable=True),
    sa.Column('result', sa.Enum('in_progress', 'recovery', 'approved', 'failed', 'failed_attendance', name='classenrollmentresult'), server_default='in_progress', nullable=False),
    sa.Column('dismissed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('dismissal_reason', sa.String(length=300), nullable=True),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['class_offering_id'], ['class_offerings.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('class_offering_id', 'student_id')
    )
    op.create_index(op.f('ix_class_enrollments_class_offering_id'), 'class_enrollments', ['class_offering_id'], unique=False)
    op.create_index(op.f('ix_class_enrollments_institution_id'), 'class_enrollments', ['institution_id'], unique=False)
    op.create_index(op.f('ix_class_enrollments_student_id'), 'class_enrollments', ['student_id'], unique=False)
    op.create_table('class_group_members',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('class_group_id', sa.Uuid(), nullable=False),
    sa.Column('program_enrollment_id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['class_group_id'], ['class_groups.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['program_enrollment_id'], ['program_enrollments.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('class_group_id', 'program_enrollment_id')
    )
    op.create_index(op.f('ix_class_group_members_class_group_id'), 'class_group_members', ['class_group_id'], unique=False)
    op.create_index(op.f('ix_class_group_members_institution_id'), 'class_group_members', ['institution_id'], unique=False)
    op.create_index(op.f('ix_class_group_members_program_enrollment_id'), 'class_group_members', ['program_enrollment_id'], unique=False)
    op.create_table('complementary_activities',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('program_enrollment_id', sa.Uuid(), nullable=False),
    sa.Column('category', sa.Enum('teaching', 'research', 'extension', 'cultural', 'professional', 'other', name='activitycategory'), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('occurred_on', sa.Date(), nullable=False),
    sa.Column('hours_requested', sa.Integer(), nullable=False),
    sa.Column('hours_approved', sa.Integer(), nullable=True),
    sa.Column('status', sa.Enum('submitted', 'approved', 'rejected', name='reviewstatus'), nullable=False),
    sa.Column('decision_note', sa.Text(), nullable=True),
    sa.Column('decided_by_id', sa.Uuid(), nullable=True),
    sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['decided_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['program_enrollment_id'], ['program_enrollments.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_complementary_activities_institution_id'), 'complementary_activities', ['institution_id'], unique=False)
    op.create_index(op.f('ix_complementary_activities_program_enrollment_id'), 'complementary_activities', ['program_enrollment_id'], unique=False)
    op.create_table('credit_transfers',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('program_enrollment_id', sa.Uuid(), nullable=False),
    sa.Column('subject_id', sa.Uuid(), nullable=False),
    sa.Column('origin', sa.Enum('internal', 'external', name='credittransferorigin'), nullable=False),
    sa.Column('source_institution', sa.String(length=200), nullable=True),
    sa.Column('source_subject', sa.String(length=200), nullable=False),
    sa.Column('grade', sa.Float(), nullable=True),
    sa.Column('hours', sa.Integer(), nullable=True),
    sa.Column('status', sa.Enum('requested', 'approved', 'rejected', name='credittransferstatus'), nullable=False),
    sa.Column('decision_note', sa.Text(), nullable=True),
    sa.Column('decided_by_id', sa.Uuid(), nullable=True),
    sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['decided_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['program_enrollment_id'], ['program_enrollments.id'], ),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_credit_transfers_institution_id'), 'credit_transfers', ['institution_id'], unique=False)
    op.create_index(op.f('ix_credit_transfers_program_enrollment_id'), 'credit_transfers', ['program_enrollment_id'], unique=False)
    op.create_index(op.f('ix_credit_transfers_subject_id'), 'credit_transfers', ['subject_id'], unique=False)
    op.create_table('documents',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('document_type', sa.Enum('contract', 'term', 'material', 'policy', 'template', 'other', name='documenttype'), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('draft', 'active', 'archived', name='documentstatus'), nullable=False),
    sa.Column('course_id', sa.Uuid(), nullable=True),
    sa.Column('class_offering_id', sa.Uuid(), nullable=True),
    sa.Column('organization_id', sa.Uuid(), nullable=True),
    sa.Column('student_id', sa.Uuid(), nullable=True),
    sa.Column('uploaded_by_id', sa.Uuid(), nullable=True),
    sa.Column('latest_version_number', sa.Integer(), nullable=False),
    sa.Column('is_signed', sa.Boolean(), nullable=False),
    sa.Column('signed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('signed_by', sa.String(length=200), nullable=True),
    sa.Column('external_reference', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['class_offering_id'], ['class_offerings.id'], ),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['uploaded_by_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_class_offering_id'), 'documents', ['class_offering_id'], unique=False)
    op.create_index(op.f('ix_documents_course_id'), 'documents', ['course_id'], unique=False)
    op.create_index(op.f('ix_documents_institution_id'), 'documents', ['institution_id'], unique=False)
    op.create_index(op.f('ix_documents_organization_id'), 'documents', ['organization_id'], unique=False)
    op.create_index(op.f('ix_documents_student_id'), 'documents', ['student_id'], unique=False)
    op.create_index(op.f('ix_documents_title'), 'documents', ['title'], unique=False)
    op.create_index(op.f('ix_documents_uploaded_by_id'), 'documents', ['uploaded_by_id'], unique=False)
    op.create_table('final_projects',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('program_enrollment_id', sa.Uuid(), nullable=False),
    sa.Column('title', sa.String(length=300), nullable=False),
    sa.Column('advisor_id', sa.Uuid(), nullable=True),
    sa.Column('co_advisor_name', sa.String(length=200), nullable=True),
    sa.Column('status', sa.Enum('in_progress', 'submitted', 'approved', 'failed', name='finalprojectstatus'), nullable=False),
    sa.Column('defense_on', sa.Date(), nullable=True),
    sa.Column('grade', sa.Float(), nullable=True),
    sa.Column('committee', sa.Text(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['advisor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['program_enrollment_id'], ['program_enrollments.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_final_projects_advisor_id'), 'final_projects', ['advisor_id'], unique=False)
    op.create_index(op.f('ix_final_projects_institution_id'), 'final_projects', ['institution_id'], unique=False)
    op.create_index(op.f('ix_final_projects_program_enrollment_id'), 'final_projects', ['program_enrollment_id'], unique=True)
    op.create_table('internships',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('program_enrollment_id', sa.Uuid(), nullable=False),
    sa.Column('company_name', sa.String(length=200), nullable=False),
    sa.Column('supervisor_name', sa.String(length=200), nullable=True),
    sa.Column('advisor_id', sa.Uuid(), nullable=True),
    sa.Column('is_mandatory', sa.Boolean(), nullable=False),
    sa.Column('agreement_number', sa.String(length=80), nullable=True),
    sa.Column('starts_on', sa.Date(), nullable=False),
    sa.Column('ends_on', sa.Date(), nullable=True),
    sa.Column('planned_hours', sa.Integer(), nullable=True),
    sa.Column('status', sa.Enum('in_progress', 'completed', 'cancelled', name='internshipstatus'), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['advisor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['program_enrollment_id'], ['program_enrollments.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_internships_advisor_id'), 'internships', ['advisor_id'], unique=False)
    op.create_index(op.f('ix_internships_institution_id'), 'internships', ['institution_id'], unique=False)
    op.create_index(op.f('ix_internships_program_enrollment_id'), 'internships', ['program_enrollment_id'], unique=False)
    op.create_table('material_requests',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('requester_id', sa.Uuid(), nullable=False),
    sa.Column('class_offering_id', sa.Uuid(), nullable=True),
    sa.Column('purpose', sa.Text(), nullable=False),
    sa.Column('needed_on', sa.Date(), nullable=False),
    sa.Column('status', sa.Enum('pending', 'approved', 'rejected', 'delivered', 'closed', 'cancelled', name='requeststatus'), nullable=False),
    sa.Column('decision_note', sa.Text(), nullable=True),
    sa.Column('decided_by_id', sa.Uuid(), nullable=True),
    sa.Column('decided_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('delivered_by_id', sa.Uuid(), nullable=True),
    sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('return_due_on', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['class_offering_id'], ['class_offerings.id'], ),
    sa.ForeignKeyConstraint(['decided_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['delivered_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['requester_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_material_requests_class_offering_id'), 'material_requests', ['class_offering_id'], unique=False)
    op.create_index(op.f('ix_material_requests_institution_id'), 'material_requests', ['institution_id'], unique=False)
    op.create_index(op.f('ix_material_requests_requester_id'), 'material_requests', ['requester_id'], unique=False)
    op.create_table('offering_period_closures',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('class_offering_id', sa.Uuid(), nullable=False),
    sa.Column('grading_period_id', sa.Uuid(), nullable=False),
    sa.Column('closed_by_id', sa.Uuid(), nullable=True),
    sa.Column('closed_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['class_offering_id'], ['class_offerings.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['closed_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['grading_period_id'], ['grading_periods.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('class_offering_id', 'grading_period_id')
    )
    op.create_index(op.f('ix_offering_period_closures_class_offering_id'), 'offering_period_closures', ['class_offering_id'], unique=False)
    op.create_index(op.f('ix_offering_period_closures_grading_period_id'), 'offering_period_closures', ['grading_period_id'], unique=False)
    op.create_index(op.f('ix_offering_period_closures_institution_id'), 'offering_period_closures', ['institution_id'], unique=False)
    op.create_table('offering_time_slots',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('class_offering_id', sa.Uuid(), nullable=False),
    sa.Column('weekday', sa.Integer(), nullable=False),
    sa.Column('starts_at', sa.Time(), nullable=False),
    sa.Column('ends_at', sa.Time(), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['class_offering_id'], ['class_offerings.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_offering_time_slots_class_offering_id'), 'offering_time_slots', ['class_offering_id'], unique=False)
    op.create_index(op.f('ix_offering_time_slots_institution_id'), 'offering_time_slots', ['institution_id'], unique=False)
    op.create_table('program_enrollment_events',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('program_enrollment_id', sa.Uuid(), nullable=False),
    sa.Column('kind', sa.Enum('enrolled', 'reenrolled', 'locked', 'reactivated', 'cancelled', 'dropped', 'transferred_out', 'transferred_internal', 'curriculum_changed', 'graduated', name='enrollmenteventkind'), nullable=False),
    sa.Column('term_id', sa.Uuid(), nullable=True),
    sa.Column('reason', sa.Text(), nullable=True),
    sa.Column('details', sa.JSON(), nullable=False),
    sa.Column('created_by_id', sa.Uuid(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['program_enrollment_id'], ['program_enrollments.id'], ),
    sa.ForeignKeyConstraint(['term_id'], ['academic_terms.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_program_enrollment_events_institution_id'), 'program_enrollment_events', ['institution_id'], unique=False)
    op.create_index(op.f('ix_program_enrollment_events_program_enrollment_id'), 'program_enrollment_events', ['program_enrollment_id'], unique=False)
    op.create_index(op.f('ix_program_enrollment_events_term_id'), 'program_enrollment_events', ['term_id'], unique=False)
    op.create_table('quiz_attempts',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('quiz_id', sa.Uuid(), nullable=False),
    sa.Column('score', sa.Integer(), nullable=False),
    sa.Column('passed', sa.Boolean(), nullable=False),
    sa.Column('answers', sa.JSON(), nullable=False),
    sa.Column('attempted_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('student_id', 'quiz_id', 'attempted_at')
    )
    op.create_index(op.f('ix_quiz_attempts_institution_id'), 'quiz_attempts', ['institution_id'], unique=False)
    op.create_index(op.f('ix_quiz_attempts_quiz_id'), 'quiz_attempts', ['quiz_id'], unique=False)
    op.create_index(op.f('ix_quiz_attempts_student_id'), 'quiz_attempts', ['student_id'], unique=False)
    op.create_table('quiz_questions',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('quiz_id', sa.Uuid(), nullable=False),
    sa.Column('question', sa.Text(), nullable=False),
    sa.Column('options', sa.JSON(), nullable=False),
    sa.Column('correct_index', sa.Integer(), nullable=False),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quiz_questions_institution_id'), 'quiz_questions', ['institution_id'], unique=False)
    op.create_index(op.f('ix_quiz_questions_quiz_id'), 'quiz_questions', ['quiz_id'], unique=False)
    op.create_table('scheduled_meetings',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('class_offering_id', sa.Uuid(), nullable=False),
    sa.Column('lesson_id', sa.Uuid(), nullable=True),
    sa.Column('room_id', sa.Uuid(), nullable=True),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('starts_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('ends_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('type', sa.Enum('in_person', 'live', 'hybrid', name='meetingtype'), nullable=False),
    sa.Column('meeting_url', sa.String(length=500), nullable=True),
    sa.Column('is_closed', sa.Boolean(), nullable=False),
    sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['class_offering_id'], ['class_offerings.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ),
    sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scheduled_meetings_class_offering_id'), 'scheduled_meetings', ['class_offering_id'], unique=False)
    op.create_index(op.f('ix_scheduled_meetings_institution_id'), 'scheduled_meetings', ['institution_id'], unique=False)
    op.create_index(op.f('ix_scheduled_meetings_lesson_id'), 'scheduled_meetings', ['lesson_id'], unique=False)
    op.create_index(op.f('ix_scheduled_meetings_room_id'), 'scheduled_meetings', ['room_id'], unique=False)
    op.create_table('student_discounts',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('program_enrollment_id', sa.Uuid(), nullable=False),
    sa.Column('kind', sa.Enum('scholarship', 'sibling', 'punctuality', 'agreement', 'other', name='discountkind'), nullable=False),
    sa.Column('percent', sa.Float(), nullable=True),
    sa.Column('amount_cents', sa.Integer(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('valid_from', sa.Date(), nullable=False),
    sa.Column('valid_until', sa.Date(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['program_enrollment_id'], ['program_enrollments.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_student_discounts_institution_id'), 'student_discounts', ['institution_id'], unique=False)
    op.create_index(op.f('ix_student_discounts_program_enrollment_id'), 'student_discounts', ['program_enrollment_id'], unique=False)
    op.create_table('term_registrations',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('program_enrollment_id', sa.Uuid(), nullable=False),
    sa.Column('term_id', sa.Uuid(), nullable=False),
    sa.Column('curriculum_term_number', sa.Integer(), nullable=True),
    sa.Column('created_by_id', sa.Uuid(), nullable=True),
    sa.Column('registered_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['program_enrollment_id'], ['program_enrollments.id'], ),
    sa.ForeignKeyConstraint(['term_id'], ['academic_terms.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('program_enrollment_id', 'term_id')
    )
    op.create_index(op.f('ix_term_registrations_institution_id'), 'term_registrations', ['institution_id'], unique=False)
    op.create_index(op.f('ix_term_registrations_program_enrollment_id'), 'term_registrations', ['program_enrollment_id'], unique=False)
    op.create_index(op.f('ix_term_registrations_term_id'), 'term_registrations', ['term_id'], unique=False)
    op.create_table('waitlist_entries',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('class_offering_id', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['class_offering_id'], ['class_offerings.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('class_offering_id', 'student_id')
    )
    op.create_index(op.f('ix_waitlist_entries_class_offering_id'), 'waitlist_entries', ['class_offering_id'], unique=False)
    op.create_index(op.f('ix_waitlist_entries_institution_id'), 'waitlist_entries', ['institution_id'], unique=False)
    op.create_index(op.f('ix_waitlist_entries_student_id'), 'waitlist_entries', ['student_id'], unique=False)
    op.create_table('admission_applications',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('call_id', sa.Uuid(), nullable=False),
    sa.Column('applicant_id', sa.Uuid(), nullable=False),
    sa.Column('protocol', sa.String(length=20), nullable=False),
    sa.Column('birth_date', sa.Date(), nullable=False),
    sa.Column('schooling', sa.Enum('none', 'elementary_incomplete', 'elementary', 'high_school_incomplete', 'high_school', 'higher_incomplete', 'higher', name='schooling'), nullable=False),
    sa.Column('family_income_cents', sa.Integer(), nullable=False),
    sa.Column('household_size', sa.Integer(), nullable=False),
    sa.Column('city', sa.String(length=120), nullable=False),
    sa.Column('claims_reserved', sa.Boolean(), nullable=False),
    sa.Column('reserved_verified', sa.Boolean(), nullable=True),
    sa.Column('review_score', sa.Float(), nullable=True),
    sa.Column('status', sa.Enum('submitted', 'ineligible', 'waitlisted', 'selected', 'confirmed', 'declined', 'expired', 'withdrawn', name='applicationstatus'), nullable=False),
    sa.Column('ineligibility_reasons', sa.JSON(), nullable=False),
    sa.Column('rank', sa.Integer(), nullable=True),
    sa.Column('seat_kind', sa.Enum('general', 'reserved', name='seatkind'), nullable=True),
    sa.Column('called_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('confirm_until', sa.DateTime(timezone=True), nullable=True),
    sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['applicant_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['call_id'], ['admission_calls.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('call_id', 'applicant_id')
    )
    op.create_index(op.f('ix_admission_applications_applicant_id'), 'admission_applications', ['applicant_id'], unique=False)
    op.create_index(op.f('ix_admission_applications_call_id'), 'admission_applications', ['call_id'], unique=False)
    op.create_index(op.f('ix_admission_applications_institution_id'), 'admission_applications', ['institution_id'], unique=False)
    op.create_index(op.f('ix_admission_applications_protocol'), 'admission_applications', ['protocol'], unique=False)
    op.create_table('attendance_records',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('scheduled_meeting_id', sa.Uuid(), nullable=False),
    sa.Column('class_offering_id', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('status', sa.Enum('present', 'late', 'absent', name='attendancestatus'), nullable=False),
    sa.Column('method', sa.Enum('manual', 'qr_code', 'webhook', 'biometric', 'facial', name='attendancemethod'), nullable=False),
    sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['class_offering_id'], ['class_offerings.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['scheduled_meeting_id'], ['scheduled_meetings.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('scheduled_meeting_id', 'student_id')
    )
    op.create_index(op.f('ix_attendance_records_class_offering_id'), 'attendance_records', ['class_offering_id'], unique=False)
    op.create_index(op.f('ix_attendance_records_institution_id'), 'attendance_records', ['institution_id'], unique=False)
    op.create_index(op.f('ix_attendance_records_scheduled_meeting_id'), 'attendance_records', ['scheduled_meeting_id'], unique=False)
    op.create_index(op.f('ix_attendance_records_student_id'), 'attendance_records', ['student_id'], unique=False)
    op.create_table('benefit_deliveries',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('item_id', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('class_offering_id', sa.Uuid(), nullable=False),
    sa.Column('scheduled_meeting_id', sa.Uuid(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('unit_cost_cents', sa.Integer(), nullable=False),
    sa.Column('delivered_on', sa.Date(), nullable=False),
    sa.Column('delivered_by_id', sa.Uuid(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['class_offering_id'], ['class_offerings.id'], ),
    sa.ForeignKeyConstraint(['delivered_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['item_id'], ['benefit_items.id'], ),
    sa.ForeignKeyConstraint(['scheduled_meeting_id'], ['scheduled_meetings.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_benefit_deliveries_class_offering_id'), 'benefit_deliveries', ['class_offering_id'], unique=False)
    op.create_index(op.f('ix_benefit_deliveries_institution_id'), 'benefit_deliveries', ['institution_id'], unique=False)
    op.create_index(op.f('ix_benefit_deliveries_item_id'), 'benefit_deliveries', ['item_id'], unique=False)
    op.create_index(op.f('ix_benefit_deliveries_scheduled_meeting_id'), 'benefit_deliveries', ['scheduled_meeting_id'], unique=False)
    op.create_index(op.f('ix_benefit_deliveries_student_id'), 'benefit_deliveries', ['student_id'], unique=False)
    op.create_table('checkin_tokens',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('scheduled_meeting_id', sa.Uuid(), nullable=False),
    sa.Column('token', sa.String(length=120), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['scheduled_meeting_id'], ['scheduled_meetings.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_checkin_tokens_institution_id'), 'checkin_tokens', ['institution_id'], unique=False)
    op.create_index(op.f('ix_checkin_tokens_scheduled_meeting_id'), 'checkin_tokens', ['scheduled_meeting_id'], unique=False)
    op.create_index(op.f('ix_checkin_tokens_token'), 'checkin_tokens', ['token'], unique=True)
    op.create_table('class_diary_entries',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('class_offering_id', sa.Uuid(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('lesson_count', sa.Integer(), nullable=False),
    sa.Column('content_taught', sa.Text(), nullable=False),
    sa.Column('instructor_id', sa.Uuid(), nullable=True),
    sa.Column('scheduled_meeting_id', sa.Uuid(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['class_offering_id'], ['class_offerings.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['instructor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['scheduled_meeting_id'], ['scheduled_meetings.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('class_offering_id', 'date')
    )
    op.create_index(op.f('ix_class_diary_entries_class_offering_id'), 'class_diary_entries', ['class_offering_id'], unique=False)
    op.create_index(op.f('ix_class_diary_entries_institution_id'), 'class_diary_entries', ['institution_id'], unique=False)
    op.create_index(op.f('ix_class_diary_entries_instructor_id'), 'class_diary_entries', ['instructor_id'], unique=False)
    op.create_index(op.f('ix_class_diary_entries_scheduled_meeting_id'), 'class_diary_entries', ['scheduled_meeting_id'], unique=False)
    op.create_table('document_versions',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('document_id', sa.Uuid(), nullable=False),
    sa.Column('version_number', sa.Integer(), nullable=False),
    sa.Column('file_name', sa.String(length=255), nullable=True),
    sa.Column('mime_type', sa.String(length=120), nullable=True),
    sa.Column('file_size', sa.Integer(), nullable=True),
    sa.Column('storage_path', sa.String(length=500), nullable=True),
    sa.Column('external_url', sa.String(length=500), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_by_id', sa.Uuid(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('document_id', 'version_number')
    )
    op.create_index(op.f('ix_document_versions_created_by_id'), 'document_versions', ['created_by_id'], unique=False)
    op.create_index(op.f('ix_document_versions_document_id'), 'document_versions', ['document_id'], unique=False)
    op.create_index(op.f('ix_document_versions_institution_id'), 'document_versions', ['institution_id'], unique=False)
    op.create_table('enrollment_contracts',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('program_enrollment_id', sa.Uuid(), nullable=False),
    sa.Column('template_id', sa.Uuid(), nullable=True),
    sa.Column('term_id', sa.Uuid(), nullable=True),
    sa.Column('document_id', sa.Uuid(), nullable=True),
    sa.Column('kind', sa.Enum('enrollment', 'reenrollment', name='contractkind'), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('status', sa.Enum('pending', 'signed', 'cancelled', name='contractstatus'), nullable=False),
    sa.Column('validation_code', sa.String(length=40), nullable=False),
    sa.Column('signer_id', sa.Uuid(), nullable=True),
    sa.Column('signed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('signature_hash', sa.String(length=128), nullable=True),
    sa.Column('created_by_id', sa.Uuid(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['program_enrollment_id'], ['program_enrollments.id'], ),
    sa.ForeignKeyConstraint(['signer_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['template_id'], ['contract_templates.id'], ),
    sa.ForeignKeyConstraint(['term_id'], ['academic_terms.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_enrollment_contracts_document_id'), 'enrollment_contracts', ['document_id'], unique=False)
    op.create_index(op.f('ix_enrollment_contracts_institution_id'), 'enrollment_contracts', ['institution_id'], unique=False)
    op.create_index(op.f('ix_enrollment_contracts_program_enrollment_id'), 'enrollment_contracts', ['program_enrollment_id'], unique=False)
    op.create_index(op.f('ix_enrollment_contracts_template_id'), 'enrollment_contracts', ['template_id'], unique=False)
    op.create_index(op.f('ix_enrollment_contracts_term_id'), 'enrollment_contracts', ['term_id'], unique=False)
    op.create_index(op.f('ix_enrollment_contracts_validation_code'), 'enrollment_contracts', ['validation_code'], unique=True)
    op.create_table('grade_entries',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('assessment_item_id', sa.Uuid(), nullable=False),
    sa.Column('class_enrollment_id', sa.Uuid(), nullable=False),
    sa.Column('score', sa.Float(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('graded_by_id', sa.Uuid(), nullable=True),
    sa.Column('graded_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['assessment_item_id'], ['assessment_items.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['class_enrollment_id'], ['class_enrollments.id'], ),
    sa.ForeignKeyConstraint(['graded_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('assessment_item_id', 'class_enrollment_id')
    )
    op.create_index(op.f('ix_grade_entries_assessment_item_id'), 'grade_entries', ['assessment_item_id'], unique=False)
    op.create_index(op.f('ix_grade_entries_class_enrollment_id'), 'grade_entries', ['class_enrollment_id'], unique=False)
    op.create_index(op.f('ix_grade_entries_institution_id'), 'grade_entries', ['institution_id'], unique=False)
    op.create_table('internship_logs',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('internship_id', sa.Uuid(), nullable=False),
    sa.Column('worked_on', sa.Date(), nullable=False),
    sa.Column('hours', sa.Integer(), nullable=False),
    sa.Column('activities', sa.Text(), nullable=False),
    sa.Column('status', sa.Enum('submitted', 'approved', 'rejected', name='reviewstatus'), nullable=False),
    sa.Column('reviewed_by_id', sa.Uuid(), nullable=True),
    sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['internship_id'], ['internships.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['reviewed_by_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_internship_logs_institution_id'), 'internship_logs', ['institution_id'], unique=False)
    op.create_index(op.f('ix_internship_logs_internship_id'), 'internship_logs', ['internship_id'], unique=False)
    op.create_table('material_request_lines',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('request_id', sa.Uuid(), nullable=False),
    sa.Column('item_id', sa.Uuid(), nullable=False),
    sa.Column('quantity_requested', sa.Integer(), nullable=False),
    sa.Column('quantity_approved', sa.Integer(), nullable=True),
    sa.Column('quantity_delivered', sa.Integer(), nullable=False),
    sa.Column('quantity_returned', sa.Integer(), nullable=False),
    sa.Column('quantity_lost', sa.Integer(), nullable=False),
    sa.Column('unit_cost_cents', sa.Integer(), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['item_id'], ['warehouse_items.id'], ),
    sa.ForeignKeyConstraint(['request_id'], ['material_requests.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_material_request_lines_institution_id'), 'material_request_lines', ['institution_id'], unique=False)
    op.create_index(op.f('ix_material_request_lines_item_id'), 'material_request_lines', ['item_id'], unique=False)
    op.create_index(op.f('ix_material_request_lines_request_id'), 'material_request_lines', ['request_id'], unique=False)
    op.create_table('notification_events',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('event_type', sa.Enum('class_created', 'meeting_created', 'meeting_reminder', 'absence_registered', 'attendance_recorded', 'content_published', 'certificate_issued', 'grades_published', 'occurrence_registered', 'agenda_published', 'waitlist_promoted', 'activity_reviewed', 'admission_called', 'absence_dismissal', 'material_request_decided', name='notificationeventtype'), nullable=False),
    sa.Column('channel', sa.Enum('internal', 'whatsapp', 'email', 'push', name='notificationchannel'), nullable=False),
    sa.Column('template_key', sa.String(length=120), nullable=True),
    sa.Column('recipient_student_id', sa.Uuid(), nullable=True),
    sa.Column('course_id', sa.Uuid(), nullable=True),
    sa.Column('class_offering_id', sa.Uuid(), nullable=True),
    sa.Column('scheduled_meeting_id', sa.Uuid(), nullable=True),
    sa.Column('payload', sa.JSON(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('status', sa.Enum('pending', 'sent', 'failed', name='notificationstatus'), nullable=False),
    sa.Column('scheduled_for', sa.DateTime(timezone=True), nullable=True),
    sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['class_offering_id'], ['class_offerings.id'], ),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['recipient_student_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['scheduled_meeting_id'], ['scheduled_meetings.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_events_class_offering_id'), 'notification_events', ['class_offering_id'], unique=False)
    op.create_index(op.f('ix_notification_events_course_id'), 'notification_events', ['course_id'], unique=False)
    op.create_index(op.f('ix_notification_events_event_type'), 'notification_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_notification_events_institution_id'), 'notification_events', ['institution_id'], unique=False)
    op.create_index(op.f('ix_notification_events_recipient_student_id'), 'notification_events', ['recipient_student_id'], unique=False)
    op.create_index(op.f('ix_notification_events_scheduled_meeting_id'), 'notification_events', ['scheduled_meeting_id'], unique=False)
    op.create_index(op.f('ix_notification_events_template_key'), 'notification_events', ['template_key'], unique=False)
    op.create_table('period_results',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('class_offering_id', sa.Uuid(), nullable=False),
    sa.Column('class_enrollment_id', sa.Uuid(), nullable=False),
    sa.Column('grading_period_id', sa.Uuid(), nullable=False),
    sa.Column('average', sa.Float(), nullable=True),
    sa.Column('absences', sa.Integer(), nullable=False),
    sa.Column('closed_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['class_enrollment_id'], ['class_enrollments.id'], ),
    sa.ForeignKeyConstraint(['class_offering_id'], ['class_offerings.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['grading_period_id'], ['grading_periods.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('class_enrollment_id', 'grading_period_id')
    )
    op.create_index(op.f('ix_period_results_class_enrollment_id'), 'period_results', ['class_enrollment_id'], unique=False)
    op.create_index(op.f('ix_period_results_class_offering_id'), 'period_results', ['class_offering_id'], unique=False)
    op.create_index(op.f('ix_period_results_grading_period_id'), 'period_results', ['grading_period_id'], unique=False)
    op.create_index(op.f('ix_period_results_institution_id'), 'period_results', ['institution_id'], unique=False)
    op.create_table('practical_assessment_records',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('scheduled_meeting_id', sa.Uuid(), nullable=False),
    sa.Column('class_offering_id', sa.Uuid(), nullable=False),
    sa.Column('student_id', sa.Uuid(), nullable=False),
    sa.Column('score', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('reviewed', 'returned', name='practicalassessmentstatus'), nullable=False),
    sa.Column('feedback', sa.Text(), nullable=True),
    sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('recorded_by_id', sa.Uuid(), nullable=True),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['class_offering_id'], ['class_offerings.id'], ),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['recorded_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['scheduled_meeting_id'], ['scheduled_meetings.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('scheduled_meeting_id', 'student_id')
    )
    op.create_index(op.f('ix_practical_assessment_records_class_offering_id'), 'practical_assessment_records', ['class_offering_id'], unique=False)
    op.create_index(op.f('ix_practical_assessment_records_institution_id'), 'practical_assessment_records', ['institution_id'], unique=False)
    op.create_index(op.f('ix_practical_assessment_records_recorded_by_id'), 'practical_assessment_records', ['recorded_by_id'], unique=False)
    op.create_index(op.f('ix_practical_assessment_records_scheduled_meeting_id'), 'practical_assessment_records', ['scheduled_meeting_id'], unique=False)
    op.create_index(op.f('ix_practical_assessment_records_student_id'), 'practical_assessment_records', ['student_id'], unique=False)
    op.create_table('application_documents',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('application_id', sa.Uuid(), nullable=False),
    sa.Column('kind', sa.String(length=120), nullable=False),
    sa.Column('file_name', sa.String(length=255), nullable=False),
    sa.Column('mime_type', sa.String(length=120), nullable=True),
    sa.Column('storage_path', sa.String(length=500), nullable=False),
    sa.Column('review', sa.Enum('pending', 'accepted', 'rejected', name='documentreview'), nullable=False),
    sa.Column('review_note', sa.Text(), nullable=True),
    sa.Column('reviewed_by_id', sa.Uuid(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['application_id'], ['admission_applications.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.ForeignKeyConstraint(['reviewed_by_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_application_documents_application_id'), 'application_documents', ['application_id'], unique=False)
    op.create_index(op.f('ix_application_documents_institution_id'), 'application_documents', ['institution_id'], unique=False)
    op.create_table('diary_attendance',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('diary_entry_id', sa.Uuid(), nullable=False),
    sa.Column('class_enrollment_id', sa.Uuid(), nullable=False),
    sa.Column('absences', sa.Integer(), nullable=False),
    sa.Column('justified', sa.Boolean(), nullable=False),
    sa.Column('note', sa.String(length=300), nullable=True),
    sa.Column('institution_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['class_enrollment_id'], ['class_enrollments.id'], ),
    sa.ForeignKeyConstraint(['diary_entry_id'], ['class_diary_entries.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('diary_entry_id', 'class_enrollment_id')
    )
    op.create_index(op.f('ix_diary_attendance_class_enrollment_id'), 'diary_attendance', ['class_enrollment_id'], unique=False)
    op.create_index(op.f('ix_diary_attendance_diary_entry_id'), 'diary_attendance', ['diary_entry_id'], unique=False)
    op.create_index(op.f('ix_diary_attendance_institution_id'), 'diary_attendance', ['institution_id'], unique=False)
    # ### end Alembic commands ###

    _seed(institutions, minimum_wages)
    if _is_postgres():
        _enable_row_level_security()


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_diary_attendance_institution_id'), table_name='diary_attendance')
    op.drop_index(op.f('ix_diary_attendance_diary_entry_id'), table_name='diary_attendance')
    op.drop_index(op.f('ix_diary_attendance_class_enrollment_id'), table_name='diary_attendance')
    op.drop_table('diary_attendance')
    op.drop_index(op.f('ix_application_documents_institution_id'), table_name='application_documents')
    op.drop_index(op.f('ix_application_documents_application_id'), table_name='application_documents')
    op.drop_table('application_documents')
    op.drop_index(op.f('ix_practical_assessment_records_student_id'), table_name='practical_assessment_records')
    op.drop_index(op.f('ix_practical_assessment_records_scheduled_meeting_id'), table_name='practical_assessment_records')
    op.drop_index(op.f('ix_practical_assessment_records_recorded_by_id'), table_name='practical_assessment_records')
    op.drop_index(op.f('ix_practical_assessment_records_institution_id'), table_name='practical_assessment_records')
    op.drop_index(op.f('ix_practical_assessment_records_class_offering_id'), table_name='practical_assessment_records')
    op.drop_table('practical_assessment_records')
    op.drop_index(op.f('ix_period_results_institution_id'), table_name='period_results')
    op.drop_index(op.f('ix_period_results_grading_period_id'), table_name='period_results')
    op.drop_index(op.f('ix_period_results_class_offering_id'), table_name='period_results')
    op.drop_index(op.f('ix_period_results_class_enrollment_id'), table_name='period_results')
    op.drop_table('period_results')
    op.drop_index(op.f('ix_notification_events_template_key'), table_name='notification_events')
    op.drop_index(op.f('ix_notification_events_scheduled_meeting_id'), table_name='notification_events')
    op.drop_index(op.f('ix_notification_events_recipient_student_id'), table_name='notification_events')
    op.drop_index(op.f('ix_notification_events_institution_id'), table_name='notification_events')
    op.drop_index(op.f('ix_notification_events_event_type'), table_name='notification_events')
    op.drop_index(op.f('ix_notification_events_course_id'), table_name='notification_events')
    op.drop_index(op.f('ix_notification_events_class_offering_id'), table_name='notification_events')
    op.drop_table('notification_events')
    op.drop_index(op.f('ix_material_request_lines_request_id'), table_name='material_request_lines')
    op.drop_index(op.f('ix_material_request_lines_item_id'), table_name='material_request_lines')
    op.drop_index(op.f('ix_material_request_lines_institution_id'), table_name='material_request_lines')
    op.drop_table('material_request_lines')
    op.drop_index(op.f('ix_internship_logs_internship_id'), table_name='internship_logs')
    op.drop_index(op.f('ix_internship_logs_institution_id'), table_name='internship_logs')
    op.drop_table('internship_logs')
    op.drop_index(op.f('ix_grade_entries_institution_id'), table_name='grade_entries')
    op.drop_index(op.f('ix_grade_entries_class_enrollment_id'), table_name='grade_entries')
    op.drop_index(op.f('ix_grade_entries_assessment_item_id'), table_name='grade_entries')
    op.drop_table('grade_entries')
    op.drop_index(op.f('ix_enrollment_contracts_validation_code'), table_name='enrollment_contracts')
    op.drop_index(op.f('ix_enrollment_contracts_term_id'), table_name='enrollment_contracts')
    op.drop_index(op.f('ix_enrollment_contracts_template_id'), table_name='enrollment_contracts')
    op.drop_index(op.f('ix_enrollment_contracts_program_enrollment_id'), table_name='enrollment_contracts')
    op.drop_index(op.f('ix_enrollment_contracts_institution_id'), table_name='enrollment_contracts')
    op.drop_index(op.f('ix_enrollment_contracts_document_id'), table_name='enrollment_contracts')
    op.drop_table('enrollment_contracts')
    op.drop_index(op.f('ix_document_versions_institution_id'), table_name='document_versions')
    op.drop_index(op.f('ix_document_versions_document_id'), table_name='document_versions')
    op.drop_index(op.f('ix_document_versions_created_by_id'), table_name='document_versions')
    op.drop_table('document_versions')
    op.drop_index(op.f('ix_class_diary_entries_scheduled_meeting_id'), table_name='class_diary_entries')
    op.drop_index(op.f('ix_class_diary_entries_instructor_id'), table_name='class_diary_entries')
    op.drop_index(op.f('ix_class_diary_entries_institution_id'), table_name='class_diary_entries')
    op.drop_index(op.f('ix_class_diary_entries_class_offering_id'), table_name='class_diary_entries')
    op.drop_table('class_diary_entries')
    op.drop_index(op.f('ix_checkin_tokens_token'), table_name='checkin_tokens')
    op.drop_index(op.f('ix_checkin_tokens_scheduled_meeting_id'), table_name='checkin_tokens')
    op.drop_index(op.f('ix_checkin_tokens_institution_id'), table_name='checkin_tokens')
    op.drop_table('checkin_tokens')
    op.drop_index(op.f('ix_benefit_deliveries_student_id'), table_name='benefit_deliveries')
    op.drop_index(op.f('ix_benefit_deliveries_scheduled_meeting_id'), table_name='benefit_deliveries')
    op.drop_index(op.f('ix_benefit_deliveries_item_id'), table_name='benefit_deliveries')
    op.drop_index(op.f('ix_benefit_deliveries_institution_id'), table_name='benefit_deliveries')
    op.drop_index(op.f('ix_benefit_deliveries_class_offering_id'), table_name='benefit_deliveries')
    op.drop_table('benefit_deliveries')
    op.drop_index(op.f('ix_attendance_records_student_id'), table_name='attendance_records')
    op.drop_index(op.f('ix_attendance_records_scheduled_meeting_id'), table_name='attendance_records')
    op.drop_index(op.f('ix_attendance_records_institution_id'), table_name='attendance_records')
    op.drop_index(op.f('ix_attendance_records_class_offering_id'), table_name='attendance_records')
    op.drop_table('attendance_records')
    op.drop_index(op.f('ix_admission_applications_protocol'), table_name='admission_applications')
    op.drop_index(op.f('ix_admission_applications_institution_id'), table_name='admission_applications')
    op.drop_index(op.f('ix_admission_applications_call_id'), table_name='admission_applications')
    op.drop_index(op.f('ix_admission_applications_applicant_id'), table_name='admission_applications')
    op.drop_table('admission_applications')
    op.drop_index(op.f('ix_waitlist_entries_student_id'), table_name='waitlist_entries')
    op.drop_index(op.f('ix_waitlist_entries_institution_id'), table_name='waitlist_entries')
    op.drop_index(op.f('ix_waitlist_entries_class_offering_id'), table_name='waitlist_entries')
    op.drop_table('waitlist_entries')
    op.drop_index(op.f('ix_term_registrations_term_id'), table_name='term_registrations')
    op.drop_index(op.f('ix_term_registrations_program_enrollment_id'), table_name='term_registrations')
    op.drop_index(op.f('ix_term_registrations_institution_id'), table_name='term_registrations')
    op.drop_table('term_registrations')
    op.drop_index(op.f('ix_student_discounts_program_enrollment_id'), table_name='student_discounts')
    op.drop_index(op.f('ix_student_discounts_institution_id'), table_name='student_discounts')
    op.drop_table('student_discounts')
    op.drop_index(op.f('ix_scheduled_meetings_room_id'), table_name='scheduled_meetings')
    op.drop_index(op.f('ix_scheduled_meetings_lesson_id'), table_name='scheduled_meetings')
    op.drop_index(op.f('ix_scheduled_meetings_institution_id'), table_name='scheduled_meetings')
    op.drop_index(op.f('ix_scheduled_meetings_class_offering_id'), table_name='scheduled_meetings')
    op.drop_table('scheduled_meetings')
    op.drop_index(op.f('ix_quiz_questions_quiz_id'), table_name='quiz_questions')
    op.drop_index(op.f('ix_quiz_questions_institution_id'), table_name='quiz_questions')
    op.drop_table('quiz_questions')
    op.drop_index(op.f('ix_quiz_attempts_student_id'), table_name='quiz_attempts')
    op.drop_index(op.f('ix_quiz_attempts_quiz_id'), table_name='quiz_attempts')
    op.drop_index(op.f('ix_quiz_attempts_institution_id'), table_name='quiz_attempts')
    op.drop_table('quiz_attempts')
    op.drop_index(op.f('ix_program_enrollment_events_term_id'), table_name='program_enrollment_events')
    op.drop_index(op.f('ix_program_enrollment_events_program_enrollment_id'), table_name='program_enrollment_events')
    op.drop_index(op.f('ix_program_enrollment_events_institution_id'), table_name='program_enrollment_events')
    op.drop_table('program_enrollment_events')
    op.drop_index(op.f('ix_offering_time_slots_institution_id'), table_name='offering_time_slots')
    op.drop_index(op.f('ix_offering_time_slots_class_offering_id'), table_name='offering_time_slots')
    op.drop_table('offering_time_slots')
    op.drop_index(op.f('ix_offering_period_closures_institution_id'), table_name='offering_period_closures')
    op.drop_index(op.f('ix_offering_period_closures_grading_period_id'), table_name='offering_period_closures')
    op.drop_index(op.f('ix_offering_period_closures_class_offering_id'), table_name='offering_period_closures')
    op.drop_table('offering_period_closures')
    op.drop_index(op.f('ix_material_requests_requester_id'), table_name='material_requests')
    op.drop_index(op.f('ix_material_requests_institution_id'), table_name='material_requests')
    op.drop_index(op.f('ix_material_requests_class_offering_id'), table_name='material_requests')
    op.drop_table('material_requests')
    op.drop_index(op.f('ix_internships_program_enrollment_id'), table_name='internships')
    op.drop_index(op.f('ix_internships_institution_id'), table_name='internships')
    op.drop_index(op.f('ix_internships_advisor_id'), table_name='internships')
    op.drop_table('internships')
    op.drop_index(op.f('ix_final_projects_program_enrollment_id'), table_name='final_projects')
    op.drop_index(op.f('ix_final_projects_institution_id'), table_name='final_projects')
    op.drop_index(op.f('ix_final_projects_advisor_id'), table_name='final_projects')
    op.drop_table('final_projects')
    op.drop_index(op.f('ix_documents_uploaded_by_id'), table_name='documents')
    op.drop_index(op.f('ix_documents_title'), table_name='documents')
    op.drop_index(op.f('ix_documents_student_id'), table_name='documents')
    op.drop_index(op.f('ix_documents_organization_id'), table_name='documents')
    op.drop_index(op.f('ix_documents_institution_id'), table_name='documents')
    op.drop_index(op.f('ix_documents_course_id'), table_name='documents')
    op.drop_index(op.f('ix_documents_class_offering_id'), table_name='documents')
    op.drop_table('documents')
    op.drop_index(op.f('ix_credit_transfers_subject_id'), table_name='credit_transfers')
    op.drop_index(op.f('ix_credit_transfers_program_enrollment_id'), table_name='credit_transfers')
    op.drop_index(op.f('ix_credit_transfers_institution_id'), table_name='credit_transfers')
    op.drop_table('credit_transfers')
    op.drop_index(op.f('ix_complementary_activities_program_enrollment_id'), table_name='complementary_activities')
    op.drop_index(op.f('ix_complementary_activities_institution_id'), table_name='complementary_activities')
    op.drop_table('complementary_activities')
    op.drop_index(op.f('ix_class_group_members_program_enrollment_id'), table_name='class_group_members')
    op.drop_index(op.f('ix_class_group_members_institution_id'), table_name='class_group_members')
    op.drop_index(op.f('ix_class_group_members_class_group_id'), table_name='class_group_members')
    op.drop_table('class_group_members')
    op.drop_index(op.f('ix_class_enrollments_student_id'), table_name='class_enrollments')
    op.drop_index(op.f('ix_class_enrollments_institution_id'), table_name='class_enrollments')
    op.drop_index(op.f('ix_class_enrollments_class_offering_id'), table_name='class_enrollments')
    op.drop_table('class_enrollments')
    op.drop_index(op.f('ix_charges_tuition_plan_id'), table_name='charges')
    op.drop_index(op.f('ix_charges_subscription_id'), table_name='charges')
    op.drop_index(op.f('ix_charges_student_id'), table_name='charges')
    op.drop_index(op.f('ix_charges_program_enrollment_id'), table_name='charges')
    op.drop_index(op.f('ix_charges_payer_id'), table_name='charges')
    op.drop_index(op.f('ix_charges_organization_id'), table_name='charges')
    op.drop_index(op.f('ix_charges_institution_id'), table_name='charges')
    op.drop_index(op.f('ix_charges_gateway_reference'), table_name='charges')
    op.drop_index(op.f('ix_charges_course_id'), table_name='charges')
    op.drop_index(op.f('ix_charges_class_offering_id'), table_name='charges')
    op.drop_index(op.f('ix_charges_billing_plan_id'), table_name='charges')
    op.drop_table('charges')
    op.drop_index(op.f('ix_attendance_student_id'), table_name='attendance')
    op.drop_index(op.f('ix_attendance_lesson_id'), table_name='attendance')
    op.drop_index(op.f('ix_attendance_institution_id'), table_name='attendance')
    op.drop_table('attendance')
    op.drop_index(op.f('ix_assessment_items_quiz_id'), table_name='assessment_items')
    op.drop_index(op.f('ix_assessment_items_institution_id'), table_name='assessment_items')
    op.drop_index(op.f('ix_assessment_items_grading_period_id'), table_name='assessment_items')
    op.drop_index(op.f('ix_assessment_items_class_offering_id'), table_name='assessment_items')
    op.drop_table('assessment_items')
    op.drop_index(op.f('ix_agenda_items_institution_id'), table_name='agenda_items')
    op.drop_index(op.f('ix_agenda_items_due_on'), table_name='agenda_items')
    op.drop_index(op.f('ix_agenda_items_class_offering_id'), table_name='agenda_items')
    op.drop_index(op.f('ix_agenda_items_class_group_id'), table_name='agenda_items')
    op.drop_table('agenda_items')
    op.drop_index(op.f('ix_admission_calls_institution_id'), table_name='admission_calls')
    op.drop_index(op.f('ix_admission_calls_class_offering_id'), table_name='admission_calls')
    op.drop_table('admission_calls')
    op.drop_index(op.f('ix_academic_declarations_validation_code'), table_name='academic_declarations')
    op.drop_index(op.f('ix_academic_declarations_program_enrollment_id'), table_name='academic_declarations')
    op.drop_index(op.f('ix_academic_declarations_institution_id'), table_name='academic_declarations')
    op.drop_table('academic_declarations')
    op.drop_index(op.f('ix_tuition_plans_term_id'), table_name='tuition_plans')
    op.drop_index(op.f('ix_tuition_plans_program_id'), table_name='tuition_plans')
    op.drop_index(op.f('ix_tuition_plans_institution_id'), table_name='tuition_plans')
    op.drop_index(op.f('ix_tuition_plans_class_group_id'), table_name='tuition_plans')
    op.drop_table('tuition_plans')
    op.drop_index(op.f('ix_student_occurrences_student_id'), table_name='student_occurrences')
    op.drop_index(op.f('ix_student_occurrences_occurred_on'), table_name='student_occurrences')
    op.drop_index(op.f('ix_student_occurrences_institution_id'), table_name='student_occurrences')
    op.drop_index(op.f('ix_student_occurrences_class_group_id'), table_name='student_occurrences')
    op.drop_table('student_occurrences')
    op.drop_index(op.f('ix_sessions_student_id'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_lesson_id'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_institution_id'), table_name='sessions')
    op.drop_index(op.f('ix_sessions_bevox_session_id'), table_name='sessions')
    op.drop_table('sessions')
    op.drop_index(op.f('ix_quizzes_lesson_id'), table_name='quizzes')
    op.drop_index(op.f('ix_quizzes_institution_id'), table_name='quizzes')
    op.drop_table('quizzes')
    op.drop_index(op.f('ix_progress_student_id'), table_name='progress')
    op.drop_index(op.f('ix_progress_lesson_id'), table_name='progress')
    op.drop_index(op.f('ix_progress_institution_id'), table_name='progress')
    op.drop_table('progress')
    op.drop_index(op.f('ix_program_enrollments_transferred_from_id'), table_name='program_enrollments')
    op.drop_index(op.f('ix_program_enrollments_student_id'), table_name='program_enrollments')
    op.drop_index(op.f('ix_program_enrollments_program_id'), table_name='program_enrollments')
    op.drop_index(op.f('ix_program_enrollments_institution_id'), table_name='program_enrollments')
    op.drop_index(op.f('ix_program_enrollments_entry_term_id'), table_name='program_enrollments')
    op.drop_index(op.f('ix_program_enrollments_curriculum_id'), table_name='program_enrollments')
    op.drop_table('program_enrollments')
    op.drop_index(op.f('ix_instructor_ratings_student_id'), table_name='instructor_ratings')
    op.drop_index(op.f('ix_instructor_ratings_instructor_profile_id'), table_name='instructor_ratings')
    op.drop_table('instructor_ratings')
    op.drop_index(op.f('ix_instructor_availability_instructor_profile_id'), table_name='instructor_availability')
    op.drop_table('instructor_availability')
    op.drop_index(op.f('ix_forum_posts_thread_id'), table_name='forum_posts')
    op.drop_index(op.f('ix_forum_posts_institution_id'), table_name='forum_posts')
    op.drop_index(op.f('ix_forum_posts_author_id'), table_name='forum_posts')
    op.drop_table('forum_posts')
    op.drop_index(op.f('ix_curriculum_components_subject_id'), table_name='curriculum_components')
    op.drop_index(op.f('ix_curriculum_components_institution_id'), table_name='curriculum_components')
    op.drop_index(op.f('ix_curriculum_components_curriculum_id'), table_name='curriculum_components')
    op.drop_table('curriculum_components')
    op.drop_index(op.f('ix_class_offerings_term_id'), table_name='class_offerings')
    op.drop_index(op.f('ix_class_offerings_subject_id'), table_name='class_offerings')
    op.drop_index(op.f('ix_class_offerings_room_id'), table_name='class_offerings')
    op.drop_index(op.f('ix_class_offerings_location_id'), table_name='class_offerings')
    op.drop_index(op.f('ix_class_offerings_instructor_id'), table_name='class_offerings')
    op.drop_index(op.f('ix_class_offerings_institution_id'), table_name='class_offerings')
    op.drop_index(op.f('ix_class_offerings_grading_scheme_id'), table_name='class_offerings')
    op.drop_index(op.f('ix_class_offerings_funding_source_id'), table_name='class_offerings')
    op.drop_index(op.f('ix_class_offerings_course_id'), table_name='class_offerings')
    op.drop_index(op.f('ix_class_offerings_class_group_id'), table_name='class_offerings')
    op.drop_table('class_offerings')
    op.drop_index(op.f('ix_chat_messages_sender_id'), table_name='chat_messages')
    op.drop_index(op.f('ix_chat_messages_institution_id'), table_name='chat_messages')
    op.drop_index(op.f('ix_chat_messages_conversation_id'), table_name='chat_messages')
    op.drop_table('chat_messages')
    op.drop_index(op.f('ix_assignment_submissions_student_id'), table_name='assignment_submissions')
    op.drop_index(op.f('ix_assignment_submissions_reviewed_by_id'), table_name='assignment_submissions')
    op.drop_index(op.f('ix_assignment_submissions_lesson_id'), table_name='assignment_submissions')
    op.drop_index(op.f('ix_assignment_submissions_institution_id'), table_name='assignment_submissions')
    op.drop_index(op.f('ix_assignment_submissions_course_id'), table_name='assignment_submissions')
    op.drop_table('assignment_submissions')
    op.drop_index(op.f('ix_warehouse_entries_item_id'), table_name='warehouse_entries')
    op.drop_index(op.f('ix_warehouse_entries_institution_id'), table_name='warehouse_entries')
    op.drop_index(op.f('ix_warehouse_entries_funding_source_id'), table_name='warehouse_entries')
    op.drop_table('warehouse_entries')
    op.drop_index(op.f('ix_subscriptions_student_id'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_organization_id'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_institution_id'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_billing_plan_id'), table_name='subscriptions')
    op.drop_table('subscriptions')
    op.drop_index(op.f('ix_subject_prerequisites_subject_id'), table_name='subject_prerequisites')
    op.drop_index(op.f('ix_subject_prerequisites_required_subject_id'), table_name='subject_prerequisites')
    op.drop_index(op.f('ix_subject_prerequisites_institution_id'), table_name='subject_prerequisites')
    op.drop_table('subject_prerequisites')
    op.drop_index(op.f('ix_subject_equivalences_subject_id'), table_name='subject_equivalences')
    op.drop_index(op.f('ix_subject_equivalences_institution_id'), table_name='subject_equivalences')
    op.drop_index(op.f('ix_subject_equivalences_equivalent_subject_id'), table_name='subject_equivalences')
    op.drop_table('subject_equivalences')
    op.drop_index(op.f('ix_student_profiles_student_id'), table_name='student_profiles')
    op.drop_index(op.f('ix_student_profiles_document'), table_name='student_profiles')
    op.drop_table('student_profiles')
    op.drop_index(op.f('ix_student_guardians_student_id'), table_name='student_guardians')
    op.drop_index(op.f('ix_student_guardians_institution_id'), table_name='student_guardians')
    op.drop_index(op.f('ix_student_guardians_guardian_id'), table_name='student_guardians')
    op.drop_table('student_guardians')
    op.drop_index(op.f('ix_rooms_location_id'), table_name='rooms')
    op.drop_index(op.f('ix_rooms_institution_id'), table_name='rooms')
    op.drop_table('rooms')
    op.drop_index(op.f('ix_registration_windows_term_id'), table_name='registration_windows')
    op.drop_index(op.f('ix_registration_windows_program_id'), table_name='registration_windows')
    op.drop_index(op.f('ix_registration_windows_institution_id'), table_name='registration_windows')
    op.drop_table('registration_windows')
    op.drop_index(op.f('ix_lessons_module_id'), table_name='lessons')
    op.drop_index(op.f('ix_lessons_institution_id'), table_name='lessons')
    op.drop_index(op.f('ix_lessons_course_id'), table_name='lessons')
    op.drop_table('lessons')
    op.drop_index(op.f('ix_instructor_profiles_student_id'), table_name='instructor_profiles')
    op.drop_table('instructor_profiles')
    op.drop_index(op.f('ix_institution_memberships_user_id'), table_name='institution_memberships')
    op.drop_index(op.f('ix_institution_member_roles_membership_id'), table_name='institution_member_roles')
    op.drop_table('institution_member_roles')
    op.drop_index(op.f('ix_institution_memberships_institution_id'), table_name='institution_memberships')
    op.drop_table('institution_memberships')
    op.drop_index(op.f('ix_forum_threads_institution_id'), table_name='forum_threads')
    op.drop_index(op.f('ix_forum_threads_course_id'), table_name='forum_threads')
    op.drop_index(op.f('ix_forum_threads_author_id'), table_name='forum_threads')
    op.drop_table('forum_threads')
    op.drop_index(op.f('ix_enrollments_student_id'), table_name='enrollments')
    op.drop_index(op.f('ix_enrollments_institution_id'), table_name='enrollments')
    op.drop_index(op.f('ix_enrollments_course_id'), table_name='enrollments')
    op.drop_table('enrollments')
    op.drop_index(op.f('ix_curricula_program_id'), table_name='curricula')
    op.drop_index(op.f('ix_curricula_institution_id'), table_name='curricula')
    op.drop_table('curricula')
    op.drop_index(op.f('ix_class_groups_term_id'), table_name='class_groups')
    op.drop_index(op.f('ix_class_groups_program_id'), table_name='class_groups')
    op.drop_index(op.f('ix_class_groups_institution_id'), table_name='class_groups')
    op.drop_index(op.f('ix_class_groups_homeroom_teacher_id'), table_name='class_groups')
    op.drop_table('class_groups')
    op.drop_index(op.f('ix_chat_conversations_student_id'), table_name='chat_conversations')
    op.drop_index(op.f('ix_chat_conversations_instructor_id'), table_name='chat_conversations')
    op.drop_index(op.f('ix_chat_conversations_institution_id'), table_name='chat_conversations')
    op.drop_index(op.f('ix_chat_conversations_course_id'), table_name='chat_conversations')
    op.drop_table('chat_conversations')
    op.drop_index(op.f('ix_certificates_validation_code'), table_name='certificates')
    op.drop_index(op.f('ix_certificates_student_id'), table_name='certificates')
    op.drop_index(op.f('ix_certificates_issued_by_id'), table_name='certificates')
    op.drop_index(op.f('ix_certificates_institution_id'), table_name='certificates')
    op.drop_index(op.f('ix_certificates_course_id'), table_name='certificates')
    op.drop_table('certificates')
    op.drop_index(op.f('ix_benefit_stock_entries_item_id'), table_name='benefit_stock_entries')
    op.drop_index(op.f('ix_benefit_stock_entries_institution_id'), table_name='benefit_stock_entries')
    op.drop_index(op.f('ix_benefit_stock_entries_funding_source_id'), table_name='benefit_stock_entries')
    op.drop_table('benefit_stock_entries')
    op.drop_index(op.f('ix_access_role_assignments_user_id'), table_name='access_role_assignments')
    op.drop_index(op.f('ix_access_role_assignments_role_id'), table_name='access_role_assignments')
    op.drop_index(op.f('ix_access_role_assignments_institution_id'), table_name='access_role_assignments')
    op.drop_table('access_role_assignments')
    op.drop_index(op.f('ix_users_organization_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_subjects_institution_id'), table_name='subjects')
    op.drop_index(op.f('ix_subjects_course_id'), table_name='subjects')
    op.drop_table('subjects')
    op.drop_index(op.f('ix_programs_unit_id'), table_name='programs')
    op.drop_index(op.f('ix_programs_institution_id'), table_name='programs')
    op.drop_table('programs')
    op.drop_index(op.f('ix_platform_invoices_subscription_id'), table_name='platform_invoices')
    op.drop_index(op.f('ix_platform_invoices_institution_id'), table_name='platform_invoices')
    op.drop_table('platform_invoices')
    op.drop_index(op.f('ix_locations_institution_id'), table_name='locations')
    op.drop_index(op.f('ix_locations_campus_id'), table_name='locations')
    op.drop_table('locations')
    op.drop_index(op.f('ix_learning_path_courses_learning_path_id'), table_name='learning_path_courses')
    op.drop_index(op.f('ix_learning_path_courses_institution_id'), table_name='learning_path_courses')
    op.drop_index(op.f('ix_learning_path_courses_course_id'), table_name='learning_path_courses')
    op.drop_table('learning_path_courses')
    op.drop_index(op.f('ix_grading_periods_term_id'), table_name='grading_periods')
    op.drop_index(op.f('ix_grading_periods_institution_id'), table_name='grading_periods')
    op.drop_table('grading_periods')
    op.drop_index(op.f('ix_course_prerequisites_prerequisite_course_id'), table_name='course_prerequisites')
    op.drop_index(op.f('ix_course_prerequisites_institution_id'), table_name='course_prerequisites')
    op.drop_index(op.f('ix_course_prerequisites_course_id'), table_name='course_prerequisites')
    op.drop_table('course_prerequisites')
    op.drop_index(op.f('ix_course_modules_institution_id'), table_name='course_modules')
    op.drop_index(op.f('ix_course_modules_course_id'), table_name='course_modules')
    op.drop_table('course_modules')
    op.drop_index(op.f('ix_course_completion_rules_institution_id'), table_name='course_completion_rules')
    op.drop_index(op.f('ix_course_completion_rules_course_id'), table_name='course_completion_rules')
    op.drop_table('course_completion_rules')
    op.drop_index(op.f('ix_calendar_events_term_id'), table_name='calendar_events')
    op.drop_index(op.f('ix_calendar_events_starts_on'), table_name='calendar_events')
    op.drop_index(op.f('ix_calendar_events_institution_id'), table_name='calendar_events')
    op.drop_table('calendar_events')
    op.drop_index(op.f('ix_warehouse_items_institution_id'), table_name='warehouse_items')
    op.drop_table('warehouse_items')
    op.drop_index(op.f('ix_organizations_name'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_institution_id'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_document'), table_name='organizations')
    op.drop_table('organizations')
    op.drop_index(op.f('ix_notification_templates_key'), table_name='notification_templates')
    op.drop_index(op.f('ix_notification_templates_institution_id'), table_name='notification_templates')
    op.drop_table('notification_templates')
    op.drop_index(op.f('ix_learning_paths_institution_id'), table_name='learning_paths')
    op.drop_table('learning_paths')
    op.drop_index(op.f('ix_institution_subscriptions_plan_id'), table_name='institution_subscriptions')
    op.drop_index(op.f('ix_institution_subscriptions_institution_id'), table_name='institution_subscriptions')
    op.drop_table('institution_subscriptions')
    op.drop_index(op.f('ix_grading_schemes_institution_id'), table_name='grading_schemes')
    op.drop_table('grading_schemes')
    op.drop_index(op.f('ix_funding_sources_institution_id'), table_name='funding_sources')
    op.drop_table('funding_sources')
    op.drop_index(op.f('ix_courses_institution_id'), table_name='courses')
    op.drop_table('courses')
    op.drop_index(op.f('ix_contract_templates_institution_id'), table_name='contract_templates')
    op.drop_table('contract_templates')
    op.drop_index(op.f('ix_campuses_institution_id'), table_name='campuses')
    op.drop_table('campuses')
    op.drop_index(op.f('ix_billing_plans_name'), table_name='billing_plans')
    op.drop_index(op.f('ix_billing_plans_institution_id'), table_name='billing_plans')
    op.drop_table('billing_plans')
    op.drop_index(op.f('ix_benefit_items_institution_id'), table_name='benefit_items')
    op.drop_table('benefit_items')
    op.drop_index(op.f('ix_access_roles_institution_id'), table_name='access_roles')
    op.drop_table('access_roles')
    op.drop_index(op.f('ix_academic_units_parent_id'), table_name='academic_units')
    op.drop_index(op.f('ix_academic_units_institution_id'), table_name='academic_units')
    op.drop_table('academic_units')
    op.drop_index(op.f('ix_academic_terms_institution_id'), table_name='academic_terms')
    op.drop_table('academic_terms')
    op.drop_table('saas_plans')
    op.drop_index(op.f('ix_minimum_wage_values_valid_from'), table_name='minimum_wage_values')
    op.drop_table('minimum_wage_values')
    op.drop_index(op.f('ix_institutions_slug'), table_name='institutions')
    op.drop_index(op.f('ix_institutions_document'), table_name='institutions')
    op.drop_table('institutions')
    # ### end Alembic commands ###
    if _is_postgres():
        for enum in ENUM_TYPES:
            op.execute(f"DROP TYPE IF EXISTS {enum}")
