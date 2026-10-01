"""Situacao do aluno num periodo letivo: o que ja cursou, o que tem inscrito e o que cada oferta exige."""
from __future__ import annotations
from uuid import UUID

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.academic import CurriculumComponent
from app.models.academic_groups import ProgramEnrollment
from app.models.schedule import ClassOffering, WaitlistEntry
from app.repositories.academic import SubjectPrerequisiteRepository
from app.repositories.registration import OfferingTimeSlotRepository, StudentRecordRepository
from app.repositories.secretariat import TranscriptRepository
from app.services.academic.summary import effective_credits
from app.services.registration.rules import Evaluation, WeeklySlot, clashing, evaluate, missing_prerequisites


@dataclass
class TermPlan:
    enrollment: ProgramEnrollment
    term_id: UUID
    done: set[UUID]
    components: dict[UUID, CurriculumComponent]
    enrolled: dict[UUID, ClassOffering]
    waitlisted: dict[UUID, WaitlistEntry]
    slots: dict[UUID, list[WeeklySlot]]
    prerequisites: dict[UUID, dict[UUID, str]]

    def credit_of(self, offering: ClassOffering) -> int:
        component = self.components.get(offering.subject_id)
        if component is not None:
            return effective_credits(component) or 0
        return (offering.subject.credits if offering.subject else None) or 0

    def registered_credits(self, excluding: int | None = None) -> int:
        return sum(self.credit_of(offering) for offering_id, offering in self.enrolled.items() if offering_id != excluding)

    def evaluate(self, offering: ClassOffering, seats_taken: int, max_credits: int | None) -> Evaluation:
        others = {offering_id: other for offering_id, other in self.enrolled.items() if offering_id != offering.id}
        same_subject = next((other.name for other in others.values() if other.subject_id == offering.subject_id), None)
        return evaluate(
            already_done=offering.subject_id in self.done,
            same_subject_in=same_subject,
            missing=missing_prerequisites(self.prerequisites.get(offering.subject_id, {}), self.done),
            clashes=clashing(self.slots.get(offering.id, []), {other.name: self.slots.get(other.id, []) for other in others.values()}),
            credits=self.credit_of(offering),
            registered_credits=self.registered_credits(excluding=offering.id),
            max_credits=max_credits,
            seats_left=offering.capacity - seats_taken,
        )


class TermPlanBuilder:
    def __init__(self, db: Session):
        self.records = StudentRecordRepository(db)
        self.slots = OfferingTimeSlotRepository(db)
        self.prerequisites = SubjectPrerequisiteRepository(db)
        self.transcripts = TranscriptRepository(db)

    def build(self, enrollment: ProgramEnrollment, term_id: UUID, candidates: list[ClassOffering]) -> TermPlan:
        student_id = enrollment.student_id
        enrolled = {e.class_offering_id: e.class_offering for e in self.records.term_enrollments(student_id, term_id)}
        offering_ids = list({*enrolled, *(offering.id for offering in candidates)})
        subject_ids = {offering.subject_id for offering in [*candidates, *enrolled.values()] if offering.subject_id}
        return TermPlan(
            enrollment=enrollment,
            term_id=term_id,
            done=self._done(enrollment),
            components={component.subject_id: component for component in enrollment.curriculum.components},
            enrolled=enrolled,
            waitlisted={entry.class_offering_id: entry for entry in self.records.term_waitlist(student_id, term_id)},
            slots={
                offering_id: [WeeklySlot(slot.weekday, slot.starts_at, slot.ends_at) for slot in slots]
                for offering_id, slots in self.slots.by_offerings(offering_ids).items()
            },
            prerequisites=self.prerequisites.required_names(subject_ids),
        )

    def _done(self, enrollment: ProgramEnrollment) -> set[UUID]:
        """Aprovadas e aproveitadas; a equivalente de uma cumprida tambem conta."""
        done = self.records.approved_subject_ids(enrollment.student_id) | self.records.credited_subject_ids(enrollment.id)
        for first, second in self.transcripts.equivalences(done):
            done |= {first, second}
        return done
