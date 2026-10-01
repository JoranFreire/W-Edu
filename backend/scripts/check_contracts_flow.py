"""Exercise enrollment contracts (phase 17, delivery 2): templates, issuing into the GED, electronic acceptance by the
student or the financial guardian, cancellation and public validation with tamper detection.

Uses a temporary SQLite database by default (set DATABASE_URL to use PostgreSQL).
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
import sys

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_contracts_check_{os.getpid()}.sqlite3"
    os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["NOTIFICATION_WORKER_ENABLED"] = "false"
os.environ.setdefault("DOCUMENTS_STORAGE_DIR", tempfile.mkdtemp(prefix="wedu_contracts_"))

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
from app.models.contracts import EnrollmentContract
from app.models.document import Document, DocumentType
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
    ("coord", UserRole.coordinator),
    ("secretaria", UserRole.secretary),
    ("ana", UserRole.student),
    ("bia", UserRole.student),
)


def seed() -> dict[str, int]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ids = {}
    with SessionLocal() as db:
        institution = Institution(slug="colegio", name="Colégio Exemplo", type=InstitutionType.school)
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


BODY = """CONTRATO DE PRESTACAO DE SERVICOS EDUCACIONAIS

{institution_name} e {payer_name}, responsavel financeiro por {student_name} (matricula {registration_number}), ajustam a matricula no programa {program_name} para o periodo {term_name}.

