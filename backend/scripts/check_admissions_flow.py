"""Exercise free-course admissions (phase 18, delivery 1): public catalog and signup, calls with requirements and reserved
seats, documents, selection by order, lottery and review, public result, confirmation, declines and successive calls.

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
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_admissions_check_{os.getpid()}.sqlite3"
    os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["NOTIFICATION_WORKER_ENABLED"] = "false"
os.environ.setdefault("DOCUMENTS_STORAGE_DIR", tempfile.mkdtemp(prefix="wedu_admissions_"))

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
from app.models.admissions import AdmissionApplication, SelectionMethod
from app.models.notification import NotificationEvent, NotificationEventType
from app.models.schedule import ClassEnrollment
from app.services.admissions.rules import Candidate, rank
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
HOST = {"X-Institution": "instituto"}
APPLICANTS = [f"a{i}" for i in range(1, 8)]


def seed() -> dict[str, int]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ids = {}
    with SessionLocal() as db:
        institution = Institution(slug="instituto", name="Instituto Social", type=InstitutionType.vocational)
        db.add(institution)
        db.flush()
        for name, role in (("secretaria", UserRole.secretary), ("coord", UserRole.coordinator)):
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


def iso(delta: timedelta) -> str:
    return (datetime.now(timezone.utc) + delta).isoformat()


def answers(**overrides) -> dict:
    return {"birth_date": "2000-05-10", "schooling": "high_school", "family_income_cents": 200000, "household_size": 4,
            "city": "Recife", **overrides}


async def signup_applicants(c: Checker) -> dict[str, dict]:
    """Candidatos criam a conta pelo cadastro publico da instituicao (como na pagina de inscricoes)."""
    headers = {}
    for name in APPLICANTS:
        await c.call("POST", "/users", 201, f"signup {name}", HOST, json={"name": name.upper(), "email": f"{name}@example.com", "password": PASSWORD})
        headers[name] = await c.login(f"{name}@example.com")
    return headers


async def new_call(c: Checker, sec: dict, offering_id: int, **fields) -> dict:
    payload = {"class_offering_id": offering_id, "title": "Edital", "seats": 1, "opens_at": iso(-timedelta(hours=1)),
               "closes_at": iso(timedelta(hours=1)), **fields}
    call = await c.call("POST", "/admissions/calls", 201, f"create {payload['title']}", sec, json=payload)
    await c.call("POST", f"/admissions/calls/{call['id']}/status", 200, "open call", sec, json={"status": "open"})
    return call


async def close(c: Checker, sec: dict, call_id: int) -> None:
    await c.call("POST", f"/admissions/calls/{call_id}/status", 200, "close call", sec, json={"status": "closed"})


async def check_first_come(c: Checker, h: dict, offering_id: int) -> None:
    sec = h["secretaria"]
    payload = {"class_offering_id": offering_id, "title": "Auxiliar administrativo", "seats": 3, "reserved_seats": 1,
               "reserved_label": "Renda até meio salário", "opens_at": iso(-timedelta(hours=1)), "closes_at": iso(timedelta(hours=1)),
               "min_age": 16, "max_income_per_capita_cents": 150000, "required_city": "Recife", "required_documents": ["RG"]}
    await c.call("POST", "/admissions/calls", 403, "applicant cannot create call", h["a1"], json=payload)
    await c.call("POST", "/admissions/calls", 400, "more seats than the class", sec, json={**payload, "seats": 99})
    await c.call("POST", "/admissions/calls", 422, "reserve above seats", sec, json={**payload, "reserved_seats": 5})
    call = await c.call("POST", "/admissions/calls", 201, "draft call", sec, json=payload)
    cid = call["id"]
    catalog = await c.call("GET", "/admissions/public/calls", 200, "public catalog", HOST)
    c.expect(catalog == [], f"draft hidden: {catalog}")
    await c.call("POST", f"/admissions/calls/{cid}/apply", 409, "apply to draft", h["a1"], json=answers())
    await c.call("POST", f"/admissions/calls/{cid}/status", 200, "open", sec, json={"status": "open"})
    catalog = await c.call("GET", "/admissions/public/calls", 200, "public catalog open", HOST)
    c.expect([x["title"] for x in catalog] == ["Auxiliar administrativo"] and catalog[0]["is_accepting"], f"catalog: {catalog}")
    by_param = await c.call("GET", "/admissions/public/calls", 200, "catalog by query param", {}, params={"institution": "instituto"})
    c.expect(len(by_param) == 1, f"query param: {by_param}")
    await c.call("GET", "/admissions/public/calls", 404, "unknown institution", {"X-Institution": "nao-existe"})

    apps = {}
    for name in ("a1", "a2", "a3", "a4", "a5"):
        apps[name] = await c.call("POST", f"/admissions/calls/{cid}/apply", 201, f"{name} applies", h[name],
                                  json=answers(city="recife", claims_reserved=name in ("a4", "a5")))
    c.expect(all(a["status"] == "submitted" for a in apps.values()), f"eligible: {[a['status'] for a in apps.values()]}")
    young = await c.call("POST", f"/admissions/calls/{cid}/apply", 201, "a6 too young", h["a6"], json=answers(birth_date="2015-01-01"))
    c.expect(young["status"] == "ineligible" and young["ineligibility_reasons"] == ["Idade mínima de 16 anos"], f"age: {young}")
    away = await c.call("POST", f"/admissions/calls/{cid}/apply", 201, "a7 other city and income", h["a7"],
                        json=answers(city="Olinda", family_income_cents=900000, household_size=2))
    c.expect(set(away["ineligibility_reasons"]) == {"Exige morar em Recife", "Renda por pessoa acima do limite"}, f"reasons: {away}")
    await c.call("POST", f"/admissions/calls/{cid}/apply", 409, "apply twice", h["a1"], json=answers())
    withdrawn = await c.call("POST", f"/admissions/my/applications/{away['id']}/withdraw", 200, "a7 withdraws", h["a7"])
    c.expect(withdrawn["status"] == "withdrawn", f"withdrawn: {withdrawn}")

    files = {"file": ("rg.pdf", b"%PDF-1.4 rg", "application/pdf")}
    uploaded = await c.call("POST", f"/admissions/my/applications/{apps['a1']['id']}/documents", 201, "upload RG", h["a1"], data={"kind": "RG"}, files=files)
    document_id = uploaded["documents"][0]["id"]
    await c.call("POST", f"/admissions/my/applications/{apps['a1']['id']}/documents", 400, "wrong type", h["a1"],
                 data={"kind": "RG"}, files={"file": ("virus.exe", b"MZ", "application/octet-stream")})
    await c.call("POST", f"/admissions/my/applications/{apps['a1']['id']}/documents", 404, "other applicant", h["a2"], data={"kind": "RG"}, files=files)
    reviewed = await c.call("POST", f"/admissions/documents/{document_id}/review", 200, "accept RG", sec, json={"review": "accepted"})
    c.expect(reviewed["documents"][0]["review"] == "accepted", f"doc review: {reviewed}")
    download = await c.client.get(f"/admissions/documents/{document_id}/download", headers=sec)
    c.expect(download.status_code == 200 and download.content == b"%PDF-1.4 rg", f"download: {download.status_code}")
    await c.call("GET", f"/admissions/documents/{document_id}/download", 403, "applicant cannot use office download", h["a1"])

    await c.call("POST", f"/admissions/applications/{apps['a4']['id']}/review", 200, "reserve not proven", sec, json={"reserved_verified": False})
    await c.call("POST", f"/admissions/applications/{apps['a5']['id']}/review", 200, "reserve proven", sec, json={"reserved_verified": True})
    await c.call("POST", f"/admissions/applications/{apps['a1']['id']}/review", 400, "score needs review method", sec, json={"review_score": 10})
    await c.call("POST", f"/admissions/applications/{apps['a3']['id']}/review", 400, "ineligible needs reason", sec, json={"eligible": False})

    await c.call("POST", f"/admissions/calls/{cid}/select", 409, "select while open", sec)
    await c.call("GET", f"/admissions/public/calls/{cid}/result", 404, "no result yet", HOST)
    await close(c, sec, cid)
    selection = await c.call("POST", f"/admissions/calls/{cid}/select", 200, "select", sec)
    c.expect(selection == {"ranked": 5, "called": 3, "waitlisted": 2}, f"selection: {selection}")
    await c.call("POST", f"/admissions/calls/{cid}/select", 409, "select twice", sec)
    listed = {a["applicant"]["name"]: a for a in await c.call("GET", f"/admissions/calls/{cid}/applications", 200, "office list", sec)}
    picked = {name: (a["status"], a["seat_kind"]) for name, a in listed.items() if a["status"] == "selected"}
    c.expect(picked == {"A5": ("selected", "reserved"), "A1": ("selected", "general"), "A2": ("selected", "general")}, f"called: {picked}")
    c.expect([listed[n]["rank"] for n in ("A1", "A2", "A3", "A4", "A5")] == [1, 2, 3, 4, 5], "first come ranking")
    result = await c.call("GET", f"/admissions/public/calls/{cid}/result", 200, "public result", HOST)
    c.expect(len(result["entries"]) == 5 and "applicant" not in result["entries"][0] and result["lottery_seed"] is None, f"result: {result}")
    with SessionLocal() as db:
        called = db.query(NotificationEvent).filter(NotificationEvent.event_type == NotificationEventType.admission_called).count()
    c.expect(called == 3, f"called notices: {called}")

    confirmed = await c.call("POST", f"/admissions/my/applications/{apps['a1']['id']}/confirm", 200, "a1 confirms", h["a1"])
    c.expect(confirmed["status"] == "confirmed", f"confirmed: {confirmed}")
    with SessionLocal() as db:
        enrolled = db.query(ClassEnrollment).filter(ClassEnrollment.class_offering_id == offering_id).count()
    c.expect(enrolled == 1, f"enrolled in class: {enrolled}")
    await c.call("POST", f"/admissions/my/applications/{apps['a3']['id']}/confirm", 409, "waitlisted cannot confirm", h["a3"])
    await c.call("POST", f"/admissions/my/applications/{apps['a5']['id']}/decline", 200, "a5 declines reserved seat", h["a5"])
    listed = {a["applicant"]["name"]: a for a in await c.call("GET", f"/admissions/calls/{cid}/applications", 200, "after decline", sec)}
    c.expect(listed["A3"]["status"] == "selected" and listed["A3"]["seat_kind"] == "general", f"reserve without claimant goes general: {listed['A3']}")

    with SessionLocal() as db:
        late = db.get(AdmissionApplication, apps["a2"]["id"])
        late.confirm_until = datetime.now(timezone.utc) - timedelta(minutes=1)
        db.commit()
    await c.call("POST", f"/admissions/my/applications/{apps['a2']['id']}/confirm", 409, "a2 missed the deadline", h["a2"])
    listed = {a["applicant"]["name"]: a for a in await c.call("GET", f"/admissions/calls/{cid}/applications", 200, "after deadline", sec)}
    c.expect(listed["A2"]["status"] == "expired" and listed["A4"]["status"] == "selected", f"successive call: {[(n, a['status']) for n, a in listed.items()]}")
    again = await c.call("POST", f"/admissions/calls/{cid}/process-deadlines", 200, "nothing to expire", sec)
    c.expect(again == {"expired": 0, "called": 0, "waitlisted": 0}, f"deadlines: {again}")
    mine = await c.call("GET", "/admissions/my/applications", 200, "my applications", h["a4"])
    c.expect(mine[0]["status"] == "selected" and mine[0]["confirm_until"], f"a4 sees call: {mine}")


async def check_lottery(c: Checker, h: dict, offering_id: int) -> None:
    sec = h["secretaria"]
    call = await new_call(c, sec, offering_id, title="Sorteio informática", method="lottery", seats=2)
    ids = []
    for name in ("a1", "a2", "a3", "a4", "a6"):
        ids.append((await c.call("POST", f"/admissions/calls/{call['id']}/apply", 201, f"{name} lottery", h[name], json=answers()))["id"])
    await close(c, sec, call["id"])
    await c.call("POST", f"/admissions/calls/{call['id']}/select", 200, "draw", sec)
    result = await c.call("GET", f"/admissions/public/calls/{call['id']}/result", 200, "lottery result", HOST)
    seed = result["lottery_seed"]
    c.expect(bool(seed), "seed published")
    with SessionLocal() as db:
        applications = db.query(AdmissionApplication).filter(AdmissionApplication.call_id == call["id"]).all()
        candidates = [Candidate(a.id, a.created_at, None, False) for a in applications]
        by_id = {a.id: a.rank for a in applications}
    redraw = [cand.id for cand in rank(candidates, SelectionMethod.lottery, seed)]
    c.expect([by_id[i] for i in redraw] == [1, 2, 3, 4, 5], "anyone can reproduce the draw from the seed")
    c.expect(sum(1 for e in result["entries"] if e["status"] == "selected") == 2, f"two called: {result}")


async def check_review(c: Checker, h: dict, offering_id: int) -> None:
    sec = h["secretaria"]
    call = await new_call(c, sec, offering_id, title="Análise de perfil", method="review", seats=1)
    first = await c.call("POST", f"/admissions/calls/{call['id']}/apply", 201, "a6 review", h["a6"], json=answers())
    second = await c.call("POST", f"/admissions/calls/{call['id']}/apply", 201, "a7 review", h["a7"], json=answers())
    await close(c, sec, call["id"])
    await c.call("POST", f"/admissions/calls/{call['id']}/select", 409, "scores missing", sec)
    await c.call("POST", f"/admissions/applications/{first['id']}/review", 200, "score a6", sec, json={"review_score": 50})
    await c.call("POST", f"/admissions/applications/{second['id']}/review", 200, "score a7", sec, json={"review_score": 80})
    await c.call("POST", f"/admissions/calls/{call['id']}/select", 200, "select by score", sec)
    listed = {a["applicant"]["name"]: a for a in await c.call("GET", f"/admissions/calls/{call['id']}/applications", 200, "review list", sec)}
    c.expect(listed["A7"]["status"] == "selected" and listed["A7"]["rank"] == 1 and listed["A6"]["status"] == "waitlisted", f"review: {listed}")
    await c.call("POST", f"/admissions/applications/{first['id']}/review", 409, "no review after selection", sec, json={"review_score": 99})


async def run() -> int:
    seed()
    transport = httpx.ASGITransport(app=app)
    async with ApiClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        h = {"secretaria": await c.login("secretaria@example.com"), "coord": await c.login("coord@example.com")}
        h.update(await signup_applicants(c))
        course = await c.call("POST", "/courses", 201, "course", h["coord"], json={"name": "Auxiliar administrativo"})
        offering = await c.call("POST", "/schedule/classes", 201, "offering", h["coord"], json={
            "course_id": course["id"], "name": "Turma 2027", "capacity": 20, "status": "open",
            "starts_at": "2027-03-01T08:00:00Z", "ends_at": "2027-06-30T12:00:00Z",
        })
        await check_first_come(c, h, offering["id"])
        await check_lottery(c, h, offering["id"])
        await check_review(c, h, offering["id"])

    if c.failures:
        print("Admissions flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Admissions flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
