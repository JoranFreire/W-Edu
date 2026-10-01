"""Permissao efetiva: a do papel do usuario mais as dos perfis atribuidos na instituicao ativa."""

from fastapi import HTTPException, status

from app.models.student import Student
from app.services.access.catalog import role_permissions


def effective_permissions(user: Student) -> frozenset[str]:
    """`granted_permissions` e carregado na autenticacao; usuarios montados sem ela (testes) usam so o papel."""
    return role_permissions(user.role) | getattr(user, "granted_permissions", frozenset())


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
