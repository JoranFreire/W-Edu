"""Permissao efetiva: a de cada papel da pessoa na instituicao ativa mais as dos perfis atribuidos."""

from fastapi import HTTPException, status

from app.models.student import Student
from app.policies.roles import roles_of
from app.services.access.catalog import role_permissions


def effective_permissions(user: Student) -> frozenset[str]:
    """Papeis e `granted_permissions` vem da autenticacao; usuarios montados sem eles (testes) usam so o papel principal."""
    by_roles = frozenset().union(*(role_permissions(role) for role in roles_of(user)))
    return by_roles | getattr(user, "granted_permissions", frozenset())


def has_permission(user: Student, key: str) -> bool:
    return key in effective_permissions(user)


def ensure_permission(user: Student, key: str, detail: str) -> Student:
    if not has_permission(user, key):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
    return user


def ensure_any_permission(user: Student, keys: tuple[str, ...], detail: str) -> Student:
    if not any(has_permission(user, key) for key in keys):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
    return user
