"""Exercise the Persona integration: signed gate notices (verification, single delivery, notices to
the student and guardians) and the membership-ended feed that lets Persona revoke gate access.

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
from datetime import datetime, timezone
from pathlib import Path
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_persona_check_{os.getpid()}.sqlite3"
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
from app.models.gate_passage import GatePassage
from app.models.guardians import StudentGuardian
from app.models.institution import Institution, InstitutionMembership
from app.models.membership_event import MembershipEvent
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
# (nome, papel, instituicoes)
USERS = (
    ("admin", UserRole.institution_admin, ("alfa",)), ("coord", UserRole.coordinator, ("alfa",)), ("prof", UserRole.instructor, ("alfa",)),
    ("ana", UserRole.student, ("alfa", "beta")), ("beto", UserRole.student, ("alfa",)), ("caio", UserRole.student, ("alfa",)),
    ("mae", UserRole.guardian, ("alfa",)), ("coordb", UserRole.coordinator, ("beta",)),
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
            institutions[slug] = str(institution.id)
        for name, role, slugs in USERS:
            user = Student(name=name.title(), email=f"{name}@example.com", password_hash=hash_password(PASSWORD), role=role)
            db.add(user)
            db.flush()
            for slug in slugs:
                db.add(InstitutionMembership(institution_id=institutions[slug], user_id=user.id, role=role))
            ids[name] = str(user.id)
        db.commit()
    with SessionLocal() as db:
        bind_institution(db, institutions["alfa"])
        db.add(StudentGuardian(student_id=ids["ana"], guardian_id=ids["mae"]))
        db.commit()
    return institutions, ids


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def notice(student_id: str, institution_id: str, *, typ: str = "gate_event", key: Ed25519PrivateKey = PERSONA_KEY,
           direction: str = "ENTRY", jti: str | None = None, iat_offset: int = 0) -> str:
    """Mesmo formato do Persona (core/gate/notice.py): JWS EdDSA com gate, direction e at."""
    now = int(time.time()) + iat_offset
    header = _b64(json.dumps({"alg": "EdDSA", "typ": "JWT"}).encode())
    payload = _b64(json.dumps({
        "iss": "persona", "aud": "wedu", "typ": typ, "jti": jti or uuid.uuid4().hex, "iat": now, "exp": now + 60,
        "sub": student_id, "inst": institution_id, "gate": "Portão principal", "direction": direction,
        "at": datetime(2026, 10, 5, 10, 30, tzinfo=timezone.utc).isoformat(),
    }).encode())
    return f"{header}.{payload}.{_b64(key.sign(f'{header}.{payload}'.encode()))}"


class Checker:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client
        self.failures: list[str] = []

    def expect(self, condition: bool, message: str) -> None:
        if not condition:
            self.failures.append(message)

    async def login(self, email: str, institution: str | None = None) -> dict:
        body = {"email": email, "password": PASSWORD, **({"institution": institution} if institution else {})}
        response = await self.client.post("/auth/login", json=body)
        assert response.status_code == 200, f"login {email}: {response.status_code} {response.text}"
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    async def call(self, method: str, path: str, expected: int, message: str, headers: dict | None = None, **kwargs):
        response = await self.client.request(method, path, headers=headers or {}, **kwargs)
        self.expect(response.status_code == expected, f"{message}: {response.status_code} {response.text[:200]}")
        return response.json() if response.content else {}


async def check_gate_notices(c: Checker, h: dict, ids: dict, institutions: dict) -> None:
    alfa = institutions["alfa"]
    url = "/integrations/persona/gate-events"
    first = notice(ids["ana"], alfa, jti="passagem-1")
    result = await c.call("POST", url, 200, "gate notice", json={"notice": first})
    c.expect(result == {"status": "recorded"}, f"recorded: {result}")
    again = await c.call("POST", url, 200, "same notice again (Persona retry)", json={"notice": first})
    c.expect(again == {"status": "duplicate"}, f"duplicate: {again}")

    for label, token in {
        "signed by another key": notice(ids["ana"], alfa, key=OTHER_KEY),
        "login message is not a gate notice": notice(ids["ana"], alfa, typ="facial_login"),
        "expired": notice(ids["ana"], alfa, iat_offset=-120),
        "unknown direction": notice(ids["ana"], alfa, direction="SIDEWAYS"),
        "tampered": notice(ids["ana"], alfa)[:-4] + "AAAA",
    }.items():
        await c.call("POST", url, 401, label, json={"notice": token})
    await c.call("POST", "/auth/facial-login", 401, "gate notice is not a login", json={"assertion": notice(ids["ana"], alfa)})

    outsider = await c.call("POST", url, 200, "not a member", json={"notice": notice(ids["coordb"], alfa)})
    c.expect(outsider == {"status": "ignored"}, f"ignored: {outsider}")

    exit_notice = await c.call("POST", url, 200, "exit", json={"notice": notice(ids["beto"], alfa, direction="EXIT")})
    c.expect(exit_notice == {"status": "recorded"}, f"exit: {exit_notice}")

    ana_inbox = await c.call("GET", "/notifications/me", 200, "student inbox", h["ana"])
    mae_inbox = await c.call("GET", "/notifications/me", 200, "guardian inbox", h["mae"])
    c.expect([n["title"] for n in ana_inbox] == ["Ana: entrada na catraca"], f"student notified once: {ana_inbox}")
    c.expect([n["body"] for n in mae_inbox] == ["Ana passou pela catraca Portão principal (entrada) às 07:30 de 05/10/2026."],
             f"guardian notified in local time: {mae_inbox}")
    beto_inbox = await c.call("GET", "/notifications/me", 200, "exit inbox", h["beto"])
    c.expect([n["title"] for n in beto_inbox] == ["Beto: saída na catraca"], f"exit notice: {beto_inbox}")
    with SessionLocal() as db:
        passages = db.query(GatePassage).order_by(GatePassage.occurred_at).all()
        c.expect(sorted((str(p.student_id), p.direction, str(p.institution_id)) for p in passages)
                 == sorted([(ids["ana"], "entry", alfa), (ids["beto"], "exit", alfa)]), f"passages: {passages}")


async def check_membership_feed(c: Checker, h: dict, ids: dict, institutions: dict) -> None:
    alfa, beta = institutions["alfa"], institutions["beta"]
    feed = "/integrations/persona/membership-events"
    await c.call("GET", feed, 403, "teacher cannot read the feed", h["prof"])
    empty = await c.call("GET", feed, 200, "empty feed", h["coord"])
    c.expect(empty == [], f"nothing ended yet: {empty}")

    # Desligado da Alfa (continua na Beta): so a Alfa ve o fim.
    await c.call("DELETE", f"/admin/users/{ids['ana']}", 204, "admin removes Ana from Alfa", h["admin"])
    # Conta desativada: encerra o vinculo (Alfa).
    await c.call("PATCH", f"/admin/users/{ids['beto']}", 200, "admin deactivates Beto", h["admin"], json={"is_active": False})
    # Mudanca desfeita (rollback) nao gera evento.
    with SessionLocal() as db:
        membership = db.query(InstitutionMembership).filter_by(user_id=ids["caio"]).one()
        membership.is_active = False
        db.flush()
        db.rollback()

    events = await c.call("GET", feed, 200, "alfa feed", h["coord"])
    c.expect(sorted(e["user_id"] for e in events) == sorted([ids["ana"], ids["beto"]]) and all(e["kind"] == "ended" for e in events),
             f"alfa ended: {events}")
    later = await c.call("GET", feed, 200, "since the last one", h["coord"], params={"since": events[-1]["occurred_at"]})
    c.expect(events[-1]["id"] in [e["id"] for e in later] and len(later) <= len(events), f"since is inclusive: {later}")
    beta_feed = await c.call("GET", feed, 200, "beta feed", h["coordb"])
    c.expect(beta_feed == [], f"beta did not lose anyone: {beta_feed}")

    gone = await c.call("POST", "/integrations/persona/gate-events", 200, "notice after membership ended",
                        json={"notice": notice(ids["ana"], alfa)})
    c.expect(gone == {"status": "ignored"}, f"ended member ignored: {gone}")
    with SessionLocal() as db:
        total = db.query(MembershipEvent).count()
    c.expect(total == 2, f"one event per ended membership: {total}")
    del beta


async def run() -> int:
    institutions, ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with ApiClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        h = {name: await c.login(f"{name}@example.com", institutions[slugs[0]]) for name, _, slugs in USERS}
        await check_gate_notices(c, h, ids, institutions)
        await check_membership_feed(c, h, ids, institutions)

    if c.failures:
        print("Persona integration flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Persona integration flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
