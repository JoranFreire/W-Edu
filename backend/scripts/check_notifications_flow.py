"""Exercise communication admin: default templates, creating a template for another channel, editing and deactivating it,
retrying a failed event (only failed ones) and tenant isolation of templates and events.

Uses a temporary SQLite database by default (set DATABASE_URL to use PostgreSQL).
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
import sys

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_notifications_check_{os.getpid()}.sqlite3"
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
from app.models.institution import Institution, InstitutionMembership, InstitutionType
from app.models.notification import NotificationEvent, NotificationEventType, NotificationStatus
from app.models.student import Student, UserRole
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
USERS = {
    "escola-a": [("admin-a", UserRole.institution_admin), ("prof", UserRole.instructor)],
    "escola-b": [("admin-b", UserRole.institution_admin)],
}


def seed() -> dict[str, int]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ids = {}
    with SessionLocal() as db:
        for slug, users in USERS.items():
            institution = Institution(slug=slug, name=slug.title(), type=InstitutionType.school)
            db.add(institution)
            db.flush()
            ids[slug] = str(institution.id)
            for name, role in users:
                user = Student(name=name.title(), email=f"{name}@example.com", password_hash=hash_password(PASSWORD), role=role)
                db.add(user)
                db.flush()
                db.add(InstitutionMembership(institution_id=institution.id, user_id=user.id, role=role))
                ids[name] = str(user.id)
        db.commit()
    return ids


def add_event(institution_id: int, status: NotificationStatus, error: str | None = None) -> int:
    with SessionLocal() as db:
        bind_institution(db, institution_id)
        event = NotificationEvent(
            event_type=NotificationEventType.absence_dismissal, title="Desligamento por faltas", body="Corpo",
            status=status, error_message=error,
        )
        db.add(event)
        db.commit()
        return event.id


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


async def check_templates(c: Checker, h: dict) -> None:
    defaults = await c.call("GET", "/notifications/templates", 200, "list templates", h["admin-a"])
    keys = {(t["key"], t["channel"]) for t in defaults}
    c.expect(("absence_dismissal", "internal") in keys, f"default templates: {sorted(keys)}")
    await c.call("GET", "/notifications/templates", 403, "instructor cannot manage templates", h["prof"])

    body = {"key": "absence_dismissal", "channel": "whatsapp", "title_template": "Aviso", "body_template": "Ola {student_name}"}
    created = await c.call("POST", "/notifications/templates", 201, "create whatsapp template", h["admin-a"], json=body)
    c.expect(created.get("is_active") is True, f"new template active: {created}")
    await c.call("POST", "/notifications/templates", 409, "duplicate template", h["admin-a"], json=body)

    edited = await c.call("PATCH", "/notifications/templates/absence_dismissal/whatsapp", 200, "edit template", h["admin-a"],
                          json={"title_template": "Desligamento", "is_active": False})
    c.expect(edited.get("title_template") == "Desligamento" and edited.get("is_active") is False, f"edited: {edited}")

    other = await c.call("GET", "/notifications/templates", 200, "B templates", h["admin-b"])
    c.expect(("absence_dismissal", "whatsapp") not in {(t["key"], t["channel"]) for t in other}, "B does not see A template")
    await c.call("PATCH", "/notifications/templates/absence_dismissal/whatsapp", 404, "B cannot edit A template", h["admin-b"], json={"title_template": "X"})


async def check_inactive_fallback(c: Checker, h: dict) -> None:
    await c.call("PATCH", "/notifications/templates/absence_dismissal/internal", 200, "customize internal", h["admin-a"],
                 json={"title_template": "Personalizado", "body_template": "Texto {student_name}"})
    event = await c.call("POST", "/notifications/events", 201, "event with custom template", h["admin-a"],
                         json={"event_type": "absence_dismissal", "channel": "internal", "payload": {"student_name": "Ana"}})
    c.expect(event.get("title") == "Personalizado" and event.get("body") == "Texto Ana", f"custom template used: {event}")

    await c.call("PATCH", "/notifications/templates/absence_dismissal/internal", 200, "deactivate internal", h["admin-a"], json={"is_active": False})
    event = await c.call("POST", "/notifications/events", 201, "event with inactive template", h["admin-a"],
                         json={"event_type": "absence_dismissal", "channel": "internal", "payload": {"class_name": "Turma 1"}})
    c.expect(event.get("title") == "Desligamento por faltas" and "Turma 1" in event.get("body", ""), f"platform default used: {event}")

    # Template de WhatsApp desativado (check_templates) cai no texto do canal interno.
    event = await c.call("POST", "/notifications/events", 201, "whatsapp event", h["admin-a"],
                         json={"event_type": "absence_dismissal", "channel": "whatsapp", "payload": {}})
    c.expect(event.get("title") == "Desligamento por faltas", f"inactive whatsapp falls back: {event}")


async def check_retry(c: Checker, h: dict, ids: dict) -> None:
    failed = add_event(ids["escola-a"], NotificationStatus.failed, "WOMNI_URL não configurado")
    sent = add_event(ids["escola-a"], NotificationStatus.sent)

    retried = await c.call("POST", f"/notifications/events/{failed}/retry", 200, "retry failed event", h["admin-a"])
    c.expect(retried.get("status") == "pending" and retried.get("error_message") is None, f"retried: {retried}")
    await c.call("POST", f"/notifications/events/{failed}/retry", 409, "pending event cannot be retried", h["admin-a"])
    await c.call("POST", f"/notifications/events/{sent}/retry", 409, "sent event cannot be retried", h["admin-a"])
    await c.call("POST", f"/notifications/events/{sent}/retry", 404, "B cannot retry A event", h["admin-b"])
    await c.call("POST", f"/notifications/events/{sent}/retry", 403, "instructor cannot retry", h["prof"])


async def run() -> int:
    ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with ApiClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        h = {name: await c.login(f"{name}@example.com") for users in USERS.values() for name, _ in users}
        await check_templates(c, h)
        await check_inactive_fallback(c, h)
        await check_retry(c, h, ids)

    if c.failures:
        print("Notifications flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Notifications flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
