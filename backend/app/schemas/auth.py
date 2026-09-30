from pydantic import BaseModel, EmailStr

from app.schemas.institution import InstitutionSummary


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    institution: str | None = None


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    institution: InstitutionSummary | None = None
