"""Exercise the data versions behind the mobile cache: each write bumps its area, per institution.

Uses a temporary SQLite database by default (set DATABASE_URL to use PostgreSQL).
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
import sys

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_sync_check_{os.getpid()}.sqlite3"
    os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["NOTIFICATION_WORKER_ENABLED"] = "false"

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import anyio.to_thread
import fastapi.routing
import httpx
import starlette.concurrency
import starlette.routing

from scripts.check_support import ApiClient  # noqa: E402
import app.models  # noqa: F401
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.core.tenancy import bind_institution
from app.models.academic_groups import ClassGroup
from app.models.institution import Institution, InstitutionMembership
from app.models.notification import NotificationEvent, NotificationEventType
from app.models.student import Student, UserRole
from app.services.notifications.events import NotificationEventService
from main import app


async def run_in_threadpool_inline(func, *args, **kwargs):
    kwargs.pop("abandon_on_cancel", None)
    kwargs.pop("cancellable", None)
    kwargs.pop("limiter", None)
    return func(*args, **kwargs)


fastapi.routing.run_in_threadpool = run_in_threadpool_inline
starlette.concurrency.run_in_threadpool = run_in_threadpool_inline
starlette.routing.run_in_threadpool = run_in_threadpool_inline
anyio.to_thread.run_sync = run_in_threadpool_inline

PASSWORD = "secret123"
# (nome, papel, instituicao)
USERS = (
    ("secretaria", UserRole.admin, "alfa"),
    ("ana", UserRole.student, "alfa"),
    ("beta", UserRole.secretary, "beta"),
)


def seed() -> tuple[dict[str, str], dict[str, str]]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    institutions, ids = {}, {}
    with SessionLocal() as db:
        for slug in ("alfa", "beta"):
            institution = Institution(slug=slug, name=slug.title())
            db.add(institution)
            db.flush()
            institutions[slug] = institution.id
        for name, role, slug in USERS:
            user = Student(name=name.title(), email=f"{name}@example.com", password_hash=hash_password(PASSWORD), role=role)
            db.add(user)
            db.flush()
            db.add(InstitutionMembership(institution_id=institutions[slug], user_id=user.id, role=role))
            ids[name] = str(user.id)
        db.commit()
    return institutions, ids


def publish_notice(institution_id, student_id: str) -> None:
    with SessionLocal() as db:
        bind_institution(db, institution_id)
        NotificationEventService(db).publish(
            NotificationEventType.grades_published, {"class_name": "Matemática", "result_label": "aprovado"},
            recipient_student_id=student_id,
        )
        db.commit()


def raw_notice(institution_id, student_id: str, *, bound: bool, commit: bool) -> None:
    """Sem instituicao vinculada e o caso do worker/webhook (registro com a instituicao explicita)."""
    with SessionLocal() as db:
        if bound:
            bind_institution(db, institution_id)
        db.add(NotificationEvent(institution_id=institution_id, event_type=NotificationEventType.grades_published,
                                 recipient_student_id=student_id, title="Aviso", body="Corpo"))
        db.flush()
        db.commit() if commit else db.rollback()


def bulk_touch_class_groups(institution_id) -> None:
    with SessionLocal() as db:
        bind_institution(db, institution_id)
        db.query(ClassGroup).filter(ClassGroup.capacity.is_(None)).update({ClassGroup.capacity: 30})
        db.commit()


class Checker:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client
        self.failures: list[str] = []

    def expect(self, condition: bool, message: str) -> None:
        if not condition:
            self.failures.append(message)

    async def login(self, email: str) -> dict:
        response = await self.client.post("/auth/login", json={"email": email, "password": PASSWORD})
        assert response.status_code == 200, f"login {email}: {response.status_code} {response.text}"
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    async def call(self, method: str, path: str, expected: int, message: str, headers: dict, **kwargs):
        response = await self.client.request(method, path, headers=headers, **kwargs)
        self.expect(response.status_code == expected, f"{message}: {response.status_code} {response.text[:200]}")
        return response.json() if response.content else {}

    async def versions(self, headers: dict, message: str) -> dict[str, int]:
        return (await self.call("GET", "/sync/versions", 200, message, headers)).get("versions", {})


async def check_versions(c: Checker, h: dict, institutions: dict, ids: dict) -> None:
    await c.call("GET", "/sync/versions", 401, "versions need login", {})
    start = await c.versions(h["ana"], "initial versions")
    c.expect(start == {"notifications": 0, "agenda": 0, "report_card": 0, "dependents": 0, "benefits": 0, "materials": 0}, f"initial: {start}")

    publish_notice(institutions["alfa"], ids["ana"])
    after_notice = await c.versions(h["ana"], "after notice")
    c.expect(after_notice["notifications"] == 1 and after_notice["dependents"] == 0, f"notice bumps only notifications: {after_notice}")

    notices = await c.call("GET", "/notifications/me", 200, "inbox", h["ana"])
    await c.call("POST", f"/notifications/me/{notices[0]['id']}/read", 200, "mark read", h["ana"])
    after_read = await c.versions(h["ana"], "after read")
    c.expect(after_read["notifications"] == 2, f"reading bumps notifications: {after_read}")

    publish_notice(institutions["alfa"], ids["ana"])
    await c.call("POST", "/notifications/me/read-all", 200, "read all", h["ana"])
    after_all = await c.versions(h["ana"], "after read all")
    c.expect(after_all["notifications"] == 4, f"bulk read-all bumps notifications: {after_all}")

    raw_notice(institutions["alfa"], ids["ana"], bound=True, commit=False)
    after_rollback = await c.versions(h["ana"], "after rollback")
    c.expect(after_rollback["notifications"] == 4, f"rolled back write keeps the version: {after_rollback}")

    raw_notice(institutions["alfa"], ids["ana"], bound=False, commit=True)
    unbound = await c.versions(h["ana"], "after worker write")
    c.expect(unbound["notifications"] == 5, f"write without bound institution bumps its own institution: {unbound}")

    bulk_touch_class_groups(institutions["alfa"])
    bulk = await c.versions(h["ana"], "after bulk class group update")
    c.expect(bulk["agenda"] == 1 and bulk["report_card"] == 0, f"bulk update bumps agenda: {bulk}")


async def check_dependents(c: Checker, h: dict, ids: dict) -> None:
    await c.call("POST", f"/guardians/students/{ids['ana']}/links", 201, "link guardian", h["secretaria"],
                 json={"name": "Maria", "email": "maria@example.com", "password": PASSWORD, "relationship_kind": "mother"})
    linked = await c.versions(h["secretaria"], "after link")
    c.expect(linked["dependents"] >= 1, f"guardian link bumps dependents: {linked}")

    await c.login("ana@example.com")
    after_login = await c.versions(h["secretaria"], "after login")
    c.expect(after_login["dependents"] == linked["dependents"], f"login does not bump dependents: {after_login}")

    await c.call("PATCH", f"/users/{ids['ana']}", 200, "rename student", h["secretaria"], json={"name": "Ana Souza"})
    renamed = await c.versions(h["secretaria"], "after rename")
    c.expect(renamed["dependents"] == linked["dependents"] + 1, f"student name bumps dependents: {renamed}")

    other = await c.versions(h["beta"], "other institution")
    c.expect(other == {"notifications": 0, "agenda": 0, "report_card": 0, "dependents": 0, "benefits": 0, "materials": 0}, f"versions are per institution: {other}")


async def run() -> int:
    institutions, ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with ApiClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        h = {name: await c.login(f"{name}@example.com") for name, _, _ in USERS}
        await check_versions(c, h, institutions, ids)
        await check_dependents(c, h, ids)

    if c.failures:
        print("Sync flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Sync flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
