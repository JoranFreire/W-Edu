"""Exercise benefits released with QR: release (meeting or student), stock reservation, lookup and redemption.

Uses a temporary SQLite database by default (set DATABASE_URL to use PostgreSQL).
"""

from __future__ import annotations

import asyncio
from datetime import date, timedelta
import os
import tempfile
from pathlib import Path
import sys

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_vouchers_check_{os.getpid()}.sqlite3"
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

from scripts.check_support import MISSING_ID, ApiClient  # noqa: E402
import app.models  # noqa: F401
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.core.tenancy import bind_institution
from app.models.guardians import StudentGuardian
from app.models.institution import Institution, InstitutionMembership
from app.models.schedule import ClassEnrollment
from app.models.social_programs import BenefitVoucher
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
    ("admin", UserRole.institution_admin), ("prof", UserRole.instructor), ("outro", UserRole.instructor),
    ("cantina", UserRole.student), ("mae", UserRole.guardian), ("a1", UserRole.student), ("a2", UserRole.student), ("a3", UserRole.student),
)


def seed() -> tuple[str, dict[str, str]]:
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
        institution_id = str(institution.id)
        db.commit()
    return institution_id, ids


def enroll_and_link(institution_id: str, offering_id: str, ids: dict) -> None:
    """Tres alunos inscritos na turma; a mae e responsavel pela a1."""
    with SessionLocal() as db:
        bind_institution(db, institution_id)
        for name in ("a1", "a2", "a3"):
            db.add(ClassEnrollment(class_offering_id=offering_id, student_id=ids[name]))
        db.add(StudentGuardian(student_id=ids["a1"], guardian_id=ids["mae"]))
        db.commit()


def expire(code: str) -> None:
    with SessionLocal() as db:
        voucher = db.query(BenefitVoucher).filter(BenefitVoucher.code == code).one()
        voucher.valid_until = date.today() - timedelta(days=1)
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


async def setup(c: Checker, h: dict, ids: dict, institution_id: str) -> dict:
    admin = h["admin"]
    course = await c.call("POST", "/courses", 201, "course", admin, json={"name": "Curso"})
    offering = await c.call("POST", "/schedule/classes", 201, "offering", admin, json={
        "course_id": course["id"], "name": "Turma A", "capacity": 10, "status": "open", "instructor_id": ids["prof"],
        "starts_at": "2027-03-01T08:00:00Z", "ends_at": "2027-06-30T12:00:00Z"})
    enroll_and_link(institution_id, offering["id"], ids)
    meeting = await c.call("POST", "/schedule/meetings", 201, "meeting", admin, json={
        "class_offering_id": offering["id"], "title": "Aula 1", "starts_at": "2027-03-01T08:00:00Z", "ends_at": "2027-03-01T10:00:00Z"})
    for name in ("a1", "a2"):
        await c.call("POST", f"/schedule/meetings/{meeting['id']}/attendance", 201, f"{name} present", admin, json={"student_id": ids[name]})
    snack = await c.call("POST", "/social/benefit-items", 201, "snack", admin,
                         json={"name": "Lanche", "kind": "snack", "unit_cost_cents": 500, "requires_attendance": True})
    kit = await c.call("POST", "/social/benefit-items", 201, "kit", admin, json={"name": "Kit", "kind": "material", "unit": "kit"})
    await c.call("POST", f"/social/benefit-items/{snack['id']}/stock", 201, "snack stock", admin, json={"quantity": 3, "received_on": "2027-02-20"})
    await c.call("POST", f"/social/benefit-items/{kit['id']}/stock", 201, "kit stock", admin, json={"quantity": 1, "received_on": "2027-02-20"})
    profile = await c.call("POST", "/access/roles", 201, "canteen profile", admin, json={"name": "Cantina", "permissions": ["benefits.redeem"]})
    await c.call("POST", f"/access/roles/{profile['id']}/members", 200, "canteen member", admin, json={"user_id": ids["cantina"]})
    return {"offering": offering["id"], "meeting": meeting["id"], "snack": snack["id"], "kit": kit["id"]}


