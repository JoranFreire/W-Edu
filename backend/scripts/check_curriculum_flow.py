"""Exercise the curricular structure (phase 12) through real requests.

Academic units, programs, subjects with prerequisites and equivalences, and the
versioned curriculum lifecycle. Uses a temporary SQLite database by default
(set DATABASE_URL to use PostgreSQL).
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
import sys

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_curriculum_check_{os.getpid()}.sqlite3"
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
from app.models.institution import Institution, InstitutionMembership
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


def seed() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        institution = Institution(slug="faculdade", name="Faculdade")
        db.add(institution)
        db.flush()
        for name, role in (("admin", UserRole.institution_admin), ("coord", UserRole.coordinator), ("aluno", UserRole.student)):
            user = Student(name=name, email=f"{name}@example.com", password_hash=hash_password(PASSWORD), role=role)
            db.add(user)
            db.flush()
            db.add(InstitutionMembership(institution_id=institution.id, user_id=user.id, role=role))
        db.commit()


class Checker:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client
        self.failures: list[str] = []

    def expect(self, condition: bool, message: str) -> None:
        if not condition:
            self.failures.append(message)

    async def login(self, name: str) -> dict:
        response = await self.client.post("/auth/login", json={"email": f"{name}@example.com", "password": PASSWORD})
        assert response.status_code == 200, f"login {name}: {response.status_code} {response.text}"
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    async def create(self, path: str, payload: dict, headers: dict) -> int:
        response = await self.client.post(path, json=payload, headers=headers)
        self.expect(response.status_code == 201, f"POST {path}: {response.status_code} {response.text}")
        return response.json().get("id", 0)


async def check_units_and_programs(c: Checker, coord: dict, admin: dict) -> int:
    client = c.client
    faculty = await c.create("/academic/units", {"name": "Faculdade de Direito", "kind": "faculty"}, coord)
    department = await c.create("/academic/units", {"name": "Direito Privado", "kind": "department", "parent_id": faculty}, coord)
    r = await client.patch(f"/academic/units/{faculty}", json={"parent_id": department}, headers=coord)
    c.expect(r.status_code == 400, f"unit hierarchy cycle rejected: {r.status_code}")
    r = await client.delete(f"/academic/units/{faculty}", headers=admin)
    c.expect(r.status_code == 409, f"unit with children cannot be deleted: {r.status_code}")

    program = await c.create(
        "/academic/programs",
        {"code": "DIR", "name": "Bacharelado em Direito", "level": "undergraduate", "unit_id": faculty, "duration_terms": 2},
        coord,
    )
    r = await client.post("/academic/programs", json={"code": "DIR", "name": "Outro"}, headers=coord)
    c.expect(r.status_code == 409, f"duplicate program code: {r.status_code}")
    r = await client.patch(f"/academic/programs/{program}", json={"degree": "Bacharel"}, headers=coord)
    c.expect(r.status_code == 200 and r.json()["unit_id"] == faculty, f"partial update keeps unit: {r.text}")
    r = await client.get("/academic/programs", params={"level": "undergraduate"}, headers=coord)
    c.expect([p["code"] for p in r.json()] == ["DIR"], f"filter programs by level: {r.json()}")
    r = await client.delete(f"/academic/units/{department}", headers=admin)
    c.expect(r.status_code == 204, f"leaf unit deleted: {r.status_code}")
    return program


async def check_subjects(c: Checker, coord: dict) -> dict[str, int]:
    client = c.client
    subjects = {}
    for code, hours, credits in (("CIV1", 60, 4), ("CIV2", 60, 4), ("CIV3", 80, 5), ("PEN1", 40, None), ("OLD", 30, 2)):
        subjects[code] = await c.create("/academic/subjects", {"code": code, "name": f"Disciplina {code}", "hours": hours, "credits": credits}, coord)
    r = await client.post("/academic/subjects", json={"code": "CIV1", "name": "Dup"}, headers=coord)
    c.expect(r.status_code == 409, f"duplicate subject code: {r.status_code}")
    r = await client.get("/academic/subjects", params={"search": "civ"}, headers=coord)
    c.expect([s["code"] for s in r.json()] == ["CIV1", "CIV2", "CIV3"], f"search subjects: {r.json()}")

    prereq = "/academic/subjects/{}/prerequisites"
    r = await client.post(prereq.format(subjects["CIV2"]), json={"subject_id": subjects["CIV1"]}, headers=coord)
    c.expect(r.status_code == 201, f"CIV2 requires CIV1: {r.status_code} {r.text}")
    r = await client.post(prereq.format(subjects["CIV3"]), json={"subject_id": subjects["CIV2"]}, headers=coord)
    c.expect(r.status_code == 201, f"CIV3 requires CIV2: {r.status_code}")
    r = await client.post(prereq.format(subjects["CIV1"]), json={"subject_id": subjects["CIV3"]}, headers=coord)
    c.expect(r.status_code == 400, f"transitive cycle rejected: {r.status_code}")
    r = await client.post(prereq.format(subjects["CIV1"]), json={"subject_id": subjects["CIV1"]}, headers=coord)
    c.expect(r.status_code == 400, f"self prerequisite rejected: {r.status_code}")
    r = await client.post(prereq.format(subjects["CIV2"]), json={"subject_id": subjects["CIV1"]}, headers=coord)
    c.expect(r.status_code == 409, f"duplicate prerequisite: {r.status_code}")
    r = await client.get(prereq.format(subjects["CIV3"]), headers=coord)
    c.expect([s["code"] for s in r.json()] == ["CIV2"], f"list prerequisites: {r.json()}")

    equiv = "/academic/subjects/{}/equivalences"
    r = await client.post(equiv.format(subjects["OLD"]), json={"subject_id": subjects["CIV1"]}, headers=coord)
    c.expect(r.status_code == 201, f"equivalence created: {r.status_code}")
    r = await client.post(equiv.format(subjects["CIV1"]), json={"subject_id": subjects["OLD"]}, headers=coord)
    c.expect(r.status_code == 409, f"equivalence is symmetric (duplicate): {r.status_code}")
    r = await client.get(equiv.format(subjects["CIV1"]), headers=coord)
    c.expect([s["code"] for s in r.json()] == ["OLD"], f"equivalence visible from both sides: {r.json()}")
    r = await client.delete(f"/academic/subjects/{subjects['CIV1']}/equivalences/{subjects['OLD']}", headers=await c.login("admin"))
    c.expect(r.status_code == 204, f"equivalence removed from the other side: {r.status_code}")
    return subjects


async def check_curricula(c: Checker, coord: dict, admin: dict, aluno: dict, program: int, subjects: dict[str, int]) -> None:
    client = c.client
    v1 = await c.create(f"/academic/programs/{program}/curricula", {"version": "2027"}, coord)
    r = await client.post(f"/academic/curricula/{v1}/activate", headers=coord)
    c.expect(r.status_code == 400, f"empty curriculum cannot be activated: {r.status_code}")

    components = f"/academic/curricula/{v1}/components"
    await c.create(components, {"subject_id": subjects["CIV1"], "term_number": 1}, coord)
    civ2 = await c.create(components, {"subject_id": subjects["CIV2"], "term_number": 1, "hours": 72}, coord)
    await c.create(components, {"subject_id": subjects["PEN1"], "term_number": 3, "kind": "elective"}, coord)
    r = await client.post(components, json={"subject_id": subjects["CIV1"], "term_number": 2}, headers=coord)
    c.expect(r.status_code == 409, f"subject twice in curriculum: {r.status_code}")

    await client.patch(f"/academic/subjects/{subjects['OLD']}", json={"is_active": False}, headers=coord)
    r = await client.post(components, json={"subject_id": subjects["OLD"], "term_number": 1}, headers=coord)
    c.expect(r.status_code == 400, f"inactive subject rejected: {r.status_code}")

    r = await client.get(f"/academic/curricula/{v1}", headers=aluno)
    detail = r.json()
    c.expect(r.status_code == 200, f"student reads curriculum: {r.status_code}")
    c.expect(detail["totals"] == {"hours": 172, "credits": 8, "mandatory_hours": 132, "terms": 3}, f"totals: {detail.get('totals')}")
    c.expect([row["hours"] for row in detail["components"]] == [60, 72, 40], f"effective hours: {detail['components']}")
    issues = " | ".join(detail["issues"])
    c.expect("CIV2 (período 1) exige CIV1" in issues, f"same-term prerequisite flagged: {issues}")
    c.expect("PEN1 está no período 3" in issues, f"term beyond duration flagged: {issues}")

    r = await client.patch(f"/academic/curriculum-components/{civ2}", json={"term_number": 2}, headers=coord)
    c.expect(r.status_code == 204, f"move component: {r.status_code}")
    r = await client.get(f"/academic/curricula/{v1}", headers=coord)
    c.expect(not any("CIV2" in issue for issue in r.json()["issues"]), f"issue cleared after move: {r.json()['issues']}")

    r = await client.post(f"/academic/programs/{program}/curricula", json={"version": "2027"}, headers=coord)
    c.expect(r.status_code == 409, f"duplicate version: {r.status_code}")
    r = await client.post(f"/academic/programs/{program}/curricula", json={"version": "x"}, headers=aluno)
    c.expect(r.status_code == 403, f"student cannot create curriculum: {r.status_code}")

    r = await client.post(f"/academic/curricula/{v1}/activate", headers=coord)
    c.expect(r.status_code == 200 and r.json()["status"] == "active", f"activate v1: {r.text}")
    r = await client.post(components, json={"subject_id": subjects["CIV3"], "term_number": 2}, headers=coord)
    c.expect(r.status_code == 409, f"active curriculum is read-only: {r.status_code}")
    r = await client.delete(f"/academic/curricula/{v1}", headers=admin)
    c.expect(r.status_code == 409, f"active curriculum cannot be deleted: {r.status_code}")
    r = await client.delete(f"/academic/subjects/{subjects['CIV1']}", headers=admin)
    c.expect(r.status_code == 409, f"subject in curriculum cannot be deleted: {r.status_code}")
    r = await client.delete(f"/academic/programs/{program}", headers=admin)
    c.expect(r.status_code == 409, f"program with curricula cannot be deleted: {r.status_code}")

    r = await client.post(f"/academic/curricula/{v1}/versions", json={"version": "2028"}, headers=coord)
    c.expect(r.status_code == 201 and r.json()["status"] == "draft", f"new version: {r.text}")
    v2 = r.json().get("id")
    r = await client.post(f"/academic/curricula/{v2}/components", json={"subject_id": subjects["CIV3"], "term_number": 2}, headers=coord)
    c.expect(r.status_code == 201, f"edit new draft: {r.status_code}")
    r = await client.get(f"/academic/curricula/{v1}", headers=coord)
    c.expect(len(r.json()["components"]) == 3, f"source untouched by new version: {len(r.json()['components'])}")
    r = await client.post(f"/academic/curricula/{v2}/activate", headers=coord)
    c.expect(r.status_code == 200, f"activate v2: {r.status_code}")
    r = await client.get(f"/academic/programs/{program}/curricula", headers=coord)
    statuses = {x["version"]: x["status"] for x in r.json()}
    c.expect(statuses == {"2027": "archived", "2028": "active"}, f"one active curriculum per program: {statuses}")


async def run() -> int:
    seed()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        coord, admin, aluno = await c.login("coord"), await c.login("admin"), await c.login("aluno")
        r = await client.post("/academic/units", json={"name": "X"}, headers=aluno)
        c.expect(r.status_code == 403, f"student cannot create unit: {r.status_code}")
        program = await check_units_and_programs(c, coord, admin)
        subjects = await check_subjects(c, coord)
        await check_curricula(c, coord, admin, aluno, program, subjects)

    if c.failures:
        print("Curriculum flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Curriculum flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
