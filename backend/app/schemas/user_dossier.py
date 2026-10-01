from datetime import date, datetime

from pydantic import BaseModel

from app.models.academic_groups import ProgramEnrollmentStatus
from app.models.guardians import GuardianRelationship
from app.models.school_life import OccurrenceKind, OccurrenceSeverity
from app.schemas.student import StudentOut


class DossierContact(BaseModel):
    phone: str | None = None
    document: str | None = None
    position: str | None = None
    department: str | None = None
    bio: str | None = None


class DossierPerson(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None = None


class DossierGuardianLink(BaseModel):
    """Vinculo aluno-responsavel visto pelo lado da outra pessoa (responsavel ou dependente)."""
    link_id: int
    person: DossierPerson
    relationship_kind: GuardianRelationship
    is_financial: bool
    is_primary: bool
    can_pick_up: bool


class DossierProgramEnrollment(BaseModel):
    id: int
    program_code: str
    program_name: str
    registration_number: str
    status: ProgramEnrollmentStatus
    enrolled_on: date
    entry_term_name: str | None = None


class DossierCourse(BaseModel):
    course_id: int
    course_name: str
    enrolled_at: datetime


class DossierCertificate(BaseModel):
    id: int
    course_name: str
    validation_code: str
    issued_at: datetime
    revoked: bool


class DossierFinance(BaseModel):
    open_count: int
    overdue_count: int
    open_cents: int
    next_due_at: datetime | None = None


class DossierOccurrence(BaseModel):
    id: int
    kind: OccurrenceKind
    severity: OccurrenceSeverity
    description: str
    occurred_on: date


class DossierOccurrences(BaseModel):
    total: int
    recent: list[DossierOccurrence]


class DossierOffering(BaseModel):
    id: int
    name: str
    course_name: str
    term_name: str | None = None


class UserDossier(BaseModel):
    """Visao consolidada de uma pessoa; secoes ficam nulas quando quem consulta nao tem a permissao."""
    user: StudentOut
    organization_name: str | None = None
    contact: DossierContact
    guardians: list[DossierGuardianLink] | None = None
    dependents: list[DossierGuardianLink] | None = None
    program_enrollments: list[DossierProgramEnrollment] | None = None
    courses: list[DossierCourse]
    certificates: list[DossierCertificate]
    finance: DossierFinance | None = None
    occurrences: DossierOccurrences | None = None
    teaching: list[DossierOffering] | None = None