async def check_release(c: Checker, h: dict, ids: dict, ctx: dict) -> dict:
    prof = h["prof"]
    await c.call("POST", f"/social/meetings/{ctx['meeting']}/vouchers", 403, "other instructor", h["outro"], json={"item_id": ctx["snack"]})
    await c.call("POST", f"/social/meetings/{ctx['meeting']}/vouchers", 403, "canteen cannot release", h["cantina"], json={"item_id": ctx["snack"]})
    await c.call("POST", f"/social/meetings/{ctx['meeting']}/vouchers", 400, "validity in the past", prof,
                 json={"item_id": ctx["snack"], "valid_until": str(date.today() - timedelta(days=1))})
    released = await c.call("POST", f"/social/meetings/{ctx['meeting']}/vouchers", 200, "snack for those present", prof, json={"item_id": ctx["snack"]})
    c.expect(released == {"released": 2, "available_stock": 1}, f"released: {released}")
    again = await c.call("POST", f"/social/meetings/{ctx['meeting']}/vouchers", 200, "no double release", prof, json={"item_id": ctx["snack"]})
    c.expect(again["released"] == 0, f"idempotent: {again}")
    items = {i["name"]: (i["stock"], i["reserved"]) for i in await c.call("GET", "/social/benefit-items", 200, "items", prof)}
    c.expect(items["Lanche"] == (3, 2), f"physical stock and reservation: {items}")
    # Reserva vale tambem para a entrega direta: so 1 lanche livre.
    await c.call("POST", "/social/deliveries", 409, "direct delivery respects reservation", prof,
                 json={"item_id": ctx["snack"], "student_id": ids["a3"], "class_offering_id": ctx["offering"], "quantity": 2})
    kit = await c.call("POST", "/social/vouchers", 201, "kit to a1", prof,
                       json={"item_id": ctx["kit"], "student_id": ids["a1"], "class_offering_id": ctx["offering"], "valid_until": str(date.today())})
    await c.call("POST", "/social/vouchers", 409, "kit reserved", prof, json={"item_id": ctx["kit"], "student_id": ids["a2"], "class_offering_id": ctx["offering"]})
    await c.call("POST", "/social/vouchers", 404, "student not enrolled", prof, json={"item_id": ctx["snack"], "student_id": ids["cantina"], "class_offering_id": ctx["offering"]})

    mine = await c.call("GET", "/social/my/vouchers", 200, "a1 vouchers", h["a1"])
    c.expect(sorted(v["item_name"] for v in mine) == ["Kit", "Lanche"] and all(v["status"] == "released" for v in mine), f"a1 vouchers: {mine}")
    c.expect(all(v["qr_payload"] == f"wedu-beneficio:{v['code']}" for v in mine), f"qr payload: {mine}")
    child = await c.call("GET", f"/guardians/me/dependents/{ids['a1']}/vouchers", 200, "guardian sees dependent QR", h["mae"])
    c.expect(len(child) == 2, f"guardian vouchers: {child}")
    await c.call("GET", f"/guardians/me/dependents/{ids['a2']}/vouchers", 404, "not a dependent", h["mae"])
    a3 = await c.call("GET", "/social/my/vouchers", 200, "absent student", h["a3"])
    c.expect(a3 == [], f"absent student gets no snack: {a3}")
    snack_a1 = next(v for v in mine if v["item_name"] == "Lanche")
    snack_a2 = (await c.call("GET", "/social/my/vouchers", 200, "a2 vouchers", h["a2"]))[0]
    return {"snack_a1": snack_a1, "snack_a2": snack_a2, "kit": kit}


