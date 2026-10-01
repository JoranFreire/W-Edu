"""Exercise the public pages: platform domain shows no institution, institution page by slug, custom domain and
subdomain (content, active programs, open calls only, isolation), profile editing, public plans and sales leads.

Uses a temporary SQLite database by default (set DATABASE_URL to use PostgreSQL).
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
import sys

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_public_site_check_{os.getpid()}.sqlite3"
    os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["NOTIFICATION_WORKER_ENABLED"] = "false"
os.environ["TENANT_BASE_DOMAIN"] = "wedu.test"

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
from app.models.academic import Program, ProgramLevel, ProgramStatus
from app.models.course import Course
from app.models.institution import InstitutionStatus
from app.models.saas import SaasPlan
from app.models.sales import SalesLead
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
    "escola-a": [("admin-a", UserRole.institution_admin)],
    "escola-b": [("admin-b", UserRole.institution_admin)],
    "escola-c": [],
}


def seed() -> dict[str, str]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ids = {}
    with SessionLocal() as db:
        for slug, users in USERS.items():
            institution = Institution(slug=slug, name=slug.title(), type=InstitutionType.vocational,
                                      status=InstitutionStatus.archived if slug == "escola-c" else InstitutionStatus.active)
            db.add(institution)
            db.flush()
            ids[slug] = str(institution.id)
            for name, role in users:
                user = Student(name=name.title(), email=f"{name}@example.com", password_hash=hash_password(PASSWORD), role=role)
                db.add(user)
                db.flush()
                db.add(InstitutionMembership(institution_id=institution.id, user_id=user.id, role=role))
                ids[name] = str(user.id)
        root = Student(name="Root", email="root@example.com", password_hash=hash_password(PASSWORD), role=UserRole.super_admin)
        db.add(root)
        db.add_all([
            SaasPlan(name="Pro", monthly_price_cents=99000, max_students=500, is_active=True),
            SaasPlan(name="Basico", monthly_price_cents=29000, max_students=100, is_active=True),
            SaasPlan(name="Antigo", monthly_price_cents=10000, is_active=False),
        ])
        db.commit()
    for slug, programs in (("escola-a", [("TEC-ENF", "Técnico em Enfermagem", ProgramStatus.active), ("RASC", "Rascunho", ProgramStatus.draft)]),
                           ("escola-b", [("ADM", "Administração B", ProgramStatus.active)])):
        with SessionLocal() as db:
            bind_institution(db, ids[slug])
            for code, name, status in programs:
                db.add(Program(code=code, name=name, level=ProgramLevel.technical, status=status))
            db.add(Course(name=f"Curso livre {slug}"))
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

    async def call(self, method: str, path: str, expected: int, message: str, headers: dict | None = None, **kwargs):
        response = await self.client.request(method, path, headers=headers or {}, **kwargs)
        self.expect(response.status_code == expected, f"{message}: {response.status_code} {response.text[:200]}")
        return response.json() if response.content else None


async def check_pages(c: Checker, h: dict) -> None:
    platform = await c.call("GET", "/public/institution-page", 200, "platform domain", {"Host": "wedu.test"})
    c.expect(platform is None, f"platform domain has no institution: {platform}")
    unknown = await c.call("GET", "/public/institution-page", 200, "unknown host", {"Host": "outro-site.com"})
    c.expect(unknown is None, "unknown host is not an institution")

    await c.call("PATCH", "/institutions/current", 200, "admin edits public profile", h["admin-a"],
                 json={"public_profile": {"tagline": "Formação que transforma", "about": "Escola técnica.", "phone": "81 3333-0000"}})
    page = await c.call("GET", "/public/institution-page?institution=escola-a", 200, "page by slug")
    c.expect(page["institution"]["slug"] == "escola-a" and page["profile"]["tagline"] == "Formação que transforma", f"profile: {page['profile']}")
    c.expect([p["code"] for p in page["programs"]] == ["TEC-ENF"], f"only active programs: {page['programs']}")
    c.expect([course["name"] for course in page["courses"]] == ["Curso livre escola-a"], f"isolated courses: {page['courses']}")
    c.expect(page["open_calls"] == [], "no open calls")

    by_subdomain = await c.call("GET", "/public/institution-page", 200, "page by subdomain", {"X-Forwarded-Host": "escola-b.wedu.test"})
    c.expect(by_subdomain["institution"]["slug"] == "escola-b" and [p["code"] for p in by_subdomain["programs"]] == ["ADM"], "subdomain B")
    await c.call("GET", "/public/institution-page?institution=nao-existe", 404, "unknown slug")


async def check_custom_domain(c: Checker, h: dict, ids: dict) -> None:
    root = await c.login("root@example.com")
    saved = await c.call("PUT", f"/platform/institutions/{ids['escola-a']}/domain", 200, "set domain", root,
                         json={"custom_domain": "https://Escola-A.Exemplo.com.br/matriculas"})
    c.expect(saved and saved.get("custom_domain") == "escola-a.exemplo.com.br", f"normalized domain: {saved}")
    await c.call("PUT", f"/platform/institutions/{ids['escola-b']}/domain", 409, "domain taken", root, json={"custom_domain": "escola-a.exemplo.com.br"})
    await c.call("PUT", f"/platform/institutions/{ids['escola-b']}/domain", 422, "invalid domain", root, json={"custom_domain": "nao é domínio"})
    await c.call("PUT", f"/platform/institutions/{ids['escola-b']}/domain", 422, "platform subdomain", root, json={"custom_domain": "b.wedu.test"})
    await c.call("PUT", f"/platform/institutions/{ids['escola-a']}/domain", 403, "admin cannot set domain", h["admin-a"], json={"custom_domain": "x.com.br"})
    await c.call("PUT", f"/platform/institutions/{ids['escola-c']}/domain", 200, "archived institution domain", root, json={"custom_domain": "escola-c.com.br"})

    host = {"X-Forwarded-Host": "escola-a.exemplo.com.br:443"}
    page = await c.call("GET", "/public/institution-page", 200, "page by custom domain", host)
    c.expect(page and page["institution"]["slug"] == "escola-a", f"custom domain resolves: {page}")
    brand = await c.call("GET", "/institutions/public", 200, "branding by custom domain", host)
    c.expect(brand and brand["slug"] == "escola-a", "branding by custom domain")
    inactive = await c.call("GET", "/public/institution-page", 200, "archived institution domain", {"X-Forwarded-Host": "escola-c.com.br"})
    c.expect(inactive is None, "archived institution is not served")
    current = await c.call("GET", "/institutions/current", 200, "logged in on custom domain", {**h["admin-a"], **host})
    c.expect(current["slug"] == "escola-a", "custom domain selects the institution")
    await c.call("GET", "/institutions/current", 403, "admin B on A's domain", {**h["admin-b"], **host})
    cleared = await c.call("PUT", f"/platform/institutions/{ids['escola-a']}/domain", 200, "clear domain", root, json={"custom_domain": ""})
    c.expect(cleared["custom_domain"] is None, "domain cleared")


async def check_plans_and_leads(c: Checker, h: dict) -> None:
    plans = await c.call("GET", "/public/plans", 200, "public plans")
    c.expect([plan["name"] for plan in plans] == ["Basico", "Pro"], f"active plans by price: {plans}")
    lead = {"name": "Maria Diretora", "email": "maria@escola.com.br", "institution_name": "Escola Nova", "institution_type": "school",
            "students_estimate": 300, "plan_id": plans[0]["id"], "message": "Queremos uma demonstração."}
    await c.call("POST", "/public/leads", 202, "register lead", json=lead)
    await c.call("POST", "/public/leads", 202, "bot lead accepted silently", json={**lead, "email": "bot@spam.com", "website": "http://spam"})
    await c.call("POST", "/public/leads", 422, "invalid lead", json={**lead, "email": "nao-e-email"})
    with SessionLocal() as db:
        c.expect(db.query(SalesLead).count() == 1, "honeypot lead is not stored")

    root = await c.login("root@example.com")
    leads = await c.call("GET", "/platform/leads", 200, "list leads", root)
    c.expect(len(leads) == 1 and leads[0]["plan_name"] == "Basico" and leads[0]["status"] == "new", f"leads: {leads}")
    await c.call("GET", "/platform/leads", 403, "institution admin cannot see leads", h["admin-a"])
    updated = await c.call("PATCH", f"/platform/leads/{leads[0]['id']}", 200, "update lead", root, json={"status": "contacted", "notes": "Ligar segunda"})
    c.expect(updated["status"] == "contacted" and updated["notes"] == "Ligar segunda", f"updated: {updated}")
    contacted = await c.call("GET", "/platform/leads?status=new", 200, "filter leads", root)
    c.expect(contacted == [], "status filter")


async def run() -> int:
    ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with ApiClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        h = {name: await c.login(f"{name}@example.com") for users in USERS.values() for name, _ in users}
        await check_pages(c, h)
        await check_custom_domain(c, h, ids)
        await check_plans_and_leads(c, h)

    if c.failures:
        print("Public site flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Public site flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