Valores conforme tabela vigente. Data: {date}."""


async def setup_structure(c: Checker, h: dict, ids: dict) -> dict:
    coord, sec = h["coord"], h["secretaria"]
    term = await c.call("POST", "/academic/terms", 201, "term", coord, json={"name": "2027", "starts_on": "2027-02-01", "ends_on": "2027-12-15"})
    program = await c.call("POST", "/academic/programs", 201, "program", coord, json={"code": "EF", "name": "Fundamental", "level": "basic"})
    curriculum = await c.call("POST", f"/academic/programs/{program['id']}/curricula", 201, "curriculum", coord, json={"version": "1"})
    subject = await c.call("POST", "/academic/subjects", 201, "subject", coord, json={"code": "MAT", "name": "Matemática", "hours": 160})
    await c.call("POST", f"/academic/curricula/{curriculum['id']}/components", 201, "component", coord, json={"subject_id": subject["id"], "term_number": 1})
    await c.call("POST", f"/academic/curricula/{curriculum['id']}/activate", 200, "activate", coord)
    enrollments = {}
    for name in ("ana", "bia"):
        enrollments[name] = (await c.call("POST", "/academic/program-enrollments", 201, f"enroll {name}", coord,
                                          json={"student_id": ids[name], "program_id": program["id"]}))["id"]
    await c.call("POST", f"/guardians/students/{ids['ana']}/links", 201, "financial guardian", sec,
                 json={"name": "Maria", "email": "maria@example.com", "password": PASSWORD, "relationship_kind": "mother", "is_financial": True})
    await c.call("POST", f"/guardians/students/{ids['ana']}/links", 201, "other guardian", sec,
                 json={"name": "Joao", "email": "joao@example.com", "password": PASSWORD, "relationship_kind": "father"})
    return {"term": term["id"], "enrollments": enrollments}


async def check_templates(c: Checker, h: dict) -> dict:
    sec = h["secretaria"]
    await c.call("POST", "/contracts/templates", 403, "student cannot create template", h["ana"], json={"name": "X", "body": "Y"})
    await c.call("POST", "/contracts/templates", 400, "loose brace", sec, json={"name": "Quebrado", "body": "Valor { sem fechar"})
    enrollment = await c.call("POST", "/contracts/templates", 201, "enrollment template", sec, json={"name": "Contrato de matrícula", "body": BODY})
    reenrollment = await c.call("POST", "/contracts/templates", 201, "reenrollment template", sec,
                                json={"name": "Rematrícula", "kind": "reenrollment", "body": "Rematricula de {student_name} em {term_name}."})
    inactive = await c.call("POST", "/contracts/templates", 201, "template to deactivate", sec, json={"name": "Antigo", "body": "Texto"})
    await c.call("PATCH", f"/contracts/templates/{inactive['id']}", 200, "deactivate template", sec, json={"is_active": False})
    return {"enrollment": enrollment["id"], "reenrollment": reenrollment["id"], "inactive": inactive["id"]}


async def check_issue_and_accept(c: Checker, h: dict, ctx: dict, templates: dict) -> dict:
    sec, ana = h["secretaria"], ctx["enrollments"]["ana"]
    await c.call("POST", f"/contracts/enrollments/{ana}", 409, "inactive template", sec, json={"template_id": templates["inactive"]})
    contract = await c.call("POST", f"/contracts/enrollments/{ana}", 201, "issue", sec, json={"template_id": templates["enrollment"], "term_id": ctx["term"]})
    body = contract.get("body", "")
    c.expect(contract.get("status") == "pending" and "Maria, responsavel financeiro por Ana" in body and "periodo 2027" in body
             and "Colégio Exemplo" in body, f"rendered body: {contract}")
    c.expect(contract.get("document_id") is not None, f"archived in GED: {contract}")
    with SessionLocal() as db:
        document = db.get(Document, contract["document_id"])
        c.expect(document.document_type == DocumentType.contract and document.latest_version_number == 1
                 and str(document.student_id) == ctx["ids"]["ana"], f"GED document: {document.__dict__}")
    response = await c.client.get(f"/contracts/{contract['id']}/pdf", headers=sec)
    c.expect(response.status_code == 200 and response.content.startswith(b"%PDF"), f"office pdf: {response.status_code}")
    listed = await c.call("GET", f"/contracts/enrollments/{ana}", 200, "office list", sec)
    c.expect(len(listed) == 1, f"listed: {listed}")

    maria, joao = await c.login("maria@example.com"), await c.login("joao@example.com")
    for headers, expected, label in ((h["ana"], 1, "student"), (maria, 1, "financial guardian"), (joao, 0, "other guardian"), (h["bia"], 0, "other student")):
        mine = await c.call("GET", "/contracts/my", 200, f"{label} contracts", headers)
        c.expect(len(mine) == expected, f"{label} sees {len(mine)} contracts")
    await c.call("POST", f"/contracts/my/{contract['id']}/accept", 404, "other student cannot accept", h["bia"])
    await c.call("POST", f"/contracts/my/{contract['id']}/accept", 404, "non-financial guardian cannot accept", joao)
    response = await c.client.get(f"/contracts/my/{contract['id']}/pdf", headers=maria)
    c.expect(response.status_code == 200 and response.content.startswith(b"%PDF"), f"party pdf: {response.status_code}")
    signed = await c.call("POST", f"/contracts/my/{contract['id']}/accept", 200, "financial guardian accepts", maria)
    c.expect(signed.get("status") == "signed" and signed.get("signer_name") == "Maria" and signed.get("signed_at"), f"signed: {signed}")
    await c.call("POST", f"/contracts/my/{contract['id']}/accept", 409, "accept twice", h["ana"])
    await c.call("POST", f"/contracts/{contract['id']}/cancel", 409, "signed contract cannot be cancelled", sec)
    with SessionLocal() as db:
        document = db.get(Document, contract["document_id"])
        c.expect(document.latest_version_number == 2 and document.is_signed and document.signed_by == "Maria", f"signed version in GED: {document.__dict__}")
    return contract


async def check_validation_and_cancel(c: Checker, h: dict, ctx: dict, templates: dict, contract: dict) -> None:
    sec, bia = h["secretaria"], ctx["enrollments"]["bia"]
    valid = await c.call("GET", f"/contracts/validate/{contract['validation_code']}", 200, "public validation", {})
    c.expect(valid.get("valid") is True and valid.get("signer_name") == "Maria" and valid.get("institution_name") == "Colégio Exemplo", f"valid: {valid}")
    unknown = await c.call("GET", "/contracts/validate/nao-existe", 200, "unknown code", {})
    c.expect(unknown.get("valid") is False, f"unknown: {unknown}")
    with SessionLocal() as db:
        stored = db.get(EnrollmentContract, contract["id"])
        stored.body = stored.body.replace("tabela vigente", "tabela alterada")
        db.commit()
    tampered = await c.call("GET", f"/contracts/validate/{contract['validation_code']}", 200, "tampered", {})
    c.expect(tampered.get("valid") is False and "adulterado" in tampered.get("message", ""), f"tamper detected: {tampered}")

    other = await c.call("POST", f"/contracts/enrollments/{bia}", 201, "reenrollment contract", sec, json={"template_id": templates["reenrollment"], "term_id": ctx["term"]})
    c.expect(other.get("kind") == "reenrollment" and other.get("body") == "Rematricula de Bia em 2027.", f"reenrollment: {other}")
    pending = await c.call("GET", f"/contracts/validate/{other['validation_code']}", 200, "pending validation", {})
    c.expect(pending.get("valid") is False and "não aceito" in pending.get("message", ""), f"pending: {pending}")
    cancelled = await c.call("POST", f"/contracts/{other['id']}/cancel", 200, "cancel", sec)
    c.expect(cancelled.get("status") == "cancelled", f"cancelled: {cancelled}")
    await c.call("POST", f"/contracts/my/{other['id']}/accept", 409, "cannot accept cancelled", h["bia"])
    result = await c.call("GET", f"/contracts/validate/{other['validation_code']}", 200, "cancelled validation", {})
    c.expect(result.get("valid") is False and result.get("message") == "Contrato cancelado", f"cancelled validation: {result}")


async def run() -> int:
    ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with ApiClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        h = {name: await c.login(f"{name}@example.com") for name, _ in USERS}
        ctx = await setup_structure(c, h, ids)
        ctx["ids"] = ids
        templates = await check_templates(c, h)
        contract = await check_issue_and_accept(c, h, ctx, templates)
        await check_validation_and_cancel(c, h, ctx, templates, contract)

    if c.failures:
        print("Contracts flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Contracts flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
