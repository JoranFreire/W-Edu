"""Exercise RBAC: permission catalog, built-in profiles from user roles, custom institution profiles granting permissions
to any member, revocation, no privilege escalation and tenant isolation.

Uses a temporary SQLite database by default (set DATABASE_URL to use PostgreSQL).
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
import sys

if "DATABASE_URL" not in os.environ:
    DB_PATH = Path(tempfile.gettempdir()) / f"wedu_access_check_{os.getpid()}.sqlite3"
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
USERS = {
    "escola-a": [("admin-a", UserRole.institution_admin), ("coord", UserRole.coordinator), ("secretaria", UserRole.secretary),
                 ("prof", UserRole.instructor), ("ana", UserRole.student), ("mae", UserRole.guardian)],
    "escola-b": [("admin-b", UserRole.institution_admin), ("prof-b", UserRole.instructor)],
}


def seed() -> dict[str, int]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    ids = {}
    with SessionLocal() as db:
        for slug, users in USERS.items():
            institution = Institution(slug=slug, name=slug.title(), type=InstitutionType.school)
            db.add(institution)
            db.flush()
            for name, role in users:
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


async def check_catalog(c: Checker, h: dict) -> None:
    catalog = await c.call("GET", "/access/permissions", 200, "catalog", h["admin-a"])
    c.expect({p["key"] for p in catalog} >= {"secretariat.access", "warehouse.manage", "access.manage"}, f"catalog: {catalog}")
    await c.call("GET", "/access/permissions", 403, "instructor cannot manage access", h["prof"])
    built_in = {p["role"]: set(p["permissions"]) for p in await c.call("GET", "/access/built-in", 200, "built-in profiles", h["admin-a"])}
    c.expect("secretariat.access" in built_in["secretary"] and "secretariat.access" not in built_in["instructor"], f"built-in: {built_in}")
    c.expect("guardian" not in built_in and "super_admin" not in built_in, "identity roles are not profiles")
    mine = await c.call("GET", "/access/me", 200, "my access", h["prof"])
    c.expect(mine["role"] == "instructor" and "teaching.access" in mine["permissions"] and "secretariat.access" not in mine["permissions"], f"me: {mine}")
    members = await c.call("GET", "/access/members", 200, "members", h["admin-a"])
    c.expect([m["name"] for m in members] == ["Admin-A", "Ana", "Coord", "Prof", "Secretaria"], f"members of A without guardian: {members}")


async def check_grant_and_revoke(c: Checker, h: dict, ids: dict) -> int:
    admin, prof = h["admin-a"], h["prof"]
    await c.call("GET", "/secretariat/students", 403, "instructor has no secretariat yet", prof)
    await c.call("POST", "/access/roles", 400, "unknown permission", admin, json={"name": "X", "permissions": ["nope"]})
    role = await c.call("POST", "/access/roles", 201, "create profile", admin,
                        json={"name": "Apoio da secretaria", "description": "Professor que ajuda na secretaria", "permissions": ["secretariat.access"]})
    await c.call("POST", "/access/roles", 409, "duplicate name", admin, json={"name": "Apoio da secretaria", "permissions": []})
    assigned = await c.call("POST", f"/access/roles/{role['id']}/members", 200, "assign to instructor", admin, json={"user_id": ids["prof"]})
    c.expect([m["name"] for m in assigned["members"]] == ["Prof"], f"assigned: {assigned}")
    await c.call("POST", f"/access/roles/{role['id']}/members", 200, "assign twice is idempotent", admin, json={"user_id": ids["prof"]})
    await c.call("POST", f"/access/roles/{role['id']}/members", 404, "guardian cannot get profiles", admin, json={"user_id": ids["mae"]})
    await c.call("POST", f"/access/roles/{role['id']}/members", 404, "user of another institution", admin, json={"user_id": ids["prof-b"]})
    await c.call("GET", "/secretariat/students", 200, "granted permission works", prof)
    mine = await c.call("GET", "/access/me", 200, "my access after grant", prof)
    c.expect("secretariat.access" in mine["permissions"], f"granted: {mine}")
    await c.call("GET", "/finance/plans", 200, "other routes keep working", prof)
    await c.call("DELETE", f"/access/roles/{role['id']}/members/{ids['prof']}", 200, "revoke", admin)
    await c.call("GET", "/secretariat/students", 403, "revoked permission", prof)
    await c.call("DELETE", f"/access/roles/{role['id']}/members/{ids['prof']}", 404, "revoke twice", admin)
    return role["id"]


async def check_no_escalation(c: Checker, h: dict, ids: dict, support_role: int) -> None:
    admin, coord = h["admin-a"], h["coord"]
    await c.call("GET", "/access/roles", 403, "coordinator does not manage access by default", coord)
    managers = await c.call("POST", "/access/roles", 201, "delegated access managers", admin, json={"name": "Gestão de perfis", "permissions": ["access.manage"]})
    await c.call("POST", f"/access/roles/{managers['id']}/members", 200, "delegate to coordinator", admin, json={"user_id": ids["coord"]})
    blocked = await c.call("POST", "/access/roles", 409, "cannot grant what you lack", coord, json={"name": "Financeiro", "permissions": ["finance.access"]})
    c.expect("finance.access" in blocked.get("detail", ""), f"escalation message: {blocked}")
    await c.call("POST", "/access/roles", 201, "grant what you have", coord, json={"name": "Docência extra", "permissions": ["teaching.access"]})
    admins = await c.call("POST", "/access/roles", 201, "admin-only profile", admin, json={"name": "Admin delegado", "permissions": ["institution.manage"]})
    await c.call("PUT", f"/access/roles/{admins['id']}", 409, "cannot edit a profile above you", coord, json={"name": "Admin delegado", "permissions": []})
    await c.call("POST", f"/access/roles/{admins['id']}/members", 409, "cannot assign a profile above you", coord, json={"user_id": ids["coord"]})
    await c.call("DELETE", f"/access/roles/{admins['id']}", 409, "cannot delete a profile above you", coord)
    updated = await c.call("PUT", f"/access/roles/{support_role}", 200, "edit own-level profile", coord,
                           json={"name": "Apoio da secretaria", "permissions": ["secretariat.access", "school_life.access"]})
    c.expect(updated["permissions"] == ["school_life.access", "secretariat.access"], f"updated: {updated}")
    await c.call("DELETE", f"/access/roles/{admins['id']}", 204, "admin deletes", admin)


async def check_isolation(c: Checker, h: dict, ids: dict, support_role: int) -> None:
    admin_b = h["admin-b"]
    listed = await c.call("GET", "/access/roles", 200, "B lists roles", admin_b)
    c.expect(listed == [], f"B sees no A roles: {listed}")
    await c.call("POST", f"/access/roles/{support_role}/members", 404, "B cannot use A role", admin_b, json={"user_id": ids["prof-b"]})
    await c.call("PUT", f"/access/roles/{support_role}", 404, "B cannot edit A role", admin_b, json={"name": "X", "permissions": []})
    own = await c.call("POST", "/access/roles", 201, "B profile", admin_b, json={"name": "Apoio", "permissions": ["secretariat.access"]})
    await c.call("POST", f"/access/roles/{own['id']}/members", 200, "B assigns own member", admin_b, json={"user_id": ids["prof-b"]})
    await c.call("GET", "/secretariat/students", 200, "B member granted", h["prof-b"])
    await c.call("GET", "/secretariat/students", 403, "A instructor not affected by B profile", h["prof"])


async def run() -> int:
    ids = seed()
    transport = httpx.ASGITransport(app=app)
    async with ApiClient(transport=transport, base_url="http://testserver") as client:
        c = Checker(client)
        h = {name: await c.login(f"{name}@example.com") for users in USERS.values() for name, _ in users}
        await check_catalog(c, h)
        support_role = await check_grant_and_revoke(c, h, ids)
        await check_no_escalation(c, h, ids, support_role)
        await check_isolation(c, h, ids, support_role)

    if c.failures:
        print("Access (RBAC) flow check failed:")
        for failure in c.failures:
            print(f"- {failure}")
        return 1
    print("Access (RBAC) flow check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
