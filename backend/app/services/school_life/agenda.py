from __future__ import annotations
from uuid import UUID

from datetime import date

from sqlalchemy.orm import Session

from app.models.academic_groups import ClassGroup
from app.models.school_life import AgendaItem
from app.models.student import Student
from app.policies.school_life_access import ensure_can_publish_agenda, ensure_can_remove
from app.repositories.academic import ClassGroupMemberRepository, ClassGroupRepository
from app.repositories.schedule import ClassOfferingRepository
from app.repositories.school_life import AgendaRepository
from app.schemas.school_life import AgendaItemCreate, AgendaItemOut
from app.services.academic.errors import bad_request, not_found
from app.services.school_life.family_notices import FamilyNoticeService


def to_out(item: AgendaItem) -> AgendaItemOut:
    return AgendaItemOut(
        id=item.id, class_group_id=item.class_group_id, class_group_name=item.class_group.name,
        class_offering_id=item.class_offering_id, class_offering_name=item.class_offering.name if item.class_offering else None,
        kind=item.kind, title=item.title, description=item.description, due_on=item.due_on, created_at=item.created_at,
    )


class AgendaService:
    """Agenda da turma: tarefas, provas, eventos e avisos publicados pela equipe escolar."""

    def __init__(self, db: Session):
        self.repo = AgendaRepository(db)
        self.groups = ClassGroupRepository(db)
        self.members = ClassGroupMemberRepository(db)
        self.offerings = ClassOfferingRepository(db)
        self.notices = FamilyNoticeService(db)

    def list_for_group(self, group_id: UUID, from_date: date | None = None) -> list[AgendaItemOut]:
        self._group_or_404(group_id)
        return [to_out(item) for item in self.repo.list_by_groups([group_id], from_date)]

    def for_student(self, student_id: UUID, from_date: date | None = None) -> list[AgendaItemOut]:
        group_ids = [group.id for group in self.members.groups_of_student(student_id)]
        return [to_out(item) for item in self.repo.list_by_groups(group_ids, from_date)]

    def publish(self, group_id: UUID, data: AgendaItemCreate, author: Student) -> AgendaItemOut:
        group = self._group_or_404(group_id)
        ensure_can_publish_agenda(author, group, self.groups.taught_by(group.id, author.id))
        if data.class_offering_id is not None:
            offering = self.offerings.get_by_id(data.class_offering_id)
            if not offering or offering.class_group_id != group.id:
                raise bad_request("A oferta não pertence a esta turma")
        item = self.repo.add(AgendaItem(
            class_group_id=group.id, class_offering_id=data.class_offering_id, kind=data.kind, title=data.title,
            description=data.description, due_on=data.due_on, created_by_id=author.id,
        ))
        self.repo.db.flush()
        self.notices.agenda_published(item, self.members.student_ids(group.id))
        return to_out(self.repo.save(item))

    def remove(self, item_id: UUID, user: Student) -> None:
        item = self.repo.get_by_id(item_id)
        if not item:
            raise not_found("Item da agenda não encontrado")
        ensure_can_remove(user, item.created_by_id)
        self.repo.delete(item)

    def _group_or_404(self, group_id: UUID) -> ClassGroup:
        group = self.groups.get_by_id(group_id)
        if not group:
            raise not_found("Turma não encontrada")
        return group
