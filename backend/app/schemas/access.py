from pydantic import BaseModel, Field

from app.models.student import UserRole
from app.schemas.academic_groups import PersonSummary


class PermissionOut(BaseModel):
    key: str
    module: str
    label: str
    description: str


class BuiltInProfileOut(BaseModel):
    """Perfil padrao de um papel de usuario (somente leitura)."""

    role: UserRole
    permissions: list[str]


class AccessRoleInput(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    permissions: list[str] = Field(default_factory=list)


class AccessRoleOut(BaseModel):
    id: int
    name: str
    description: str | None
    permissions: list[str]
    members: list[PersonSummary]


class AssignmentInput(BaseModel):
    user_id: int


class MemberOut(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole


class MyAccessOut(BaseModel):
    role: UserRole
    permissions: list[str]
