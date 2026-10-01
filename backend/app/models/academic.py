"""Estrutura curricular: unidades academicas, programas, disciplinas e matrizes."""

from uuid import UUID

from app.core.ids import new_id
from datetime import date, datetime, timezone
import enum

from sqlalchemy import Boolean, Date, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text, UniqueConstraint, false as sql_false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.tenancy import TenantMixin


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AcademicUnitKind(str, enum.Enum):
    segment = "segment"          # segmento escolar (Ensino Fundamental)
    faculty = "faculty"          # faculdade / centro
    department = "department"
    axis = "axis"                # eixo tecnologico
    other = "other"


class ProgramLevel(str, enum.Enum):
    basic = "basic"              # educacao basica (serie/etapa)
    technical = "technical"
    undergraduate = "undergraduate"
    graduate = "graduate"
    free = "free"                # curso livre


class ProgramStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    inactive = "inactive"


class CurriculumStatus(str, enum.Enum):
    draft = "draft"              # editavel
    active = "active"            # recebe ingressantes; uma por programa
    archived = "archived"        # vale para quem ja ingressou, sem edicao


class ComponentKind(str, enum.Enum):
    mandatory = "mandatory"
    elective = "elective"
    optional = "optional"


class AcademicUnit(TenantMixin, Base):
    __tablename__ = "academic_units"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    parent_id: Mapped[UUID | None] = mapped_column(ForeignKey("academic_units.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    kind: Mapped[AcademicUnitKind] = mapped_column(SAEnum(AcademicUnitKind), default=AcademicUnitKind.other)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    parent: Mapped["AcademicUnit | None"] = relationship(remote_side=[id], back_populates="children")
    children: Mapped[list["AcademicUnit"]] = relationship(back_populates="parent")
    programs: Mapped[list["Program"]] = relationship(back_populates="unit")


class Program(TenantMixin, Base):
    __tablename__ = "programs"
    __table_args__ = (UniqueConstraint("institution_id", "code"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    unit_id: Mapped[UUID | None] = mapped_column(ForeignKey("academic_units.id"), index=True)
    code: Mapped[str] = mapped_column(String(40))
    name: Mapped[str] = mapped_column(String(200))
    level: Mapped[ProgramLevel] = mapped_column(SAEnum(ProgramLevel), default=ProgramLevel.free)
    degree: Mapped[str | None] = mapped_column(String(120))
    duration_terms: Mapped[int | None] = mapped_column(Integer)
    total_hours: Mapped[int | None] = mapped_column(Integer)
    total_credits: Mapped[int | None] = mapped_column(Integer)
    # Requisitos de conclusao alem das disciplinas (Fase 16).
    complementary_hours: Mapped[int | None] = mapped_column(Integer)
    internship_hours: Mapped[int | None] = mapped_column(Integer)
    requires_final_project: Mapped[bool] = mapped_column(Boolean, default=False, server_default=sql_false())
    status: Mapped[ProgramStatus] = mapped_column(SAEnum(ProgramStatus), default=ProgramStatus.draft)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    unit: Mapped["AcademicUnit | None"] = relationship(back_populates="programs")
    curricula: Mapped[list["Curriculum"]] = relationship(back_populates="program", order_by="Curriculum.id")


class Subject(TenantMixin, Base):
    __tablename__ = "subjects"
    __table_args__ = (UniqueConstraint("institution_id", "code"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    code: Mapped[str] = mapped_column(String(40))
    name: Mapped[str] = mapped_column(String(200))
    syllabus: Mapped[str | None] = mapped_column(Text)
    hours: Mapped[int] = mapped_column(Integer, default=0)
    credits: Mapped[int | None] = mapped_column(Integer)
    # Conteudo EAD reaproveitado (aulas, quiz, professor IA) de um curso existente.
    course_id: Mapped[UUID | None] = mapped_column(ForeignKey("courses.id"), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    course: Mapped["Course | None"] = relationship()


class SubjectPrerequisite(TenantMixin, Base):
    __tablename__ = "subject_prerequisites"
    __table_args__ = (UniqueConstraint("subject_id", "required_subject_id"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    subject_id: Mapped[UUID] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    required_subject_id: Mapped[UUID] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)

    subject: Mapped["Subject"] = relationship(foreign_keys=[subject_id])
    required_subject: Mapped["Subject"] = relationship(foreign_keys=[required_subject_id])


class SubjectEquivalence(TenantMixin, Base):
    """Equivalencia simetrica, gravada uma vez com ``subject_id < equivalent_subject_id``."""

    __tablename__ = "subject_equivalences"
    __table_args__ = (UniqueConstraint("subject_id", "equivalent_subject_id"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    subject_id: Mapped[UUID] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)
    equivalent_subject_id: Mapped[UUID] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True)

    subject: Mapped["Subject"] = relationship(foreign_keys=[subject_id])
    equivalent_subject: Mapped["Subject"] = relationship(foreign_keys=[equivalent_subject_id])


class Curriculum(TenantMixin, Base):
    __tablename__ = "curricula"
    __table_args__ = (UniqueConstraint("program_id", "version"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    program_id: Mapped[UUID] = mapped_column(ForeignKey("programs.id"), index=True)
    version: Mapped[str] = mapped_column(String(40))
    valid_from: Mapped[date | None] = mapped_column(Date)
    status: Mapped[CurriculumStatus] = mapped_column(SAEnum(CurriculumStatus), default=CurriculumStatus.draft)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    program: Mapped["Program"] = relationship(back_populates="curricula")
    components: Mapped[list["CurriculumComponent"]] = relationship(
        back_populates="curriculum",
        order_by="(CurriculumComponent.term_number, CurriculumComponent.id)",
        cascade="all, delete-orphan",
    )


class CurriculumComponent(TenantMixin, Base):
    __tablename__ = "curriculum_components"
    __table_args__ = (UniqueConstraint("curriculum_id", "subject_id"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    curriculum_id: Mapped[UUID] = mapped_column(ForeignKey("curricula.id", ondelete="CASCADE"), index=True)
    subject_id: Mapped[UUID] = mapped_column(ForeignKey("subjects.id"), index=True)
    term_number: Mapped[int] = mapped_column(Integer)
    kind: Mapped[ComponentKind] = mapped_column(SAEnum(ComponentKind), default=ComponentKind.mandatory)
    # Sobrescrevem a carga da disciplina nesta matriz; vazio usa o valor da disciplina.
    hours: Mapped[int | None] = mapped_column(Integer)
    credits: Mapped[int | None] = mapped_column(Integer)

    curriculum: Mapped["Curriculum"] = relationship(back_populates="components")
    subject: Mapped["Subject"] = relationship()
