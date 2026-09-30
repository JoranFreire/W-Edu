"""Isolamento multi-tenant por instituicao.

A instituicao ativa fica em ``Session.info`` (vinculada por ``bind_institution``
na autenticacao). Com ela vinculada:

- toda consulta ORM a models com ``TenantMixin`` recebe o filtro
  ``institution_id = <ativa>``, inclusive em relationships e ``Session.get``;
- todo insert desses models sem ``institution_id`` recebe a instituicao ativa;
- usuarios ficam restritos aos membros da instituicao (e super admins).

Em toda gravacao, registros e usuarios referenciados por FK precisam ser da
mesma instituicao; do contrario a operacao falha com 404.

Sessoes sem instituicao vinculada (worker, webhooks, rotas publicas) nao sao
filtradas; inserts nelas herdam a instituicao do registro pai.
Para uma consulta global deliberada use ``.execution_options(**UNSCOPED)``.
"""

from fastapi import HTTPException, status
from sqlalchemy import ForeignKey, event, inspect, or_, select
from sqlalchemy.orm import MANYTOONE, Mapped, ORMExecuteState, Session, declared_attr, mapped_column, with_loader_criteria


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
def _enforce_tenant_on_write(session: Session, flush_context, instances) -> None:
    bound = bound_institution_id(session)
    new = [obj for obj in session.new if isinstance(obj, TenantMixin)]
    _assign_institution(session, [obj for obj in new if obj.institution_id is None], bound)

    dirty = [obj for obj in session.dirty if isinstance(obj, TenantMixin) and session.is_modified(obj)]
    for obj in new + dirty:
        if bound is not None and obj.institution_id != bound:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Registro de outra instituição")
        for target, related, value in _references(obj, changed_only=obj not in new):
            if issubclass(target, TenantMixin):
                parent_institution = _institution_of(session, target, related, value)
                if parent_institution is not None and parent_institution != obj.institution_id:
                    raise _cross_tenant_error()
            elif not _is_member(session, obj.institution_id, related, value):
                raise _cross_tenant_error()


def _assign_institution(session: Session, pending: list[TenantMixin], bound: int | None) -> None:
    if bound is not None:
        for obj in pending:
            obj.institution_id = bound
        return
    # Sem instituicao ativa (webhooks, worker): herda a instituicao do registro pai.
    while pending:
        resolved = []
        for obj in pending:
            parents = {
                _institution_of(session, target, related, value)
                for target, related, value in _references(obj, changed_only=False)
                if issubclass(target, TenantMixin)
            } - {None}
            if len(parents) > 1:
                raise _cross_tenant_error()
            if parents:
                obj.institution_id = parents.pop()
                resolved.append(obj)
        if not resolved:
            names = ", ".join(sorted({type(obj).__name__ for obj in pending}))
            raise RuntimeError(f"{names} criado sem instituicao vinculada a sessao")
        pending = [obj for obj in pending if obj not in resolved]


def _references(obj: TenantMixin, changed_only: bool):
    """Registros de instituicao ou usuarios referenciados por FK simples (many-to-one)."""
    from app.models.student import Student

    state = inspect(obj)
    for rel in state.mapper.relationships:
        target = rel.mapper.class_
        if rel.direction is not MANYTOONE or len(rel.local_columns) != 1:
            continue
        if not (issubclass(target, TenantMixin) or issubclass(target, Student)):
            continue
        column_key = state.mapper.get_property_by_column(next(iter(rel.local_columns))).key
        if changed_only and not (
            state.attrs[column_key].history.has_changes() or state.attrs[rel.key].history.has_changes()
        ):
            continue
        yield target, state.dict.get(rel.key), state.dict.get(column_key)


def _institution_of(session: Session, target: type, related, value) -> int | None:
    if related is not None:
        return related.institution_id
    if value is None:
        return None
    pk = inspect(target).primary_key[0]
    return session.execute(
        select(target.institution_id).where(pk == value).execution_options(**UNSCOPED)
    ).scalar_one_or_none()


def _is_member(session: Session, institution_id: int, related, value) -> bool:
    from app.models.institution import InstitutionMembership
    from app.models.student import Student, UserRole

    user_id = related.id if related is not None else value
    if user_id is None:
        return True
    membership = session.execute(
        select(InstitutionMembership.id).where(
            InstitutionMembership.institution_id == institution_id,
            InstitutionMembership.user_id == user_id,
        )
    ).first()
    if membership:
        return True
    role = session.execute(
        select(Student.role).where(Student.id == user_id).execution_options(**UNSCOPED)
    ).scalar_one_or_none()
    return role == UserRole.super_admin


def _cross_tenant_error() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro relacionado não encontrado nesta instituição")
