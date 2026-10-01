"""Versao por area: toda gravacao em tabela acompanhada sobe a versao da area na instituicao.

As areas registram suas tabelas com ``track`` (ex.: ``app.services.sync.areas``). Depois de cada
flush, as instituicoes e areas tocadas por inserts, alteracoes e exclusoes recebem ``version + 1``
na mesma transacao: se ela for desfeita, a versao tambem e. Updates e deletes em massa
(``query.update``) sobem a versao da instituicao vinculada a sessao.

Limitacoes conhecidas: SQL textual e exclusoes em cascata feitas pelo banco nao sao vistos;
em massa sem instituicao vinculada (worker) tambem nao. O app sempre pode forcar o download
(puxar para atualizar).
"""

from collections.abc import Iterable
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import event, inspect
from sqlalchemy.orm import ORMExecuteState, Session

from app.core.ids import new_id
from app.core.tenancy import TenantMixin, bound_institution_id

_areas_by_model: dict[type, set[str]] = {}
_columns_by_model: dict[type, tuple[str, ...]] = {}


def track(model: type, *areas: str, columns: tuple[str, ...] = ()) -> None:
    """Gravacoes em ``model`` mudam os dados das ``areas``.

    Com ``columns``, alteracoes so contam quando tocam essas colunas (as que a tela mostra).
    """
    _areas_by_model.setdefault(model, set()).update(areas)
    if columns:
        _columns_by_model[model] = columns


def _areas_of(model: type) -> set[str]:
    return set().union(*(areas for cls, areas in _areas_by_model.items() if issubclass(model, cls)))


def _shown_columns_changed(obj) -> bool:
    columns = next((cols for cls, cols in _columns_by_model.items() if isinstance(obj, cls)), ())
    if not columns:
        return True
    state = inspect(obj)
    return any(state.attrs[column].history.has_changes() for column in columns)


def _institution_of(session: Session, obj) -> UUID | None:
    # Tabelas globais (usuarios) contam para a instituicao em que a alteracao foi feita.
    return obj.institution_id if isinstance(obj, TenantMixin) else bound_institution_id(session)


@event.listens_for(Session, "after_flush")
def _bump_after_flush(session: Session, flush_context) -> None:
    changed: set[tuple[UUID, str]] = set()
    dirty = [obj for obj in session.dirty if session.is_modified(obj) and _shown_columns_changed(obj)]
    for obj in [*session.new, *dirty, *session.deleted]:
        areas = _areas_of(type(obj))
        institution_id = _institution_of(session, obj) if areas else None
        if institution_id is not None:
            changed.update((institution_id, area) for area in areas)
    _bump(session, changed)


@event.listens_for(Session, "do_orm_execute")
def _bump_on_bulk_write(state: ORMExecuteState) -> None:
    institution_id = bound_institution_id(state.session)
    if institution_id is None or not (state.is_update or state.is_delete):
        return
    areas = set().union(*(_areas_of(mapper.class_) for mapper in state.all_mappers))
    _bump(state.session, {(institution_id, area) for area in areas})


def _bump(session: Session, changed: Iterable[tuple[UUID, str]]) -> None:
    from app.models.data_version import DataVersion

    rows = [
        {"id": new_id(), "institution_id": institution_id, "area": area, "version": 1, "updated_at": datetime.now(timezone.utc)}
        for institution_id, area in sorted(changed, key=lambda pair: (str(pair[0]), pair[1]))
    ]
    if not rows:
        return
    connection = session.connection()
    table = DataVersion.__table__
    statement = _dialect_insert(connection.dialect.name)(table)
    statement = statement.on_conflict_do_update(
        index_elements=[table.c.institution_id, table.c.area],
        set_={"version": table.c.version + 1, "updated_at": statement.excluded.updated_at},
    )
    connection.execute(statement, rows)


def _dialect_insert(dialect: str):
    if dialect == "postgresql":
        from sqlalchemy.dialects.postgresql import insert
    else:
        from sqlalchemy.dialects.sqlite import insert
    return insert
