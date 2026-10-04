from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.finance import ChargeStatus
from app.models.guardians import GuardianRelationship
from app.schemas.academic_groups import PersonSummary


class GuardianLinkCreate(BaseModel):
    """Vincula um responsavel ja cadastrado (e-mail existente) ou cria a conta dele."""

    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    password: str | None = Field(default=None, min_length=6)
    relationship_kind: GuardianRelationship = GuardianRelationship.other
    is_financial: bool = False
    can_pick_up: bool = True
    is_primary: bool = False


class GuardianLinkUpdate(BaseModel):
    relationship_kind: GuardianRelationship | None = None
    is_financial: bool | None = None
    can_pick_up: bool | None = None
    is_primary: bool | None = None


class GuardianLinkOut(BaseModel):
    id: UUID
    student: PersonSummary
    guardian: PersonSummary
    relationship_kind: GuardianRelationship
    is_financial: bool
    can_pick_up: bool
    is_primary: bool

    model_config = {"from_attributes": True}


class DependentOut(BaseModel):
    link_id: UUID
    student: PersonSummary
    relationship_kind: GuardianRelationship
    is_financial: bool
    can_pick_up: bool
    # Maioridade do aluno (sem data de nascimento, falso): o login facial de menor
    # depende da autorizacao do responsavel; a de adulto, so dele (Persona).
    student_is_adult: bool = False
    # A partir de 16 anos o proprio aluno decide login e catraca faciais; abaixo, o responsavel.
    student_is_16_or_older: bool = False


class DependentChargeOut(BaseModel):
    id: UUID
    amount_cents: int
    currency: str
    status: ChargeStatus
    due_at: datetime | None
    checkout_url: str | None
    bank_slip_url: str | None

    model_config = {"from_attributes": True}


class DependentNoticeOut(BaseModel):
    id: UUID
    title: str
    body: str
    created_at: datetime

    model_config = {"from_attributes": True}
