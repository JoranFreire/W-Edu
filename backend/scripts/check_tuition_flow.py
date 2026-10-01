"""Exercise educational billing (phase 17, delivery 1): tuition plans by program, class group and credit, idempotent
generation, scholarships and discounts, punctuality, late fine and interest, financial guardian as payer and settlement.

Uses a temporary SQLite database by default (set DATABASE_URL to use PostgreSQL).
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
import sys

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_tuition_check_{os.getpid()}.sqlite3"
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
USERS = (
    ("admin", UserRole.institution_admin),
    ("coord", UserRole.coordinator),
    ("secretaria", UserRole.secretary),
    ("ana", UserRole.student),
    ("bia", UserRole.student),
    ("carla", UserRole.student),
)


def seed() -> dict[str, int]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ids = {}
    with SessionLocal() as db:
        institution = Institution(slug="colegio", name="Colégio", type=InstitutionType.mixed)
        db.add(institution)
        db.flush()
        for name, role in USERS:
            user = Student(name=name.title(), email=f"{name}@example.com", password_hash=hash_password(PASSWORD), role=role)
            db.add(user)
            db.flush()
            db.add(InstitutionMembership(institution_id=institution.id, user_id=user.id, role=role))
            ids[name] = str(user.id)
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


async def setup_structure(c: Checker, h: dict, ids: dict) -> dict:
    """EF (ana e bia na turma 6A), DIR por credito (carla com 8 creditos no periodo) e Maria, responsavel financeira de Ana."""
    coord, sec = h["coord"], h["secretaria"]
    term = await c.call("POST", "/academic/terms", 201, "term", coord, json={"name": "2027", "starts_on": "2027-02-01", "ends_on": "2027-12-15"})
    ef = await c.call("POST", "/academic/programs", 201, "EF", coord, json={"code": "EF", "name": "Fundamental", "level": "basic"})
    dir_ = await c.call("POST", "/academic/programs", 201, "DIR", coord, json={"code": "DIR", "name": "Direito", "level": "undergraduate"})
    course = await c.call("POST", "/courses", 201, "course", coord, json={"name": "Base"})
    offerings = []
    for program, codes in ((ef, ("MAT",)), (dir_, ("D1", "D2"))):
        curriculum = await c.call("POST", f"/academic/programs/{program['id']}/curricula", 201, "curriculum", coord, json={"version": "1"})
        for code in codes:
            subject = await c.call("POST", "/academic/subjects", 201, f"subject {code}", coord, json={"code": code, "name": code, "hours": 60, "credits": 4})
            await c.call("POST", f"/academic/curricula/{curriculum['id']}/components", 201, f"component {code}", coord,
                         json={"subject_id": subject["id"], "term_number": 1})
            if program is dir_:
                offering = await c.call("POST", "/schedule/classes", 201, f"offering {code}", coord, json={
                    "course_id": course["id"], "name": f"{code}-A", "capacity": 10, "status": "open", "term_id": term["id"],
                    "subject_id": subject["id"], "starts_at": "2027-02-01T08:00:00Z", "ends_at": "2027-06-30T12:00:00Z",
                })
                offerings.append(offering["id"])
        await c.call("POST", f"/academic/curricula/{curriculum['id']}/activate", 200, "activate", coord)
    group = await c.call("POST", "/academic/class-groups", 201, "group", coord, json={"program_id": ef["id"], "term_id": term["id"], "name": "6A"})
    enrollments = {}
    for name, program in (("ana", ef), ("bia", ef), ("carla", dir_)):
        enrollments[name] = (await c.call("POST", "/academic/program-enrollments", 201, f"enroll {name}", coord,
                                          json={"student_id": ids[name], "program_id": program["id"]}))["id"]
    for name in ("ana", "bia"):
        await c.call("POST", f"/academic/class-groups/{group['id']}/members", 201, f"allocate {name}", coord,
                     json={"program_enrollment_id": enrollments[name]})
    for offering_id in offerings:
        await c.call("POST", f"/registration/program-enrollments/{enrollments['carla']}/offerings/{offering_id}", 200, "carla registers", sec, json={})
    await c.call("POST", f"/guardians/students/{ids['ana']}/links", 201, "financial guardian", sec,
                 json={"name": "Maria", "email": "maria@example.com", "password": PASSWORD, "relationship_kind": "mother", "is_financial": True})
    return {"term": term["id"], "ef": ef["id"], "dir": dir_["id"], "group": group["id"], "enrollments": enrollments}


async def check_discounts(c: Checker, h: dict, ctx: dict) -> int:
    sec, enrollments = h["secretaria"], ctx["enrollments"]
    ana = f"/tuition/enrollments/{enrollments['ana']}/discounts"
    await c.call("POST", ana, 403, "coordinator is not finance", h["coord"], json={"kind": "scholarship", "percent": 50, "valid_from": "2027-01-01"})
    await c.call("POST", ana, 422, "percent and amount together", sec, json={"percent": 10, "amount_cents": 100, "valid_from": "2027-01-01"})
    await c.call("POST", ana, 201, "scholarship 50%", sec, json={"kind": "scholarship", "percent": 50, "valid_from": "2027-01-01"})
    await c.call("POST", ana, 201, "punctuality 10%", sec, json={"kind": "punctuality", "percent": 10, "valid_from": "2027-01-01"})
    temp = await c.call("POST", ana, 201, "discount to deactivate", sec, json={"kind": "agreement", "percent": 30, "valid_from": "2027-01-01"})
    off = await c.call("POST", f"/tuition/discounts/{temp['id']}/deactivate", 200, "deactivate", sec)
    c.expect(off["is_active"] is False, f"deactivated: {off}")
    await c.call("POST", f"/tuition/enrollments/{enrollments['bia']}/discounts", 201, "sibling until march", sec,
                 json={"kind": "sibling", "amount_cents": 5000, "valid_from": "2027-01-01", "valid_until": "2027-03-31"})
    listed = await c.call("GET", ana, 200, "list discounts", sec)
    c.expect(len(listed) == 3, f"discounts: {listed}")
    return temp["id"]


async def check_plans_and_generation(c: Checker, h: dict, ctx: dict) -> None:
    admin = h["admin"]
    base = {"term_id": ctx["term"], "installments": 3, "first_due_on": "2027-02-10"}
    await c.call("POST", "/tuition/plans", 403, "secretary cannot create plans", h["secretaria"], json={**base, "name": "X", "program_id": ctx["ef"], "amount_cents": 1})
    await c.call("POST", "/tuition/plans", 400, "program plan needs program", admin, json={**base, "name": "X", "amount_cents": 1})
    await c.call("POST", "/tuition/plans", 400, "group plan needs group", admin, json={**base, "name": "X", "basis": "class_group", "amount_cents": 1})
    plan = await c.call("POST", "/tuition/plans", 201, "program plan", admin, json={**base, "name": "Mensalidade EF", "program_id": ctx["ef"], "amount_cents": 100000})
    generated = await c.call("POST", f"/tuition/plans/{plan['id']}/generate", 200, "generate", admin)
    c.expect(generated == {"enrollments": 2, "created": 6, "skipped": 0}, f"generation: {generated}")
    again = await c.call("POST", f"/tuition/plans/{plan['id']}/generate", 200, "generate again", admin)
    c.expect(again == {"enrollments": 2, "created": 0, "skipped": 6}, f"idempotent: {again}")

    group_plan = await c.call("POST", "/tuition/plans", 201, "group plan", admin, json={
        "name": "Material 6A", "basis": "class_group", "class_group_id": ctx["group"], "term_id": ctx["term"],
        "amount_cents": 2000, "installments": 1, "first_due_on": "2027-02-15"})
    c.expect(group_plan["program_id"] == ctx["ef"] and group_plan["class_group_name"] == "6A", f"group plan: {group_plan}")
    group_run = await c.call("POST", f"/tuition/plans/{group_plan['id']}/generate", 200, "generate group", admin)
    c.expect(group_run["created"] == 2, f"group generation: {group_run}")

    credit_plan = await c.call("POST", "/tuition/plans", 201, "credit plan", admin, json={
        "name": "Crédito DIR", "basis": "credit", "program_id": ctx["dir"], "term_id": ctx["term"],
        "amount_cents": 10000, "installments": 2, "first_due_on": "2027-03-05"})
    credit_run = await c.call("POST", f"/tuition/plans/{credit_plan['id']}/generate", 200, "generate credit", admin)
    c.expect(credit_run == {"enrollments": 1, "created": 2, "skipped": 0}, f"credit generation: {credit_run}")
    carla = await c.call("GET", f"/tuition/enrollments/{ctx['enrollments']['carla']}/charges", 200, "carla statement", h["secretaria"])
    c.expect([ch["amount_cents"] for ch in carla] == [40000, 40000], f"8 credits x 100,00 / 2: {carla}")

    paused = await c.call("PATCH", f"/tuition/plans/{credit_plan['id']}", 200, "deactivate plan", admin, json={"is_active": False})
    c.expect(paused["is_active"] is False, f"inactive: {paused}")
    await c.call("POST", f"/tuition/plans/{credit_plan['id']}/generate", 409, "inactive plan", admin)


async def check_composition_and_settlement(c: Checker, h: dict, ctx: dict) -> None:
    sec, admin = h["secretaria"], h["admin"]
    ana = await c.call("GET", f"/tuition/enrollments/{ctx['enrollments']['ana']}/charges", 200, "ana statement", sec)
    monthly = [ch for ch in ana if ch["description"].startswith("Mensalidade EF")]
    first = monthly[0]
    c.expect((first["gross_amount_cents"], first["discount_cents"], first["punctuality_discount_cents"], first["amount_cents"]) == (100000, 50000, 5000, 50000),
             f"scholarship and punctuality: {first}")
    c.expect(first["payer"] and first["payer"]["name"] == "Maria" and first["due_on"] == "2027-02-10", f"payer and due date: {first}")
    c.expect([ch["due_on"] for ch in monthly] == ["2027-02-10", "2027-03-10", "2027-04-10"], f"monthly due dates: {monthly}")
    bia = await c.call("GET", f"/tuition/enrollments/{ctx['enrollments']['bia']}/charges", 200, "bia statement", sec)
    c.expect([ch["discount_cents"] for ch in bia if ch["description"].startswith("Mensalidade")] == [5000, 5000, 0], f"sibling validity: {bia}")
    c.expect(all(ch["payer"] is None for ch in bia), "bia pays herself")

    settings = await c.call("GET", "/tuition/settings", 200, "default late fees", sec)
    c.expect(settings == {"fine_percent": 2.0, "monthly_interest_percent": 1.0}, f"defaults: {settings}")
    await c.call("PUT", "/tuition/settings", 403, "secretary cannot change late fees", sec, json=settings)
    await c.call("PUT", "/tuition/settings", 200, "admin keeps late fees", admin, json={"fine_percent": 2, "monthly_interest_percent": 1})

    on_time = await c.call("GET", f"/tuition/charges/{first['id']}/quote", 200, "quote on time", h["maria"], params={"on": "2027-02-10"})
    c.expect(on_time["total_cents"] == 45000, f"punctuality applies: {on_time}")
    late = await c.call("GET", f"/tuition/charges/{first['id']}/quote", 200, "quote late", h["ana"], params={"on": "2027-03-12"})
    c.expect((late["fine_cents"], late["interest_cents"], late["total_cents"]) == (1000, 500, 51500), f"fine and interest: {late}")
    await c.call("GET", f"/tuition/charges/{first['id']}/quote", 404, "other student cannot quote", h["bia"])
    await c.call("POST", f"/tuition/charges/{first['id']}/settle", 403, "secretary cannot settle", sec, json={"paid_on": "2027-02-10"})
    paid = await c.call("POST", f"/tuition/charges/{first['id']}/settle", 200, "settle on time", admin, json={"paid_on": "2027-02-10", "payment_method": "pix"})
    c.expect(paid["status"] == "paid" and paid["amount_paid_cents"] == 45000, f"paid on time: {paid}")
    await c.call("POST", f"/tuition/charges/{first['id']}/settle", 409, "settle twice", admin, json={})
    bia_first = bia[0]
    late_paid = await c.call("POST", f"/tuition/charges/{bia_first['id']}/settle", 200, "settle late", admin, json={"paid_on": "2027-03-12"})
    c.expect((late_paid["fine_cents"], late_paid["interest_cents"], late_paid["amount_paid_cents"]) == (1900, 950, 97850), f"late payment: {late_paid}")


async def check_statements(c: Checker, h: dict, ctx: dict) -> None:
    maria = await c.call("GET", "/tuition/my/charges", 200, "guardian statement", h["maria"])
    c.expect(len(maria) == 4 and all(ch["student"]["name"] == "Ana" for ch in maria), f"payer sees dependent charges: {maria}")
    c.expect(maria[0]["status"] == "paid" and maria[0]["quote"] is None and maria[1]["quote"] is not None, f"quote only for open charges: {maria[:2]}")
    ana = await c.call("GET", "/tuition/my/charges", 200, "student statement", h["ana"])
    c.expect(len(ana) == 4, f"student sees own charges: {ana}")
    carla = await c.call("GET", "/tuition/my/charges", 200, "credit student", h["carla"])
    c.expect(len(carla) == 2, f"carla: {carla}")
    await c.call("GET", f"/tuition/enrollments/{ctx['enrollments']['ana']}/charges", 403, "student cannot read office statement", h["ana"])
    portal = await c.call("GET", f"/guardians/me/dependents/{ctx['ids']['ana']}/charges", 200, "guardian portal charges", h["maria"])
    c.expect(len(portal) == 4, f"portal: {portal}")


async def run() -> int:
    ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with ApiClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        h = {name: await c.login(f"{name}@example.com") for name, _ in USERS}
        ctx = await setup_structure(c, h, ids)
        ctx["ids"] = ids
        h["maria"] = await c.login("maria@example.com")
        await check_discounts(c, h, ctx)
        await check_plans_and_generation(c, h, ctx)
        await check_composition_and_settlement(c, h, ctx)
        await check_statements(c, h, ctx)

    if c.failures:
        print("Tuition flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Tuition flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
