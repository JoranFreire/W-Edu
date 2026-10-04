"""Exercise the facial identity integration (Persona): age from birth date, the teacher roster
and the facial login assertion (signature, lifetime, audience, single use, membership).

Uses a temporary SQLite database by default (set DATABASE_URL to use PostgreSQL).
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import tempfile
import time
import uuid
from datetime import date, timedelta
from pathlib import Path
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_facial_check_{os.getpid()}.sqlite3"
    os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["NOTIFICATION_WORKER_ENABLED"] = "false"

PERSONA_KEY = Ed25519PrivateKey.generate()
OTHER_KEY = Ed25519PrivateKey.generate()
os.environ["PERSONA_ASSERTION_PUBLIC_KEY"] = base64.urlsafe_b64encode(
    PERSONA_KEY.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
).decode().rstrip("=")

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
from app.models.guardians import StudentGuardian
from app.models.institution import Institution, InstitutionMembership
from app.models.schedule import ClassEnrollment
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
    ("admin", UserRole.institution_admin), ("coord", UserRole.coordinator), ("prof", UserRole.instructor),
    ("outro", UserRole.instructor), ("a1", UserRole.student), ("a2", UserRole.student), ("inativo", UserRole.student),
    ("mae", UserRole.guardian),
)


def seed() -> tuple[str, str, dict[str, str]]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ids = {}
    with SessionLocal() as db:
        institution = Institution(slug="escola", name="Escola")
        other = Institution(slug="outra", name="Outra")
        db.add_all([institution, other])
        db.flush()
        for name, role in USERS:
            user = Student(name=name.title(), email=f"{name}@example.com", password_hash=hash_password(PASSWORD), role=role)
            db.add(user)
            db.flush()
            db.add(InstitutionMembership(institution_id=institution.id, user_id=user.id, role=role))
            ids[name] = str(user.id)
        db.commit()
        return str(institution.id), str(other.id), ids


def enroll(institution_id: str, offering_id: str, ids: dict) -> None:
    with SessionLocal() as db:
        bind_institution(db, institution_id)
        for name in ("a1", "a2"):
            db.add(ClassEnrollment(class_offering_id=offering_id, student_id=ids[name]))
        db.commit()


def link_guardian(institution_id: str, ids: dict) -> None:
    """A mae e responsavel pelos dois alunos: a1 adulto e a2 menor."""
    with SessionLocal() as db:
        bind_institution(db, institution_id)
        for name in ("a1", "a2"):
            db.add(StudentGuardian(student_id=ids[name], guardian_id=ids["mae"]))
        db.commit()


def deactivate(user_id: str) -> None:
    with SessionLocal() as db:
        db.get(Student, uuid.UUID(user_id)).is_active = False
        db.commit()


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def assertion(user_id: str, institution_id: str, *, key: Ed25519PrivateKey = PERSONA_KEY, aud: str = "wedu",
              iat_offset: int = 0, lifetime: int = 60, jti: str | None = None, typ: str | None = "facial_login") -> str:
    """Mesmo formato que o Persona emite: JWS compacto EdDSA."""
    now = int(time.time()) + iat_offset
    header = _b64(json.dumps({"alg": "EdDSA", "typ": "JWT"}).encode())
    payload = _b64(json.dumps({
        "iss": "persona", "aud": aud, "sub": user_id, "inst": institution_id,
        "jti": jti or uuid.uuid4().hex, "iat": now, "exp": now + lifetime,
        **({"typ": typ} if typ else {}),
    }).encode())
    signature = _b64(key.sign(f"{header}.{payload}".encode()))
    return f"{header}.{payload}.{signature}"


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
        return response.json() if response.content else {}


async def check_age(c: Checker, h: dict, ids: dict) -> None:
    admin = h["admin"]
    adult_birth = str(date.today().replace(year=date.today().year - 30))
    turns_18_tomorrow = date.today() + timedelta(days=1)
    minor_birth = str(turns_18_tomorrow.replace(year=turns_18_tomorrow.year - 18))

    await c.call("PATCH", f"/admin/users/{ids['a1']}", 200, "admin sets adult birth date", admin, json={"birth_date": adult_birth})
    await c.call("PATCH", f"/admin/users/{ids['a2']}", 200, "admin sets minor birth date", admin, json={"birth_date": minor_birth})
    await c.call("PATCH", f"/admin/users/{ids['a2']}", 422, "birth date in the future",
                 admin, json={"birth_date": str(date.today() + timedelta(days=1))})

    me = await c.call("GET", "/users/me", 200, "a1 me", h["a1"])
    c.expect(me.get("is_adult") is True and me.get("birth_date") == adult_birth, f"adult: {me}")
    me = await c.call("GET", "/users/me", 200, "a2 me", h["a2"])
    c.expect(me.get("is_adult") is False, f"turns 18 tomorrow is still a minor: {me}")
    await c.call("PATCH", f"/admin/users/{ids['prof']}", 200, "admin sets a wrong birth date", admin, json={"birth_date": adult_birth})
    await c.call("PATCH", f"/admin/users/{ids['prof']}", 200, "admin clears the birth date", admin, json={"birth_date": None})
    me = await c.call("GET", "/users/me", 200, "prof me", h["prof"])
    c.expect(me.get("is_adult") is False and me.get("birth_date") is None, f"cleared birth date is not adult: {me}")

    # A propria pessoa nao declara a idade (so a secretaria/admin): o PATCH dela ignora o campo.
    await c.call("PATCH", f"/users/{ids['a2']}", 200, "minor edits own profile", h["a2"], json={"birth_date": adult_birth})
    me = await c.call("GET", "/users/me", 200, "a2 me again", h["a2"])
    c.expect(me.get("is_adult") is False, f"self-declared age ignored: {me}")


async def check_dependents_age(c: Checker, h: dict, ids: dict, institution_id: str) -> None:
    link_guardian(institution_id, ids)
    dependents = await c.call("GET", "/guardians/me/dependents", 200, "guardian dependents", h["mae"])
    adult = {d["student"]["id"]: d.get("student_is_adult") for d in dependents}
    c.expect(adult == {ids["a1"]: True, ids["a2"]: False}, f"dependents carry adulthood: {dependents}")


async def check_roster(c: Checker, h: dict, ids: dict, institution_id: str) -> None:
    course = await c.call("POST", "/courses", 201, "course", h["admin"], json={"name": "Curso"})
    offering = await c.call("POST", "/schedule/classes", 201, "offering", h["admin"], json={
        "course_id": course["id"], "name": "Turma A", "capacity": 10, "status": "open", "instructor_id": ids["prof"],
        "starts_at": "2027-03-01T08:00:00Z", "ends_at": "2027-06-30T12:00:00Z"})
    enroll(institution_id, offering["id"], ids)
    path = f"/assessment/offerings/{offering['id']}/roster"

    roster = await c.call("GET", path, 200, "teacher roster", h["prof"])
    c.expect(sorted(p["id"] for p in roster) == sorted([ids["a1"], ids["a2"]]), f"roster: {roster}")
    c.expect(all(set(p) == {"id", "name", "email"} for p in roster), f"roster only has a summary: {roster}")
    await c.call("GET", path, 200, "coordination roster", h["coord"])
    await c.call("GET", path, 403, "another instructor", h["outro"])
    await c.call("GET", path, 403, "student", h["a1"])


async def check_facial_login(c: Checker, ids: dict, institution_id: str, other_id: str) -> None:
    token = assertion(ids["a1"], institution_id)
    body = await c.call("POST", "/auth/facial-login", 200, "valid assertion", json={"assertion": token})
    c.expect(body.get("institution", {}).get("id") == institution_id, f"token institution: {body}")
    me = await c.call("GET", "/users/me", 200, "token from facial login works",
                      {"Authorization": f"Bearer {body.get('access_token')}"})
    c.expect(me.get("id") == ids["a1"], f"logged as a1: {me}")

    await c.call("POST", "/auth/facial-login", 401, "replay", json={"assertion": token})
    refusals = {
        "signed by another key": assertion(ids["a1"], institution_id, key=OTHER_KEY),
        "wrong audience": assertion(ids["a1"], institution_id, aud="outro-sistema"),
        # Aviso de catraca do Persona (mesma chave, mesmos sub/inst): nao vale como login.
        "gate notice is not a login": assertion(ids["a1"], institution_id, typ="gate_event"),
        "no message type": assertion(ids["a1"], institution_id, typ=None),
        "expired": assertion(ids["a1"], institution_id, iat_offset=-120),
        "lifetime above 60 s": assertion(ids["a1"], institution_id, lifetime=3600),
        "unknown user": assertion(str(uuid.uuid4()), institution_id),
        "tampered": assertion(ids["a1"], institution_id)[:-4] + "AAAA",
        "garbage": "nao-e-um-jws",
    }
    for message, bad in refusals.items():
        await c.call("POST", "/auth/facial-login", 401, message, json={"assertion": bad})

    await c.call("POST", "/auth/facial-login", 403, "institution without membership",
                 json={"assertion": assertion(ids["a1"], other_id)})
    deactivate(ids["inativo"])
    await c.call("POST", "/auth/facial-login", 403, "inactive account",
                 json={"assertion": assertion(ids["inativo"], institution_id)})


async def run() -> int:
    institution_id, other_id, ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with ApiClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        h = {name: await c.login(f"{name}@example.com") for name, _ in USERS}
        await check_age(c, h, ids)
        await check_dependents_age(c, h, ids, institution_id)
        await check_roster(c, h, ids, institution_id)
        await check_facial_login(c, ids, institution_id, other_id)

    if c.failures:
        print("Facial identity flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Facial identity flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
