"""Verify PostgreSQL Row Level Security as the second tenant barrier.

Needs a PostgreSQL superuser URL in RLS_ADMIN_DATABASE_URL (or DATABASE_URL) to
create a regular role and a scratch database owned by it, as in production.
Migrations run as that role, then raw SQL (bypassing the ORM filter) is checked
against the policies.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[1]
ADMIN_URL = make_url(os.environ.get("RLS_ADMIN_DATABASE_URL") or os.environ["DATABASE_URL"])
if ADMIN_URL.get_backend_name() != "postgresql":
    raise SystemExit("check_rls.py precisa de PostgreSQL.")

ROLE, ROLE_PASSWORD, DATABASE = "wedu_rls_check", "wedu_rls_check", "wedu_rls_check"
APP_URL = ADMIN_URL.set(username=ROLE, password=ROLE_PASSWORD, database=DATABASE)


def prepare_database() -> None:
    admin = create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {DATABASE} WITH (FORCE)"))
        exists = conn.execute(text("SELECT 1 FROM pg_roles WHERE rolname = :r"), {"r": ROLE}).first()
        if not exists:
            conn.execute(text(f"CREATE ROLE {ROLE} LOGIN PASSWORD '{ROLE_PASSWORD}' NOSUPERUSER NOBYPASSRLS"))
        conn.execute(text(f"CREATE DATABASE {DATABASE} OWNER {ROLE}"))
    admin.dispose()
    env = {**os.environ, "DATABASE_URL": APP_URL.render_as_string(hide_password=False)}
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=ROOT, env=env, check=True, capture_output=True)


prepare_database()
os.environ["DATABASE_URL"] = APP_URL.render_as_string(hide_password=False)
os.environ["NOTIFICATION_WORKER_ENABLED"] = "false"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import HTTPException  # noqa: E402
from sqlalchemy import select  # noqa: E402

import app.models  # noqa: E402,F401
from app.core.database import SessionLocal  # noqa: E402
from app.core.tenancy import UNSCOPED, bind_institution  # noqa: E402
from app.models.course import Course  # noqa: E402
from app.models.institution import Institution  # noqa: E402
from app.models.lesson import Lesson  # noqa: E402

failures: list[str] = []


def expect(condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def raw_course_names(db) -> list[str]:
    return sorted(row[0] for row in db.execute(text("SELECT name FROM courses")))


with SessionLocal() as db:
    a, b = Institution(slug="a", name="A"), Institution(slug="b", name="B")
    db.add_all([a, b])
    db.flush()
    ids = {"a": a.id, "b": b.id}
    for slug, name in (("a", "Curso A"), ("b", "Curso B")):
        bind_institution(db, ids[slug])
        db.add(Course(name=name))
        db.flush()
    db.commit()
    course_b_id = db.execute(text("SELECT id FROM courses WHERE name = 'Curso B'")).scalar_one()

with SessionLocal() as db:
    expect(raw_course_names(db) == ["Curso A", "Curso B"], "unbound session sees every institution")

    bind_institution(db, ids["a"])
    expect(raw_course_names(db) == ["Curso A"], f"raw SELECT limited to bound institution: {raw_course_names(db)}")
    updated = db.execute(text("UPDATE courses SET name = 'hack' WHERE name = 'Curso B'")).rowcount
    expect(updated == 0, f"raw UPDATE cannot touch other institution: {updated} rows")
    deleted = db.execute(text("DELETE FROM courses WHERE name = 'Curso B'")).rowcount
    expect(deleted == 0, f"raw DELETE cannot touch other institution: {deleted} rows")

    unscoped = sorted(db.execute(select(Course.name).execution_options(**UNSCOPED)).scalars())
    expect(unscoped == ["Curso A", "Curso B"], f"UNSCOPED query bypasses the policy: {unscoped}")
    expect(raw_course_names(db) == ["Curso A"], "policy restored after UNSCOPED query")

    db.commit()
    expect(raw_course_names(db) == ["Curso A"], "policy applied again in the next transaction")

    try:
        db.execute(text("INSERT INTO courses (name, modality, created_at, institution_id) VALUES ('x', 'online', now(), :b)"), {"b": ids["b"]})
        db.flush()
        failures.append("raw INSERT into other institution should violate the policy")
    except Exception as exc:  # psycopg2 InsufficientPrivilege wrapped by SQLAlchemy
        expect("row-level security" in str(exc), f"unexpected INSERT error: {exc}")
        db.rollback()

    bind_institution(db, ids["a"])
    db.add(Lesson(course_id=course_b_id, title="Intrusa"))
    try:
        db.flush()
        failures.append("ORM insert referencing other institution should be rejected")
    except HTTPException as exc:
        expect(exc.status_code == 404, f"cross-tenant reference rejected with 404: {exc.status_code}")
        db.rollback()

    bind_institution(db, None)
    expect(raw_course_names(db) == ["Curso A", "Curso B"], "unbinding clears the policy setting")

if failures:
    print("RLS check failed:")
    for failure in failures:
        print(f"- {failure}")
    raise SystemExit(1)
print("RLS check passed.")
