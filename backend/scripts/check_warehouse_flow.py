"""Exercise the warehouse: items and entries, teacher requests with mandatory approval (partial or rejected), withdrawal
with stock check, durable returns with losses, overdue loans, low stock, consumption, funder costs and RBAC operators.

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
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_warehouse_check_{os.getpid()}.sqlite3"
    os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["NOTIFICATION_WORKER_ENABLED"] = "false"
os.environ["MINIMUM_WAGE_API_URL"] = ""
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
from app.models.notification import NotificationEvent, NotificationEventType
from app.models.warehouse import MaterialRequest
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
USERS = (("admin", UserRole.institution_admin), ("coord", UserRole.coordinator), ("prof", UserRole.instructor), ("outro", UserRole.instructor),
         ("almox", UserRole.secretary), ("ana", UserRole.student))


def seed() -> dict[str, int]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ids = {}
    with SessionLocal() as db:
        institution = Institution(slug="escola", name="Escola", type=InstitutionType.school)
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


async def setup(c: Checker, h: dict, ids: dict) -> dict:
    """Almoxarife por perfil de acesso, materiais com entrada financiada e turma do professor."""
    admin, almox = h["admin"], h["almox"]
    await c.call("POST", "/warehouse/items", 403, "secretary is not a warehouse operator by default", almox, json={"name": "X"})
    role = await c.call("POST", "/access/roles", 201, "warehouse profile", admin, json={"name": "Almoxarife", "permissions": ["warehouse.manage"]})
    await c.call("POST", f"/access/roles/{role['id']}/members", 200, "assign profile", admin, json={"user_id": ids["almox"]})
    funding = await c.call("POST", "/social/funding-sources", 201, "funding", h["coord"], json={"name": "Prefeitura", "amount_cents": 100000, "starts_on": "2027-01-01"})
    paper = await c.call("POST", "/warehouse/items", 201, "paper", almox, json={
        "name": "Papel A4", "category": "Papelaria", "kind": "consumable", "unit": "resma", "min_stock": 5, "unit_cost_cents": 2500})
    ball = await c.call("POST", "/warehouse/items", 201, "ball", almox, json={
        "name": "Bola de vôlei", "category": "Esportes", "kind": "durable", "min_stock": 1, "unit_cost_cents": 8000, "location": "Armário 2"})
    await c.call("POST", f"/warehouse/items/{paper['id']}/entries", 201, "paper entry", almox, json={"quantity": 10, "received_on": "2027-02-01", "funding_source_id": funding["id"]})
    stocked = await c.call("POST", f"/warehouse/items/{ball['id']}/entries", 201, "ball donation", almox, json={"quantity": 3, "origin": "donation", "received_on": "2027-02-01"})
    c.expect(stocked["available"] == 3 and stocked["on_loan"] == 0, f"ball stock: {stocked}")
    catalog = await c.call("GET", "/warehouse/items", 200, "teacher sees catalog", h["prof"])
    c.expect({i["name"]: i["available"] for i in catalog} == {"Papel A4": 10, "Bola de vôlei": 3}, f"catalog: {catalog}")
    await c.call("GET", "/warehouse/items", 403, "student has no warehouse access", h["ana"])
    course = await c.call("POST", "/courses", 201, "course", h["coord"], json={"name": "Artes"})
    offering = await c.call("POST", "/schedule/classes", 201, "offering", h["coord"], json={
        "course_id": course["id"], "name": "Artes 6A", "capacity": 30, "status": "open", "instructor_id": ids["prof"],
        "starts_at": "2027-02-01T08:00:00Z", "ends_at": "2027-12-01T12:00:00Z", "funding_source_id": funding["id"]})
    return {"paper": paper["id"], "ball": ball["id"], "offering": offering["id"], "funding": funding["id"]}


def line_of(request: dict, item_id: int) -> dict:
    return next(line for line in request["lines"] if line["item_id"] == item_id)


async def check_request_cycle(c: Checker, h: dict, ids: dict, ctx: dict) -> None:
    prof, almox = h["prof"], h["almox"]
    payload = {"purpose": "Gincana de recreio", "needed_on": "2027-03-10", "class_offering_id": ctx["offering"],
               "lines": [{"item_id": ctx["paper"], "quantity": 4}, {"item_id": ctx["ball"], "quantity": 2}]}
    await c.call("POST", "/warehouse/requests", 403, "student cannot request", h["ana"], json=payload)
    await c.call("POST", "/warehouse/requests", 403, "other teacher's class", h["outro"], json=payload)
    await c.call("POST", "/warehouse/requests", 400, "repeated item", prof, json={**payload, "lines": [{"item_id": ctx["paper"], "quantity": 1}] * 2})
    request = await c.call("POST", "/warehouse/requests", 201, "teacher requests", prof, json=payload)
    c.expect(request["status"] == "pending" and request["class_offering_name"] == "Artes 6A", f"request: {request}")
    await c.call("POST", f"/warehouse/requests/{request['id']}/deliver", 409, "no withdrawal before approval", almox)
    await c.call("POST", f"/warehouse/requests/{request['id']}/approve", 403, "teacher cannot approve", prof, json={"lines": []})
    lines = {line["item_id"]: line["id"] for line in request["lines"]}
    await c.call("POST", f"/warehouse/requests/{request['id']}/approve", 400, "above requested", almox,
                 json={"lines": [{"line_id": lines[ctx["paper"]], "quantity": 9}, {"line_id": lines[ctx["ball"]], "quantity": 2}]})
    approved = await c.call("POST", f"/warehouse/requests/{request['id']}/approve", 200, "partial approval", almox, json={
        "lines": [{"line_id": lines[ctx["paper"]], "quantity": 3}, {"line_id": lines[ctx["ball"]], "quantity": 2}],
        "return_due_on": "2027-03-11", "note": "Uma resma a menos"})
    c.expect(approved["status"] == "approved" and line_of(approved, ctx["paper"])["quantity_approved"] == 3 and approved["return_due_on"] == "2027-03-11", f"approved: {approved}")
    await c.call("POST", f"/warehouse/requests/{request['id']}/approve", 409, "approve twice", almox, json={"lines": []})
    with SessionLocal() as db:
        notices = db.query(NotificationEvent).filter(NotificationEvent.event_type == NotificationEventType.material_request_decided).count()
    c.expect(notices == 1, f"teacher notified: {notices}")
    delivered = await c.call("POST", f"/warehouse/requests/{request['id']}/deliver", 200, "withdrawal", almox)
    c.expect(delivered["status"] == "delivered" and line_of(delivered, ctx["ball"])["outstanding"] == 2, f"delivered: {delivered}")
    items = {i["name"]: i for i in await c.call("GET", "/warehouse/items", 200, "balances", almox)}
    c.expect((items["Papel A4"]["available"], items["Bola de vôlei"]["available"], items["Bola de vôlei"]["on_loan"]) == (7, 1, 2), f"balances: {items}")

    ball_line = line_of(delivered, ctx["ball"])["id"]
    paper_line = line_of(delivered, ctx["paper"])["id"]
    await c.call("POST", f"/warehouse/requests/{request['id']}/returns", 400, "consumables do not return", almox, json={"lines": [{"line_id": paper_line, "returned": 1}]})
    await c.call("POST", f"/warehouse/requests/{request['id']}/returns", 400, "more than on loan", almox, json={"lines": [{"line_id": ball_line, "returned": 3}]})
    partial = await c.call("POST", f"/warehouse/requests/{request['id']}/returns", 200, "one ball back", almox, json={"lines": [{"line_id": ball_line, "returned": 1}]})
    c.expect(partial["status"] == "delivered", f"still out: {partial}")
    closed = await c.call("POST", f"/warehouse/requests/{request['id']}/returns", 200, "one ball lost", almox, json={"lines": [{"line_id": ball_line, "lost": 1}]})
    c.expect(closed["status"] == "closed", f"closed: {closed}")
    await c.call("POST", f"/warehouse/my/requests/{request['id']}/cancel", 409, "cannot cancel after withdrawal", prof)


async def check_stock_and_reports(c: Checker, h: dict, ctx: dict) -> None:
    prof, almox = h["prof"], h["almox"]
    big = await c.call("POST", "/warehouse/requests", 201, "big request", prof, json={"purpose": "Mural", "needed_on": "2027-03-12", "lines": [{"item_id": ctx["paper"], "quantity": 8}]})
    await c.call("POST", f"/warehouse/requests/{big['id']}/approve", 200, "approve 8", almox, json={"lines": [{"line_id": big["lines"][0]["id"], "quantity": 8}]})
    short = await c.call("POST", f"/warehouse/requests/{big['id']}/deliver", 409, "not enough paper", almox)
    c.expect("7 disponível(is)" in short.get("detail", ""), f"stock message: {short}")
    await c.call("POST", f"/warehouse/my/requests/{big['id']}/cancel", 200, "teacher cancels approved request", prof)

    rejected = await c.call("POST", "/warehouse/requests", 201, "request to reject", prof, json={"purpose": "X", "needed_on": "2027-03-13", "lines": [{"item_id": ctx["ball"], "quantity": 1}]})
    await c.call("POST", f"/warehouse/requests/{rejected['id']}/reject", 422, "reject needs a note", almox, json={})
    no = await c.call("POST", f"/warehouse/requests/{rejected['id']}/reject", 200, "reject", almox, json={"note": "Sem bolas disponíveis"})
    c.expect(no["status"] == "rejected", f"rejected: {no}")

    loan = await c.call("POST", "/warehouse/requests", 201, "loan", prof, json={"purpose": "Educação física", "needed_on": "2026-09-01", "class_offering_id": ctx["offering"],
                                                                            "lines": [{"item_id": ctx["ball"], "quantity": 1}, {"item_id": ctx["paper"], "quantity": 3}]})
    await c.call("POST", f"/warehouse/requests/{loan['id']}/approve", 200, "approve loan", almox,
                 json={"lines": [{"line_id": line["id"], "quantity": line["quantity_requested"]} for line in loan["lines"]], "return_due_on": "2026-09-02"})
    await c.call("POST", f"/warehouse/requests/{loan['id']}/deliver", 200, "deliver loan", almox)
    overdue = await c.call("GET", "/warehouse/reports/overdue", 200, "overdue loans", h["coord"])
    c.expect([r["id"] for r in overdue] == [loan["id"]] and overdue[0]["overdue"], f"overdue: {overdue}")
    low = await c.call("GET", "/warehouse/reports/low-stock", 200, "low stock", h["coord"])
    # Papel: 10 - 3 - 3 = 4 (< 5). Bola: 3 - 2 + 1 (devolvida) - 1 (emprestimo) = 1, igual ao minimo: nao e baixo.
    c.expect([(i["name"], i["available"]) for i in low] == [("Papel A4", 4)], f"low stock: {low}")
    await c.call("GET", "/warehouse/reports/low-stock", 403, "teacher has no reports", prof)
    usage = await c.call("GET", "/warehouse/reports/consumption", 200, "consumption", h["coord"], params={"start": "2026-09-01", "end": "2027-03-31"})
    by_item = {row["label"]: (row["quantity"], row["cost_cents"]) for row in usage["by_item"]}
    c.expect(by_item == {"Papel A4": (6, 15000), "Bola de vôlei": (2, 16000)}, f"consumption: {by_item}")
    c.expect(usage["total_cost_cents"] == 31000 and usage["by_requester"][0]["label"] == "Prof", f"totals: {usage}")
    report = await c.call("GET", f"/social/funding-sources/{ctx['funding']}/report", 200, "funder sees materials", h["coord"])
    c.expect(report["materials_cost_cents"] == 31000 and report["budget_balance_cents"] == 69000, f"funding materials: {report['materials']}")
    mine = await c.call("GET", "/warehouse/my/requests", 200, "teacher history", prof)
    c.expect([r["status"] for r in mine] == ["delivered", "rejected", "cancelled", "closed"], f"history: {[r['status'] for r in mine]}")


async def run() -> int:
    ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with ApiClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        h = {name: await c.login(f"{name}@example.com") for name, _ in USERS}
        ctx = await setup(c, h, ids)
        h["almox"] = await c.login("almox@example.com")
        await check_request_cycle(c, h, ids, ctx)
        await check_stock_and_reports(c, h, ctx)

    if c.failures:
        print("Warehouse flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Warehouse flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
