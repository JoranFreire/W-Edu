"""Isolamento multi-tenant por instituicao.

A instituicao ativa fica em ``Session.info`` (vinculada por ``bind_institution``
na autenticacao). Com ela vinculada:

- toda consulta ORM a models com ``TenantMixin`` recebe o filtro
  ``institution_id = <ativa>``, inclusive em relationships e ``Session.get``;
- todo insert desses models sem ``institution_id`` recebe a instituicao ativa;
- usuarios ficam restritos aos membros da instituicao (e super admins).

Sessoes sem instituicao vinculada (worker, rotas publicas) nao sao filtradas.
Para uma consulta global deliberada use ``.execution_options(**UNSCOPED)``.
"""

from sqlalchemy import ForeignKey, event, or_, select
from sqlalchemy.orm import Mapped, ORMExecuteState, Session, declared_attr, mapped_column, with_loader_criteria


INSTITUTION_KEY = "institution_id"
SKIP_TENANT_FILTER = "skip_tenant_filter"
UNSCOPED = {SKIP_TENANT_FILTER: True}


class TenantMixin:
    @declared_attr
    def institution_id(cls) -> Mapped[int]:
        return mapped_column(ForeignKey("institutions.id"), index=True)


def bind_institution(db: Session, institution_id: int | None) -> None:
    if institution_id is None:
        db.info.pop(INSTITUTION_KEY, None)
    else:
        db.info[INSTITUTION_KEY] = institution_id


def bound_institution_id(db: Session) -> int | None:
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


@event.listens_for(Session, "before_flush")
def _assign_tenant_on_insert(session: Session, flush_context, instances) -> None:
    institution_id = bound_institution_id(session)
    for obj in session.new:
        if isinstance(obj, TenantMixin) and obj.institution_id is None:
            if institution_id is None:
                raise RuntimeError(f"{type(obj).__name__} criado sem instituicao vinculada a sessao")
            obj.institution_id = institution_id
