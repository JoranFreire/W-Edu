"""Vinculo do aluno ao programa e turmas-grupo (ex.: 7o ano A)."""

from datetime import date, datetime, timezone
import enum

from sqlalchemy import Date, DateTime, Enum as SAEnum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.tenancy import TenantMixin


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ProgramEnrollmentStatus(str, enum.Enum):
    active = "active"
    locked = "locked"            # trancado
    graduated = "graduated"
    dropped = "dropped"          # evadido
    transferred = "transferred"
    cancelled = "cancelled"


class Shift(str, enum.Enum):
    morning = "morning"
    afternoon = "afternoon"
    evening = "evening"
    full_time = "full_time"


class ProgramEnrollment(TenantMixin, Base):
    __tablename__ = "program_enrollments"
    __table_args__ = (UniqueConstraint("institution_id", "registration_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"), index=True)
    curriculum_id: Mapped[int] = mapped_column(ForeignKey("curricula.id"), index=True)
    entry_term_id: Mapped[int | None] = mapped_column(ForeignKey("academic_terms.id"), index=True)
    registration_number: Mapped[str] = mapped_column(String(40))
    status: Mapped[ProgramEnrollmentStatus] = mapped_column(
        SAEnum(ProgramEnrollmentStatus), default=ProgramEnrollmentStatus.active
    )
    enrolled_on: Mapped[date] = mapped_column(Date, default=lambda: _now().date())
    status_changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    # Transferencia interna: matricula de origem (outro programa da instituicao).
    transferred_from_id: Mapped[int | None] = mapped_column(ForeignKey("program_enrollments.id"), index=True)

    student: Mapped["Student"] = relationship()
    program: Mapped["Program"] = relationship()
    curriculum: Mapped["Curriculum"] = relationship()
    entry_term: Mapped["AcademicTerm | None"] = relationship()


class ClassGroup(TenantMixin, Base):
    __tablename__ = "class_groups"
    __table_args__ = (UniqueConstraint("term_id", "name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(ForeignKey("programs.id"), index=True)
    term_id: Mapped[int] = mapped_column(ForeignKey("academic_terms.id"), index=True)
    # Serie/semestre da matriz que a turma cursa (ex.: 7 para "7o ano A").
    curriculum_term_number: Mapped[int | None] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(80))
    shift: Mapped[Shift] = mapped_column(SAEnum(Shift), default=Shift.morning)
    capacity: Mapped[int | None] = mapped_column(Integer)
    homeroom_teacher_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    program: Mapped["Program"] = relationship()
    term: Mapped["AcademicTerm"] = relationship()
    homeroom_teacher: Mapped["Student | None"] = relationship()
    members: Mapped[list["ClassGroupMember"]] = relationship(back_populates="class_group", cascade="all, delete-orphan")


class ClassGroupMember(TenantMixin, Base):
    """Aluno (pela matricula no programa) alocado numa turma-grupo."""

    __tablename__ = "class_group_members"
    __table_args__ = (UniqueConstraint("class_group_id", "program_enrollment_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    class_group_id: Mapped[int] = mapped_column(ForeignKey("class_groups.id", ondelete="CASCADE"), index=True)
    program_enrollment_id: Mapped[int] = mapped_column(ForeignKey("program_enrollments.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    class_group: Mapped["ClassGroup"] = relationship(back_populates="members")
    program_enrollment: Mapped["ProgramEnrollment"] = relationship()
