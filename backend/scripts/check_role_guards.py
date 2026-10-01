"""Validate role guard functions without touching the database."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import sys

from fastapi import HTTPException

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.dependencies import (
    ensure_super_admin_boundary,
    get_current_academic_staff,
    get_current_admin,
    get_current_admin_or_company_manager,
    get_current_admin_or_coordinator,
    get_current_finance_staff,
    get_current_guardian,
    get_current_school_staff,
    get_current_secretariat,
    get_current_super_admin,
    get_current_teaching_staff,
)
from app.models.student import ADMIN_ROLES, UserRole
from app.policies.user_scope import ensure_academic_user_scope


def fake_user(role: UserRole, organization_id: int | None = None):
    return SimpleNamespace(
        id=1,
        name=f"{role.value} user",
        email=f"{role.value}@example.com",
        role=role,
        organization_id=organization_id,
        is_active=True,
    )


def assert_allowed(name: str, fn, role: UserRole, organization_id: int | None = None) -> None:
    try:
        fn(fake_user(role, organization_id=organization_id))
    except HTTPException as exc:
        raise AssertionError(f"{name}: expected {role.value} to be allowed, got {exc.status_code}") from exc


def assert_forbidden(name: str, fn, role: UserRole, organization_id: int | None = None) -> None:
    try:
        fn(fake_user(role, organization_id=organization_id))
    except HTTPException as exc:
        if exc.status_code == 403:
            return
        raise AssertionError(f"{name}: expected {role.value} to get 403, got {exc.status_code}") from exc
    raise AssertionError(f"{name}: expected {role.value} to be forbidden")


def assert_scope_allowed(name: str, current_role: UserRole, target_role: UserRole, current_org: int | None = None, target_org: int | None = None) -> None:
    try:
        ensure_academic_user_scope(
            fake_user(current_role, organization_id=current_org),
            fake_user(target_role, organization_id=target_org),
        )
    except HTTPException as exc:
        raise AssertionError(
            f"{name}: expected {current_role.value} to manage {target_role.value}, got {exc.status_code}"
        ) from exc


def assert_scope_forbidden(name: str, current_role: UserRole, target_role: UserRole, current_org: int | None = None, target_org: int | None = None) -> None:
    try:
        ensure_academic_user_scope(
            fake_user(current_role, organization_id=current_org),
            fake_user(target_role, organization_id=target_org),
        )
    except HTTPException as exc:
        if exc.status_code == 403:
            return
        raise AssertionError(
            f"{name}: expected {current_role.value} managing {target_role.value} to get 403, got {exc.status_code}"
        ) from exc
    raise AssertionError(f"{name}: expected {current_role.value} managing {target_role.value} to be forbidden")


def main() -> int:
    failures: list[str] = []
    checks = [
        ("super_admin", get_current_super_admin, [UserRole.super_admin], [UserRole.admin, UserRole.institution_admin, UserRole.coordinator, UserRole.student]),
        ("admin", get_current_admin, [*ADMIN_ROLES], [UserRole.student, UserRole.instructor, UserRole.coordinator, UserRole.company_manager, UserRole.secretary, UserRole.guardian]),
        (
            "admin_or_coordinator",
            get_current_admin_or_coordinator,
            [*ADMIN_ROLES, UserRole.coordinator],
            [UserRole.student, UserRole.instructor, UserRole.company_manager, UserRole.secretary, UserRole.guardian],
        ),
        (
            "academic_staff",
            get_current_academic_staff,
            [*ADMIN_ROLES, UserRole.coordinator, UserRole.company_manager],
            [UserRole.student, UserRole.instructor, UserRole.secretary, UserRole.guardian],
        ),
        (
            "admin_or_company_manager",
            get_current_admin_or_company_manager,
            [*ADMIN_ROLES, UserRole.company_manager],
            [UserRole.student, UserRole.instructor, UserRole.coordinator, UserRole.secretary, UserRole.guardian],
        ),
        (
            "teaching_staff",
            get_current_teaching_staff,
            [*ADMIN_ROLES, UserRole.coordinator, UserRole.instructor],
            [UserRole.student, UserRole.company_manager, UserRole.secretary, UserRole.guardian],
        ),
        (
            "guardian",
            get_current_guardian,
            [UserRole.guardian],
            [*ADMIN_ROLES, UserRole.student, UserRole.instructor, UserRole.coordinator, UserRole.secretary, UserRole.company_manager],
        ),
        (
            "secretariat",
            get_current_secretariat,
            [*ADMIN_ROLES, UserRole.coordinator, UserRole.secretary],
            [UserRole.student, UserRole.instructor, UserRole.company_manager, UserRole.guardian],
        ),
        (
            "finance_staff",
            get_current_finance_staff,
            [*ADMIN_ROLES, UserRole.secretary],
            [UserRole.student, UserRole.instructor, UserRole.coordinator, UserRole.company_manager, UserRole.guardian],
        ),
        (
            "school_staff",
            get_current_school_staff,
            [*ADMIN_ROLES, UserRole.coordinator, UserRole.instructor, UserRole.secretary],
            [UserRole.student, UserRole.company_manager, UserRole.guardian],
        ),
    ]

    for name, fn, allowed_roles, forbidden_roles in checks:
        for role in allowed_roles:
            organization_id = 1 if role == UserRole.company_manager else None
            try:
                assert_allowed(name, fn, role, organization_id=organization_id)
            except AssertionError as exc:
                failures.append(str(exc))
        for role in forbidden_roles:
            organization_id = 1 if role == UserRole.company_manager else None
            try:
                assert_forbidden(name, fn, role, organization_id=organization_id)
            except AssertionError as exc:
                failures.append(str(exc))

    try:
        assert_forbidden("academic_staff_company_manager_without_org", get_current_academic_staff, UserRole.company_manager)
        assert_forbidden(
            "admin_or_company_manager_without_org",
            get_current_admin_or_company_manager,
            UserRole.company_manager,
        )
    except AssertionError as exc:
        failures.append(str(exc))

    scope_checks = [
        ("admin_can_manage_admin", assert_scope_allowed, UserRole.admin, UserRole.admin, None, None),
        ("institution_admin_can_manage_coordinator", assert_scope_allowed, UserRole.institution_admin, UserRole.coordinator, None, None),
        ("coordinator_cannot_manage_institution_admin", assert_scope_forbidden, UserRole.coordinator, UserRole.institution_admin, None, None),
        ("coordinator_cannot_manage_secretary", assert_scope_forbidden, UserRole.coordinator, UserRole.secretary, None, None),
        ("coordinator_can_manage_student", assert_scope_allowed, UserRole.coordinator, UserRole.student, None, None),
        ("coordinator_can_manage_instructor", assert_scope_allowed, UserRole.coordinator, UserRole.instructor, None, None),
        ("coordinator_cannot_manage_admin", assert_scope_forbidden, UserRole.coordinator, UserRole.admin, None, None),
        ("coordinator_cannot_manage_coordinator", assert_scope_forbidden, UserRole.coordinator, UserRole.coordinator, None, None),
        ("company_manager_can_manage_own_student", assert_scope_allowed, UserRole.company_manager, UserRole.student, 1, 1),
        ("company_manager_cannot_manage_other_student", assert_scope_forbidden, UserRole.company_manager, UserRole.student, 1, 2),
        ("company_manager_cannot_manage_own_manager", assert_scope_forbidden, UserRole.company_manager, UserRole.company_manager, 1, 1),
    ]
    for name, fn, current_role, target_role, current_org, target_org in scope_checks:
        try:
            fn(name, current_role, target_role, current_org, target_org)
        except AssertionError as exc:
            failures.append(str(exc))

    # Somente super admin atribui ou altera o papel super_admin.
    boundary_checks = [
        ("super_admin_can_grant_super_admin", UserRole.super_admin, UserRole.super_admin, None, True),
        ("institution_admin_cannot_grant_super_admin", UserRole.institution_admin, UserRole.super_admin, None, False),
        ("institution_admin_cannot_edit_super_admin", UserRole.institution_admin, None, UserRole.super_admin, False),
        ("institution_admin_can_edit_student", UserRole.institution_admin, UserRole.student, UserRole.student, True),
    ]
    for name, current_role, new_role, target_role, allowed in boundary_checks:
        target = fake_user(target_role) if target_role else None
        try:
            ensure_super_admin_boundary(fake_user(current_role), new_role, target)
            if not allowed:
                failures.append(f"{name}: expected 403")
        except HTTPException as exc:
            if allowed or exc.status_code != 403:
                failures.append(f"{name}: unexpected {exc.status_code}")

    if failures:
        print("Role guard check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Role guard check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
