"""Registra o fim de vinculo (``membership_events``) a cada gravacao que o encerra.

Depois do flush: vinculo que passou de ativo a inativo ou foi removido, e conta desativada
(encerra todos os vinculos ativos dela). Gravado na mesma transacao: desfeita a mudanca,
desfeito o evento. Nao ve SQL textual nem updates em massa.
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import event, inspect, insert, select
from sqlalchemy.orm import Session

from app.core.ids import new_id


def _deactivated(obj) -> bool:
    history = inspect(obj).attrs.is_active.history
    return bool(history.deleted) and history.deleted[0] is True and obj.is_active is False


@event.listens_for(Session, "after_flush")
def _record_membership_end(session: Session, flush_context) -> None:
    from app.models.institution import InstitutionMembership
    from app.models.membership_event import MembershipEvent
    from app.models.student import Student

    ended: set[tuple[UUID, UUID]] = set()
    for obj in session.dirty:
        if isinstance(obj, InstitutionMembership) and _deactivated(obj):
            ended.add((obj.institution_id, obj.user_id))
    for obj in session.deleted:
        if isinstance(obj, InstitutionMembership) and obj.is_active:
            ended.add((obj.institution_id, obj.user_id))

    connection = session.connection()
    deactivated_users = [obj.id for obj in session.dirty if isinstance(obj, Student) and _deactivated(obj)]
    if deactivated_users:
        rows = connection.execute(
            select(InstitutionMembership.institution_id, InstitutionMembership.user_id)
            .where(InstitutionMembership.user_id.in_(deactivated_users), InstitutionMembership.is_active.is_(True))
        )
        ended.update((institution_id, user_id) for institution_id, user_id in rows)

    if ended:
        now = datetime.now(timezone.utc)
        connection.execute(insert(MembershipEvent.__table__), [
            {"id": new_id(), "institution_id": institution_id, "user_id": user_id, "kind": "ended", "created_at": now}
            for institution_id, user_id in sorted(ended, key=lambda pair: (str(pair[0]), str(pair[1])))
        ])
