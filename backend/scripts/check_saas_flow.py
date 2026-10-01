"""Exercise SaaS plans (phase 17, delivery 2): platform catalog, institution subscription with trial, monthly invoices,
student seat limit and the institution's own view.

Uses a temporary SQLite database by default (set DATABASE_URL to use PostgreSQL).
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
import sys

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_saas_check_{os.getpid()}.sqlite3"
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

import app.models  # noqa: F401
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.institution import Institution, InstitutionMembership, InstitutionType
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
PASSWORD = "secret123"


def seed() -> dict[str, int]:
    """Escola A (admin-a) e Escola B (admin-b); root e super admin."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        ids = {}
        for slug in ("escola-a", "escola-b"):
            institution = Institution(slug=slug, name=slug.replace("-", " ").title(), type=InstitutionType.school)
            db.add(institution)
            db.flush()
            ids[slug] = institution.id
        users = (("root", UserRole.super_admin, ["escola-a"]), ("admin-a", UserRole.institution_admin, ["escola-a"]),
                 ("admin-b", UserRole.institution_admin, ["escola-b"]))
        for name, role, slugs in users:
            user = Student(name=name.title(), email=f"{name}@example.com", password_hash=hash_password(PASSWORD), role=role)
            db.add(user)
            db.flush()
            for slug in slugs:
                db.add(InstitutionMembership(institution_id=ids[slug], user_id=user.id, role=role))
        db.commit()
    return ids


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


async def check_catalog(c: Checker, root: dict, admin_a: dict) -> dict:
    await c.call("POST", "/saas/plans", 403, "institution admin cannot create plans", admin_a, json={"name": "X", "monthly_price_cents": 1})
    basic = await c.call("POST", "/saas/plans", 201, "basic plan", root, json={"name": "Básico", "monthly_price_cents": 49900, "max_students": 2})
    pro = await c.call("POST", "/saas/plans", 201, "pro plan", root, json={"name": "Profissional", "monthly_price_cents": 149900})
    await c.call("POST", "/saas/plans", 409, "duplicate name", root, json={"name": "Básico", "monthly_price_cents": 1})
    retired = await c.call("POST", "/saas/plans", 201, "plan to retire", root, json={"name": "Antigo", "monthly_price_cents": 100})
    await c.call("PATCH", f"/saas/plans/{retired['id']}", 200, "retire", root, json={"is_active": False})
    listed = await c.call("GET", "/saas/plans", 200, "list plans", root)
    c.expect([p["name"] for p in listed] == ["Antigo", "Básico", "Profissional"], f"plans by price: {listed}")
    return {"basic": basic["id"], "pro": pro["id"], "retired": retired["id"]}


async def check_subscription_and_seats(c: Checker, root: dict, admin_a: dict, ids: dict, plans: dict) -> None:
    a = ids["escola-a"]
    none = await c.call("GET", "/saas/current", 200, "no plan yet", admin_a)
    c.expect(none["subscription"] is None and none["usage"]["max_students"] is None, f"no subscription: {none}")
    await c.call("PUT", f"/saas/institutions/{a}/subscription", 409, "inactive plan", root, json={"plan_id": plans["retired"]})
    await c.call("PUT", f"/saas/institutions/9999/subscription", 404, "unknown institution", root, json={"plan_id": plans["basic"]})
    await c.call("PUT", f"/saas/institutions/{a}/subscription", 403, "institution admin cannot subscribe", admin_a, json={"plan_id": plans["pro"]})
    subscription = await c.call("PUT", f"/saas/institutions/{a}/subscription", 200, "trial on basic", root,
                                json={"plan_id": plans["basic"], "status": "trial", "started_on": "2027-01-01", "trial_ends_on": "2027-01-31"})
    c.expect(subscription["plan"]["name"] == "Básico" and subscription["status"] == "trial", f"subscription: {subscription}")

    for index in range(2):
        await c.call("POST", "/admin/users", 201, f"student {index}", admin_a,
                     json={"name": f"Aluno {index}", "email": f"aluno{index}@example.com", "password": PASSWORD, "role": "student"})
    blocked = await c.call("POST", "/admin/users", 409, "seat limit", admin_a,
                           json={"name": "Aluno 2", "email": "aluno2@example.com", "password": PASSWORD, "role": "student"})
    c.expect("Limite de alunos" in blocked.get("detail", ""), f"limit message: {blocked}")
    await c.call("POST", "/admin/users", 201, "staff is not limited", admin_a,
                 json={"name": "Prof", "email": "prof@example.com", "password": PASSWORD, "role": "instructor"})
    current = await c.call("GET", "/saas/current", 200, "institution view", admin_a)
    c.expect(current["usage"] == {"active_students": 2, "max_students": 2}, f"usage: {current['usage']}")

    other = await c.call("GET", "/saas/current", 200, "other institution view", await c.login("admin-b@example.com"))
    c.expect(other["subscription"] is None and other["invoices"] == [], f"B sees nothing of A: {other}")

    await c.call("PUT", f"/saas/institutions/{a}/subscription", 200, "upgrade to pro", root, json={"plan_id": plans["pro"], "status": "active"})
    await c.call("POST", "/admin/users", 201, "no limit on pro", admin_a,
                 json={"name": "Aluno 2", "email": "aluno2@example.com", "password": PASSWORD, "role": "student"})


