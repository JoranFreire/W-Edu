"""Isolamento multi-tenant por instituicao.

A instituicao ativa fica em ``Session.info`` (vinculada por ``bind_institution``
na autenticacao). Com ela vinculada:

- toda consulta ORM a models com ``TenantMixin`` recebe o filtro
  ``institution_id = <ativa>``, inclusive em relationships e ``Session.get``;
- todo insert desses models sem ``institution_id`` recebe a instituicao ativa;
- usuarios ficam restritos aos membros da instituicao (e super admins).

Sessoes sem instituicao vinculada (worker, webhooks, rotas publicas) nao sao
filtradas. As regras de gravacao ficam em ``app.core.tenant_integrity``.
Para uma consulta global deliberada use ``.execution_options(**UNSCOPED)``.
"""

from collections.abc import Callable
from uuid import UUID

from sqlalchemy import ForeignKey, event, or_, select
from sqlalchemy.orm import Mapped, ORMExecuteState, Session, declared_attr, mapped_column, with_loader_criteria

from app.core.ids import parse_id


INSTITUTION_KEY = "institution_id"
SKIP_TENANT_FILTER = "skip_tenant_filter"
UNSCOPED = {SKIP_TENANT_FILTER: True}


class TenantMixin:
    @declared_attr
    def institution_id(cls) -> Mapped[UUID]:
        return mapped_column(ForeignKey("institutions.id"), index=True)


BindHook = Callable[[Session, UUID | None], None]
_bind_hooks: list[BindHook] = []


def on_bind(hook: BindHook) -> BindHook:
    """Registra funcao chamada sempre que a instituicao da sessao muda (ex.: RLS)."""
    _bind_hooks.append(hook)
    return hook


def bind_institution(db: Session, institution_id: UUID | str | None) -> None:
    institution_id = parse_id(institution_id)
    if institution_id is None:
        db.info.pop(INSTITUTION_KEY, None)
    else:
        db.info[INSTITUTION_KEY] = institution_id
    for hook in _bind_hooks:
        hook(db, institution_id)


def bound_institution_id(db: Session) -> UUID | None:
    return db.info.get(INSTITUTION_KEY)


@event.listens_for(Session, "do_orm_execute")
def _apply_tenant_filter(state: ORMExecuteState) -> None:
    institution_id = bound_institution_id(state.session)
    if institution_id is None or state.execution_options.get(SKIP_TENANT_FILTER):
        return
    if not (state.is_select or state.is_update or state.is_delete):
        return

    from app.models.institution import InstitutionMembership
    from app.models.student import Student, UserRole

    state.statement = state.statement.options(
        with_loader_criteria(
            TenantMixin,
            lambda cls: cls.institution_id == institution_id,
            include_aliases=True,
        ),
        with_loader_criteria(
            Student,
            or_(
                Student.id.in_(
                    select(InstitutionMembership.user_id).where(
                        InstitutionMembership.institution_id == institution_id,
                        InstitutionMembership.is_active.is_(True),
                    )
                ),
                Student.role == UserRole.super_admin,
            ),
            include_aliases=True,
        ),
    )