async def check_redeem(c: Checker, h: dict, ids: dict, ctx: dict, vouchers: dict) -> None:
    canteen, prof = h["cantina"], h["prof"]
    snack = vouchers["snack_a1"]
    await c.call("POST", "/social/vouchers/redeem", 403, "student cannot redeem", h["a2"], json={"code": snack["code"]})
    await c.call("POST", "/social/vouchers/lookup", 404, "unknown code", canteen, json={"code": "nao-existe"})
    looked = await c.call("POST", "/social/vouchers/lookup", 200, "lookup by scanned QR", canteen, json={"code": snack["qr_payload"]})
    c.expect(looked.get("student", {}).get("name") == "A1" and looked.get("status") == "released", f"lookup: {looked}")
    redeemed = await c.call("POST", "/social/vouchers/redeem", 200, "redeem", canteen, json={"code": snack["qr_payload"]})
    c.expect(redeemed.get("status") == "redeemed" and redeemed.get("redeemed_at"), f"redeemed: {redeemed}")
    twice = await c.call("POST", "/social/vouchers/redeem", 409, "redeem twice", canteen, json={"code": snack["code"]})
    c.expect("já foi retirado" in twice.get("detail", ""), f"twice: {twice}")
    deliveries = await c.call("GET", f"/social/offerings/{ctx['offering']}/deliveries", 200, "redemption becomes delivery", prof)
    c.expect([(d["item_name"], d["student"]["name"], d["unit_cost_cents"]) for d in deliveries] == [("Lanche", "A1", 500)], f"deliveries: {deliveries}")
    items = {i["name"]: (i["stock"], i["reserved"]) for i in await c.call("GET", "/social/benefit-items", 200, "items after redeem", prof)}
    c.expect(items["Lanche"] == (2, 1), f"stock after redeem: {items}")

    cancelled = await c.call("POST", f"/social/vouchers/{vouchers['snack_a2']['id']}/cancel", 200, "cancel", prof)
    c.expect(cancelled.get("status") == "cancelled", f"cancelled: {cancelled}")
    await c.call("POST", f"/social/vouchers/{vouchers['snack_a2']['id']}/cancel", 409, "cancel twice", prof)
    await c.call("POST", f"/social/vouchers/{snack['id']}/cancel", 409, "cannot cancel redeemed", prof)
    await c.call("POST", f"/social/vouchers/{MISSING_ID}/cancel", 404, "unknown voucher", prof)
    refused = await c.call("POST", "/social/vouchers/redeem", 409, "cancelled QR", canteen, json={"code": vouchers["snack_a2"]["code"]})
    c.expect("cancelado" in refused.get("detail", ""), f"cancelled refusal: {refused}")

    expire(vouchers["kit"]["code"])
    expired = await c.call("POST", "/social/vouchers/redeem", 409, "expired QR", canteen, json={"code": vouchers["kit"]["code"]})
    c.expect("venceu" in expired.get("detail", ""), f"expired: {expired}")
    listed = {v["item_name"]: v["status"] for v in await c.call("GET", f"/social/offerings/{ctx['offering']}/vouchers", 200, "offering vouchers", prof)
              if v["student"]["name"] == "A1"}
    c.expect(listed == {"Lanche": "redeemed", "Kit": "expired"}, f"statuses: {listed}")
    # Vencido nao reserva mais: o kit volta a ficar disponivel.
    await c.call("POST", "/social/vouchers", 201, "kit released again after expiry", prof,
                 json={"item_id": ctx["kit"], "student_id": ids["a2"], "class_offering_id": ctx["offering"]})
    versions = (await c.call("GET", "/sync/versions", 200, "versions", h["a1"]))["versions"]
    c.expect(versions.get("benefits", 0) > 0, f"benefits area version: {versions}")


async def run() -> int:
    institution_id, ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with ApiClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        h = {name: await c.login(f"{name}@example.com") for name, _ in USERS}
        ctx = await setup(c, h, ids, institution_id)
        vouchers = await check_release(c, h, ids, ctx)
        await check_redeem(c, h, ids, ctx, vouchers)

    if c.failures:
        print("Benefit vouchers flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Benefit vouchers flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