async def check_invoices(c: Checker, root: dict, admin_a: dict, ids: dict, plans: dict) -> None:
    a = ids["escola-a"]
    await c.call("PUT", f"/saas/institutions/{a}/subscription", 200, "back to trial", root,
                 json={"plan_id": plans["basic"], "status": "trial", "trial_ends_on": "2027-01-31"})
    trial = await c.call("POST", f"/saas/institutions/{a}/invoices", 201, "trial invoice", root, json={"period_start": "2027-01-01"})
    c.expect(trial["amount_cents"] == 0 and trial["period_end"] == "2027-01-31" and trial["due_on"] == "2027-01-11", f"trial invoice: {trial}")
    await c.call("PUT", f"/saas/institutions/{a}/subscription", 200, "activate", root, json={"plan_id": plans["basic"], "status": "active"})
    february = await c.call("POST", f"/saas/institutions/{a}/invoices", 201, "february invoice", root, json={"period_start": "2027-02-01"})
    c.expect(february["amount_cents"] == 49900 and february["period_end"] == "2027-02-28" and february["plan_name"] == "Básico", f"february: {february}")
    again = await c.call("POST", f"/saas/institutions/{a}/invoices", 201, "same period", root, json={"period_start": "2027-02-01"})
    c.expect(again["id"] == february["id"], "one invoice per period")
    await c.call("POST", f"/saas/invoices/{february['id']}/paid", 403, "institution cannot mark paid", admin_a)
    paid = await c.call("POST", f"/saas/invoices/{february['id']}/paid", 200, "mark paid", root)
    c.expect(paid["status"] == "paid" and paid["paid_at"], f"paid: {paid}")
    await c.call("POST", f"/saas/invoices/{february['id']}/paid", 409, "pay twice", root)
    overview = await c.call("GET", f"/saas/institutions/{a}", 200, "platform overview", root)
    c.expect([i["period_start"] for i in overview["invoices"]] == ["2027-02-01", "2027-01-01"], f"invoices newest first: {overview}")
    mine = await c.call("GET", "/saas/current", 200, "institution invoices", admin_a)
    c.expect(len(mine["invoices"]) == 2, f"institution sees invoices: {mine}")
    await c.call("PUT", f"/saas/institutions/{a}/subscription", 200, "cancel", root, json={"plan_id": plans["basic"], "status": "cancelled"})
    await c.call("POST", f"/saas/institutions/{a}/invoices", 409, "no invoice when cancelled", root, json={"period_start": "2027-03-01"})


async def run() -> int:
    ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        root, admin_a = await c.login("root@example.com"), await c.login("admin-a@example.com")
        plans = await check_catalog(c, root, admin_a)
        await check_subscription_and_seats(c, root, admin_a, ids, plans)
        await check_invoices(c, root, admin_a, ids, plans)

    if c.failures:
        print("SaaS flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("SaaS flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
