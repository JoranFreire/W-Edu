"""Exercise social programs (phase 18, delivery 2): funding source, benefit items and stock, deliveries (snack only to
those present), absence-based dismissal when meetings close, risk levels, readmission and the funder's report.

Uses a temporary SQLite database by default (set DATABASE_URL to use PostgreSQL).
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import os
import tempfile
from pathlib import Path
import sys

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_social_check_{os.getpid()}.sqlite3"
    os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["NOTIFICATION_WORKER_ENABLED"] = "false"
os.environ["MINIMUM_WAGE_API_URL"] = ""  # sem rede: vale a tabela local (vazia aqui, entao o valor de reserva)
os.environ.setdefault("DOCUMENTS_STORAGE_DIR", tempfile.mkdtemp(prefix="wedu_admissions_"))

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
from app.models.notification import NotificationEvent, NotificationEventType
from app.models.reference_values import MinimumWageValue
from app.models.schedule import ClassEnrollment, ClassEnrollmentStatus
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
USERS = (("coord", UserRole.coordinator), ("secretaria", UserRole.secretary), ("prof", UserRole.instructor), ("outro", UserRole.instructor),
         *((f"a{i}", UserRole.student) for i in range(1, 6)))


def seed() -> dict[str, int]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ids = {}
    with SessionLocal() as db:
        institution = Institution(slug="instituto", name="Instituto Social", type=InstitutionType.vocational)
        db.add(institution)
        db.flush()
        for name, role in USERS:
            user = Student(name=name.title(), email=f"{name}@example.com", password_hash=hash_password(PASSWORD), role=role)
            db.add(user)
            db.flush()
            db.add(InstitutionMembership(institution_id=institution.id, user_id=user.id, role=role))
            ids[name] = user.id
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


def iso(delta: timedelta) -> str:
    return (datetime.now(timezone.utc) + delta).isoformat()


async def setup(c: Checker, h: dict, ids: dict) -> dict:
    """Financiador, turma financiada (limite de 40% de faltas) e quatro alunos matriculados pelo edital."""
    coord, sec = h["coord"], h["secretaria"]
    await c.call("POST", "/social/funding-sources", 403, "secretary cannot create funding", sec, json={"name": "X", "starts_on": "2027-01-01"})
    funding = await c.call("POST", "/social/funding-sources", 201, "funding", coord, json={
        "name": "Convênio Prefeitura", "kind": "government", "agreement_number": "123/2027", "amount_cents": 100000, "starts_on": "2027-01-01"})
    course = await c.call("POST", "/courses", 201, "course", coord, json={"name": "Auxiliar de cozinha"})
    await c.call("POST", "/schedule/classes", 404, "unknown funding", coord, json={
        "course_id": course["id"], "name": "X", "capacity": 10, "starts_at": "2027-03-01T08:00:00Z", "ends_at": "2027-06-30T12:00:00Z",
        "funding_source_id": 9999})
    offering = await c.call("POST", "/schedule/classes", 201, "funded offering", coord, json={
        "course_id": course["id"], "name": "Cozinha 2027", "capacity": 10, "status": "open", "instructor_id": ids["prof"],
        "starts_at": "2027-03-01T08:00:00Z", "ends_at": "2027-06-30T12:00:00Z", "funding_source_id": funding["id"], "max_absence_percent": 40,
    })
    c.expect(offering.get("funding_source_id") == funding["id"] and offering.get("max_absence_percent") == 40, f"offering: {offering}")
    call = await c.call("POST", "/admissions/calls", 201, "call", sec, json={
        "class_offering_id": offering["id"], "title": "Cozinha", "seats": 4, "opens_at": iso(-timedelta(hours=1)), "closes_at": iso(timedelta(hours=1))})
    await c.call("POST", f"/admissions/calls/{call['id']}/status", 200, "open", sec, json={"status": "open"})
    births = {"a1": "2009-01-01", "a2": "2000-01-01", "a3": "1990-01-01", "a4": "1960-01-01", "a5": "1995-01-01"}
    applications = {}
    for name in ("a1", "a2", "a3", "a4", "a5"):
        applications[name] = await c.call("POST", f"/admissions/calls/{call['id']}/apply", 201, f"{name} applies", h[name], json={
            "birth_date": births[name], "schooling": "elementary", "family_income_cents": 120000, "household_size": 4, "city": "Recife"})
    await c.call("POST", f"/admissions/calls/{call['id']}/status", 200, "close", sec, json={"status": "closed"})
    await c.call("POST", f"/admissions/calls/{call['id']}/select", 200, "select", sec)
    for name in ("a1", "a2", "a3", "a4"):
        await c.call("POST", f"/admissions/my/applications/{applications[name]['id']}/confirm", 200, f"{name} confirms", h[name])
    return {"funding": funding["id"], "offering": offering["id"]}


async def check_benefits(c: Checker, h: dict, ids: dict, ctx: dict) -> dict:
    sec, prof = h["secretaria"], h["prof"]
    await c.call("POST", "/social/benefit-items", 403, "student cannot create item", h["a1"], json={"name": "X"})
    snack = await c.call("POST", "/social/benefit-items", 201, "snack", sec,
                         json={"name": "Lanche", "kind": "snack", "unit_cost_cents": 500, "requires_attendance": True})
    kit = await c.call("POST", "/social/benefit-items", 201, "kit", sec, json={"name": "Kit de material", "kind": "material", "unit": "kit", "unit_cost_cents": 3000})
    stocked = await c.call("POST", f"/social/benefit-items/{snack['id']}/stock", 201, "snack stock", sec,
                           json={"quantity": 10, "funding_source_id": ctx["funding"], "received_on": "2027-02-20"})
    c.expect(stocked["stock"] == 10, f"stock: {stocked}")
    await c.call("POST", f"/social/benefit-items/{kit['id']}/stock", 201, "kit donation", sec, json={"quantity": 3, "origin": "donation", "received_on": "2027-02-20"})
    await c.call("POST", f"/social/benefit-items/{kit['id']}/stock", 404, "unknown funding", sec, json={"quantity": 1, "funding_source_id": 9999, "received_on": "2027-02-20"})
    entries = await c.call("GET", f"/social/benefit-items/{kit['id']}/stock", 200, "kit entries", sec)
    c.expect(len(entries) == 1 and entries[0]["unit_cost_cents"] == 3000, f"entries: {entries}")
    items = await c.call("GET", "/social/benefit-items", 200, "instructor lists items", prof)
    c.expect({i["name"]: i["stock"] for i in items} == {"Kit de material": 3, "Lanche": 10}, f"items: {items}")
    return {"snack": snack["id"], "kit": kit["id"]}


async def schedule_meetings(c: Checker, h: dict, ctx: dict) -> list[int]:
    """Tres encontros previstos: o limite de faltas vale sobre o curso inteiro."""
    meetings = []
    for day in (1, 2, 3):
        created = await c.call("POST", "/schedule/meetings", 201, f"meeting {day}", h["coord"], json={
            "class_offering_id": ctx["offering"], "title": f"Aula {day}",
            "starts_at": f"2027-03-0{day}T08:00:00Z", "ends_at": f"2027-03-0{day}T10:00:00Z"})
        meetings.append(created["id"])
    return meetings


async def attend(c: Checker, h: dict, ids: dict, meeting_id: int, present: list[str]) -> int:
    for name in present:
        await c.call("POST", f"/schedule/meetings/{meeting_id}/attendance", 201, f"{name} present", h["coord"], json={"student_id": ids[name]})
    return meeting_id


async def check_deliveries_and_retention(c: Checker, h: dict, ids: dict, ctx: dict, items: dict) -> None:
    prof, sec = h["prof"], h["secretaria"]
    first_id, second_id, third_id = await schedule_meetings(c, h, ctx)
    first = await attend(c, h, ids, first_id, ["a1", "a2", "a3"])
    await c.call("POST", f"/schedule/meetings/{first}/close", 200, "close meeting 1", h["coord"])
    with SessionLocal() as db:
        early = db.query(ClassEnrollment).filter(ClassEnrollment.student_id == ids["a4"], ClassEnrollment.class_offering_id == ctx["offering"]).one()
        c.expect(early.status == ClassEnrollmentStatus.active, "one absence in three planned meetings does not dismiss")
    await c.call("POST", f"/social/meetings/{first}/deliveries", 403, "other instructor", h["outro"], json={"item_id": items["snack"]})
    snack = await c.call("POST", f"/social/meetings/{first}/deliveries", 200, "snack to those present", prof, json={"item_id": items["snack"]})
    c.expect(snack == {"delivered": 3, "remaining_stock": 7}, f"snack: {snack}")
    again = await c.call("POST", f"/social/meetings/{first}/deliveries", 200, "no double snack", prof, json={"item_id": items["snack"]})
    c.expect(again["delivered"] == 0, f"idempotent: {again}")
    short = await c.call("POST", f"/social/meetings/{first}/deliveries", 409, "kit for everyone exceeds stock", prof, json={"item_id": items["kit"]})
    c.expect("3 disponível(is), 4 necessário(s)" in short.get("detail", ""), f"stock message: {short}")
    await c.call("POST", "/social/deliveries", 201, "kit to a1", prof, json={"item_id": items["kit"], "student_id": ids["a1"], "class_offering_id": ctx["offering"]})
    await c.call("POST", "/social/deliveries", 404, "not enrolled", prof, json={"item_id": items["kit"], "student_id": ids["a5"], "class_offering_id": ctx["offering"]})
    mine = await c.call("GET", "/social/my/benefits", 200, "a1 benefits", h["a1"])
    c.expect(sorted(d["item_name"] for d in mine) == ["Kit de material", "Lanche"], f"a1 benefits: {mine}")
    listed = await c.call("GET", f"/social/offerings/{ctx['offering']}/deliveries", 200, "offering deliveries", sec)
    c.expect(len(listed) == 4, f"deliveries: {listed}")

    second = await attend(c, h, ids, second_id, ["a1", "a2", "a3"])
    await c.call("POST", f"/schedule/meetings/{second}/close", 200, "close meeting 2", h["coord"])
    with SessionLocal() as db:
        dismissed = db.query(ClassEnrollment).filter(ClassEnrollment.student_id == ids["a4"], ClassEnrollment.class_offering_id == ctx["offering"]).one()
        c.expect(dismissed.status == ClassEnrollmentStatus.cancelled and dismissed.dismissed_at is not None, "a4 dismissed after 2 absences of 3 planned")
        notices = db.query(NotificationEvent).filter(NotificationEvent.event_type == NotificationEventType.absence_dismissal).count()
    c.expect(notices == 1, f"dismissal notice: {notices}")
    third = await attend(c, h, ids, third_id, ["a1", "a2"])
    await c.call("POST", f"/schedule/meetings/{third}/close", 200, "close meeting 3", h["coord"])
    report = await c.call("GET", f"/retention/offerings/{ctx['offering']}", 200, "retention report", prof)
    rows = {row["student"]["name"]: row for row in report["rows"]}
    c.expect(rows["A3"]["level"] == "attention" and rows["A3"]["absence_percent"] == 33.3 and rows["A3"]["status"] == "active", f"a3: {rows.get('A3')}")
    c.expect(rows["A1"]["level"] == "ok" and rows["A4"]["dismissed_at"] and rows["A4"]["level"] == "exceeded", f"rows: {rows}")
    await c.call("GET", f"/retention/offerings/{ctx['offering']}", 403, "other instructor", h["outro"])
    evaluation = await c.call("POST", f"/retention/offerings/{ctx['offering']}/evaluate", 200, "evaluate", sec)
    c.expect(evaluation == {"dismissed": []}, f"nothing new: {evaluation}")
    ctx["a4_enrollment"] = rows["A4"]["class_enrollment_id"]


async def check_report(c: Checker, h: dict, ctx: dict) -> None:
    sec = h["secretaria"]
    report = await c.call("GET", f"/social/funding-sources/{ctx['funding']}/report", 200, "funding report", sec)
    totals = report["totals"]
    c.expect((totals["applications"], totals["enrolled"], totals["active"], totals["dismissed"], totals["evasion_rate"]) == (5, 4, 3, 1, 25.0), f"totals: {totals}")
    profile = report["profile"]
    c.expect(profile["respondents"] == 4 and profile["income_per_capita"]["até 1/4 SM"] == 4, f"income: {profile}")
    c.expect(profile["age"]["até 17"] == 1 and profile["age"]["60 ou mais"] == 1, f"age: {profile['age']}")
    usage = {b["item_name"]: (b["quantity"], b["cost_cents"]) for b in report["benefits"]}
    c.expect(usage == {"Kit de material": (1, 3000), "Lanche": (3, 1500)}, f"usage: {usage}")
    c.expect(report["minimum_wage_source"] == "fallback" and report["minimum_wage_cents"] == 162100, f"fallback wage: {report}")
    informed = await c.call("GET", f"/social/funding-sources/{ctx['funding']}/report", 200, "informed wage", sec, params={"minimum_wage_cents": 100000})
    c.expect(informed["minimum_wage_source"] == "informed" and informed["profile"]["income_per_capita"]["1/4 a 1/2 SM"] == 4, f"informed: {informed['profile']}")
    c.expect(report["benefits_cost_cents"] == 4500 and report["budget_balance_cents"] == 95500 and report["stock_received_cents"] == 5000, f"money: {report}")
    response = await c.client.get(f"/social/funding-sources/{ctx['funding']}/report.csv", headers=sec)
    c.expect(response.status_code == 200 and "Cozinha 2027;5;4;3;0;1;0;25,0" in response.text, f"csv: {response.text[:300]}")
    await c.call("GET", f"/social/funding-sources/{ctx['funding']}/report", 403, "instructor cannot read report", h["prof"])

    readmitted = await c.call("POST", f"/retention/enrollments/{ctx['a4_enrollment']}/readmit", 200, "readmit a4", sec)
    c.expect(readmitted["status"] == "active" and readmitted["dismissed_at"] is None, f"readmitted: {readmitted}")
    await c.call("POST", f"/retention/enrollments/{ctx['a4_enrollment']}/readmit", 409, "readmit twice", sec)


def check_minimum_wage(c: Checker) -> None:
    """Tabela local do salario minimo: grava so mudancas, vale o ultimo valor ate a data e funciona sem a API."""
    from datetime import date
    from app.repositories.reference import MinimumWageRepository
    from app.services.social.minimum_wage import MinimumWageProvider, parse_points

    payload = [{"data": "01/12/2025", "valor": "1518.00"}, {"data": "01/01/2026", "valor": "1621.00"}, {"data": "01/02/2026", "valor": "1621.00"}]
    points = parse_points(payload)
    c.expect(points[1] == (date(2026, 1, 1), 162100), f"parse: {points}")
    with SessionLocal() as db:
        repo = MinimumWageRepository(db)
        repo.upsert(points, datetime.now(timezone.utc))
        repo.upsert(points, datetime.now(timezone.utc))
        stored = [(row.valid_from, row.cents) for row in db.query(MinimumWageValue).order_by(MinimumWageValue.valid_from)]
        c.expect(stored == [(date(2025, 12, 1), 151800), (date(2026, 1, 1), 162100)], f"only changes are stored: {stored}")
        current = MinimumWageProvider(db).current(date(2026, 10, 1))
        c.expect((current.cents, current.source) == (162100, "bcb"), f"table value without the API: {current}")
        before = MinimumWageProvider(db).current(date(2020, 1, 1))
        c.expect(before.source == "fallback", f"no value before the series: {before}")


async def run() -> int:
    ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        h = {name: await c.login(f"{name}@example.com") for name, _ in USERS}
        ctx = await setup(c, h, ids)
        items = await check_benefits(c, h, ids, ctx)
        await check_deliveries_and_retention(c, h, ids, ctx, items)
        await check_report(c, h, ctx)
        check_minimum_wage(c)

    if c.failures:
        print("Social programs flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Social programs flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
