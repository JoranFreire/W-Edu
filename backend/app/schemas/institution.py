from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.institution import InstitutionStatus, InstitutionType
from app.models.student import UserRole
from app.schemas.public_profile import PublicProfile


SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


class InstitutionSummary(BaseModel):
    id: UUID
    slug: str
    name: str
    type: InstitutionType
    branding: dict

    model_config = {"from_attributes": True}


class InstitutionOut(InstitutionSummary):
    legal_name: str | None
    document: str | None
    status: InstitutionStatus
    settings: dict
    custom_domain: str | None = None
    public_profile: dict = {}
    created_at: datetime


class InstitutionAdminCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)


class InstitutionCreate(BaseModel):
    slug: str = Field(min_length=2, max_length=80, pattern=SLUG_PATTERN)
    name: str
    legal_name: str | None = None
    document: str | None = None
    type: InstitutionType = InstitutionType.mixed
    settings: dict = Field(default_factory=dict)
    branding: dict = Field(default_factory=dict)
    admin: InstitutionAdminCreate | None = None


class InstitutionUpdate(BaseModel):
    name: str | None = None
    legal_name: str | None = None
    document: str | None = None
    type: InstitutionType | None = None
    settings: dict | None = None
    branding: dict | None = None
    # Conteudo da pagina publica (apresentacao, contatos); campos ausentes sao limpos.
    public_profile: PublicProfile | None = None


class PlatformInstitutionUpdate(InstitutionUpdate):
    status: InstitutionStatus | None = None


class MembershipOut(BaseModel):
    role: UserRole
    is_active: bool
    institution: InstitutionSummary

    model_config = {"from_attributes": True}


class SwitchInstitutionRequest(BaseModel):
    institution: str


class CampusCreate(BaseModel):
    name: str
    address: str | None = None
    is_active: bool = True


class CampusUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    is_active: bool | None = None


class CampusOut(BaseModel):
    id: UUID
    institution_id: UUID
    name: str
    address: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
