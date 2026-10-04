from uuid import UUID
from datetime import date, datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, EmailStr, Field
from app.models.student import UserRole


def _not_in_future(value: date) -> date:
    if value > date.today():
        raise ValueError("Data de nascimento no futuro")
    return value


BirthDate = Annotated[date, AfterValidator(_not_in_future)]


class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.student
    # Todos os papeis na instituicao (aluno e professor, por exemplo); sem a lista, so `role`.
    roles: list[UserRole] | None = None
    organization_id: UUID | None = None
    birth_date: BirthDate | None = None


class StudentUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    role: UserRole | None = None
    roles: list[UserRole] | None = None
    organization_id: UUID | None = None
    is_active: bool | None = None
    birth_date: BirthDate | None = None


class OrganizationCreate(BaseModel):
    name: str
    legal_name: str | None = None
    document: str | None = None
    contact_email: EmailStr | None = None


class OrganizationUpdate(BaseModel):
    name: str | None = None
    legal_name: str | None = None
    document: str | None = None
    contact_email: EmailStr | None = None
    is_active: bool | None = None


class OrganizationOut(BaseModel):
    id: UUID
    name: str
    legal_name: str | None
    document: str | None
    contact_email: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class StudentProfileUpdate(BaseModel):
    phone: str | None = None
    document: str | None = None
    position: str | None = None
    department: str | None = None
    bio: str | None = None


class StudentProfileOut(BaseModel):
    id: UUID
    student_id: UUID
    phone: str | None
    document: str | None
    position: str | None
    department: str | None
    bio: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class InstructorProfileUpdate(BaseModel):
    specialties: str | None = None
    bio: str | None = None
    rating: str | None = None


class InstructorProfileOut(BaseModel):
    id: UUID
    student_id: UUID
    specialties: str | None
    bio: str | None
    rating: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class InstructorAvailabilityCreate(BaseModel):
    day_of_week: int = Field(ge=0, le=6)
    start_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(pattern=r"^\d{2}:\d{2}$")


class InstructorAvailabilityUpdate(BaseModel):
    day_of_week: int | None = Field(default=None, ge=0, le=6)
    start_time: str | None = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    end_time: str | None = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    is_active: bool | None = None


class InstructorAvailabilityOut(BaseModel):
    id: UUID
    instructor_profile_id: UUID
    day_of_week: int
    start_time: str
    end_time: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class InstructorRatingCreate(BaseModel):
    score: int
    comment: str | None = None


class InstructorRatingOut(BaseModel):
    id: UUID
    instructor_profile_id: UUID
    student_id: UUID
    score: int
    comment: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class StudentOut(BaseModel):
    id: UUID
    name: str
    email: str
    role: UserRole
    # Papeis na instituicao ativa, o principal primeiro.
    roles: list[UserRole] = []
    organization_id: UUID | None
    is_active: bool
    birth_date: date | None = None
    # Calculado de `birth_date`; sem a data, falso.
    is_adult: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


UserCreate = StudentCreate
UserUpdate = StudentUpdate
UserOut = StudentOut
