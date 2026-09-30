"""add institution_id to child tables

Revision ID: b1c2d3e4f5a6
Revises: a0b1c2d3e4f5
Create Date: 2026-09-30 00:00:01.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "b1c2d3e4f5a6"
down_revision = "a0b1c2d3e4f5"
branch_labels = None
depends_on = None


# Ordem importa: cada tabela herda a instituicao de pais ja preenchidos.
# Cada item: (tabela, [(coluna FK, tabela pai), ...]) tentados em sequencia.
CHILD_TABLES = [
    ("course_completion_rules", [("course_id", "courses")]),
    ("course_modules", [("course_id", "courses")]),
    ("course_prerequisites", [("course_id", "courses")]),
    ("learning_path_courses", [("learning_path_id", "learning_paths")]),
    ("lessons", [("course_id", "courses")]),
    ("rooms", [("location_id", "locations")]),
    ("enrollments", [("course_id", "courses")]),
    ("forum_threads", [("course_id", "courses")]),
    ("chat_conversations", [("course_id", "courses")]),
    ("assignment_submissions", [("course_id", "courses")]),
    ("subscriptions", [("billing_plan_id", "billing_plans")]),
    ("class_enrollments", [("class_offering_id", "class_offerings")]),
    ("waitlist_entries", [("class_offering_id", "class_offerings")]),
    ("scheduled_meetings", [("class_offering_id", "class_offerings")]),
    ("attendance_records", [("class_offering_id", "class_offerings")]),
    ("practical_assessment_records", [("class_offering_id", "class_offerings")]),
    ("quizzes", [("lesson_id", "lessons")]),
    ("progress", [("lesson_id", "lessons")]),
    ("sessions", [("lesson_id", "lessons")]),
    ("attendance", [("lesson_id", "lessons")]),
    ("quiz_questions", [("quiz_id", "quizzes")]),
    ("quiz_attempts", [("quiz_id", "quizzes")]),
    ("chat_messages", [("conversation_id", "chat_conversations")]),
    ("forum_posts", [("thread_id", "forum_threads")]),
    ("checkin_tokens", [("scheduled_meeting_id", "scheduled_meetings")]),
    ("document_versions", [("document_id", "documents")]),
    (
        "charges",
        [
            ("billing_plan_id", "billing_plans"),
            ("class_offering_id", "class_offerings"),
            ("course_id", "courses"),
            ("subscription_id", "subscriptions"),
            ("organization_id", "organizations"),
        ],
    ),
    (
        "notification_events",
        [
            ("course_id", "courses"),
            ("class_offering_id", "class_offerings"),
            ("scheduled_meeting_id", "scheduled_meetings"),
        ],
    ),
]


def upgrade() -> None:
    for table, parents in CHILD_TABLES:
        op.add_column(table, sa.Column("institution_id", sa.Integer(), nullable=True))
        for fk_column, parent in parents:
            op.execute(
                f"UPDATE {table} SET institution_id = p.institution_id FROM {parent} p "
                f"WHERE p.id = {table}.{fk_column} AND {table}.institution_id IS NULL"
            )
        if table == "notification_events":
            op.execute(
                "UPDATE notification_events SET institution_id = ("
                "SELECT MIN(m.institution_id) FROM institution_memberships m "
                "WHERE m.user_id = notification_events.recipient_student_id"
                ") WHERE institution_id IS NULL"
            )
        op.execute(
            f"UPDATE {table} SET institution_id = (SELECT id FROM institutions WHERE slug = 'default') "
            "WHERE institution_id IS NULL"
        )
        op.alter_column(table, "institution_id", nullable=False)
        op.create_foreign_key(f"fk_{table}_institution_id", table, "institutions", ["institution_id"], ["id"])
        op.create_index(op.f(f"ix_{table}_institution_id"), table, ["institution_id"], unique=False)


def downgrade() -> None:
    for table, _ in reversed(CHILD_TABLES):
        op.drop_index(op.f(f"ix_{table}_institution_id"), table_name=table)
        op.drop_constraint(f"fk_{table}_institution_id", table, type_="foreignkey")
        op.drop_column(table, "institution_id")
