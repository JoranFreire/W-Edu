"""Exercise guardians (phase 15, delivery 1): links managed by the secretariat and the guardian portal.

Uses a temporary SQLite database by default (set DATABASE_URL to use PostgreSQL).
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
import sys

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_guardians_check_{os.getpid()}.sqlite3"
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
from app.models.finance import Charge
from app.models.institution import Institution, InstitutionMembership
from app.models.notification import NotificationEventType
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
USERS = (
    ("secretaria", UserRole.secretary),
    ("prof", UserRole.instructor),
    ("ana", UserRole.student),
    ("beto", UserRole.student),
    ("carla", UserRole.student),
)


def seed() -> tuple[int, dict[str, int]]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ids = {}
    with SessionLocal() as db:
        institution = Institution(slug="escola", name="Escola")
        db.add(institution)
        db.flush()
        for name, role in USERS:
            user = Student(name=name.title(), email=f"{name}@example.com", password_hash=hash_password(PASSWORD), role=role)
            db.add(user)
            db.flush()
            db.add(InstitutionMembership(institution_id=institution.id, user_id=user.id, role=role))
            ids[name] = str(user.id)
        institution_id = institution.id
        db.commit()
    return institution_id, ids


def seed_notice_and_charge(institution_id: int, student_id: int) -> None:
    """Comunicado e cobranca da aluna, que o responsavel ve no portal."""
    with SessionLocal() as db:
        bind_institution(db, institution_id)
        NotificationEventService(db).publish(
            NotificationEventType.grades_published, {"class_name": "Matemática", "result_label": "aprovado"},
            recipient_student_id=student_id,
        )
        db.add(Charge(student_id=student_id, amount_cents=45000))
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


async def check_links(c: Checker, sec: dict, ids: dict) -> dict[str, int]:
    maria = {"name": "Maria", "email": "maria@example.com", "password": PASSWORD, "relationship_kind": "mother", "is_financial": True, "is_primary": True}
    link_ana = await c.call("POST", f"/guardians/students/{ids['ana']}/links", 201, "new guardian account", sec, json=maria)
    c.expect(link_ana.get("guardian", {}).get("name") == "Maria" and link_ana.get("is_primary") is True, f"link: {link_ana}")
    await c.call("POST", f"/guardians/students/{ids['ana']}/links", 409, "duplicate link", sec, json=maria)
    link_beto = await c.call("POST", f"/guardians/students/{ids['beto']}/links", 201, "existing guardian reused", sec,
                             json={"name": "Maria", "email": "maria@example.com", "relationship_kind": "mother"})
    c.expect(link_beto.get("guardian", {}).get("id") == link_ana["guardian"]["id"], "same guardian account for siblings")
    # Conta de outro papel (professor) passa a ser tambem responsavel, sem perder o papel que tinha.
    prof_link = await c.call("POST", f"/guardians/students/{ids['ana']}/links", 201, "teacher becomes guardian too", sec,
                             json={"name": "Prof", "email": "prof@example.com", "relationship_kind": "father"})
    prof = await c.login("prof@example.com")
    access = await c.call("GET", "/access/me", 200, "teacher access", prof)
    c.expect({"instructor", "guardian"} <= set(access.get("roles", [])), f"teacher and guardian roles: {access}")
    await c.call("GET", "/assessment/teaching/offerings", 200, "still teaches", prof)
    kids = await c.call("GET", "/guardians/me/dependents", 200, "teacher sees dependents", prof)
    c.expect([d["student"]["name"] for d in kids] == ["Ana"], f"teacher dependents: {kids}")
    await c.call("DELETE", f"/guardians/links/{prof_link['id']}", 204, "remove teacher link", sec)
    await c.call("POST", f"/guardians/students/{ids['ana']}/links", 409, "student cannot guard herself", sec,
                 json={"name": "Ana", "email": "ana@example.com"})
    await c.call("POST", f"/guardians/students/{ids['ana']}/links", 400, "new account needs password", sec,
                 json={"name": "Sem senha", "email": "semsenha@example.com"})
    await c.call("POST", f"/guardians/students/{ids['prof']}/links", 404, "only students have guardians", sec,
                 json={"name": "X", "email": "x@example.com", "password": PASSWORD})

    joao = await c.call("POST", f"/guardians/students/{ids['ana']}/links", 201, "second guardian as primary", sec,
                        json={"name": "João", "email": "joao@example.com", "password": PASSWORD, "relationship_kind": "father", "is_primary": True})
    links = await c.call("GET", f"/guardians/students/{ids['ana']}/links", 200, "list links", sec)
    c.expect([(link["guardian"]["name"], link["is_primary"]) for link in links] == [("João", True), ("Maria", False)], f"one primary guardian: {links}")
    await c.call("PATCH", f"/guardians/links/{link_beto['id']}", 200, "update link", sec, json={"can_pick_up": False})
    return {"joao_link": joao["id"]}


async def check_portal(c: Checker, h: dict, ids: dict, institution_id: int, joao_link: int) -> None:
    maria, joao = await c.login("maria@example.com"), await c.login("joao@example.com")
    dependents = await c.call("GET", "/guardians/me/dependents", 200, "maria dependents", maria)
    c.expect([(d["student"]["name"], d["is_financial"], d["can_pick_up"]) for d in dependents] == [("Ana", True, True), ("Beto", False, False)],
             f"dependents: {dependents}")
    seed_notice_and_charge(institution_id, ids["ana"])
    base = f"/guardians/me/dependents/{ids['ana']}"
    await c.call("GET", f"{base}/report-card", 200, "dependent report card", maria)
    await c.call("GET", f"{base}/transcripts", 200, "dependent transcripts", maria)
    notices = await c.call("GET", f"{base}/notices", 200, "dependent notices", maria)
    c.expect([n["title"] for n in notices] == ["Boletim disponível"], f"notices: {notices}")
    charges = await c.call("GET", f"{base}/charges", 200, "financial guardian sees charges", maria)
    c.expect([ch["amount_cents"] for ch in charges] == [45000], f"charges: {charges}")
    await c.call("GET", f"{base}/charges", 403, "non-financial guardian", joao)
    await c.call("GET", f"/guardians/me/dependents/{ids['beto']}/charges", 403, "not financial for beto", maria)
    await c.call("GET", f"/guardians/me/dependents/{ids['carla']}/report-card", 404, "unlinked student", maria)
    await c.call("GET", "/guardians/me/dependents", 403, "student cannot use portal", h["ana"])
    await c.call("GET", f"/guardians/students/{ids['ana']}/links", 403, "guardian cannot manage links", maria)

    await c.call("DELETE", f"/guardians/links/{joao_link}", 204, "remove link", h["secretaria"])
    after = await c.call("GET", "/guardians/me/dependents", 200, "joao dependents after removal", joao)
    c.expect(after == [], f"removed link hides dependent: {after}")


async def run() -> int:
    institution_id, ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with ApiClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        h = {name: await c.login(f"{name}@example.com") for name, _ in USERS}
        links = await check_links(c, h["secretaria"], ids)
        await check_portal(c, h, ids, institution_id, links["joao_link"])

    if c.failures:
        print("Guardians flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Guardians flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
