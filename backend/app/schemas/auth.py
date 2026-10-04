from pydantic import BaseModel, EmailStr

from app.schemas.institution import InstitutionSummary


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    institution: str | None = None


class FacialLoginRequest(BaseModel):
    # Assertion assinado pelo Persona depois de conferir o rosto (app/core/facial_assertion.py).
    assertion: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    institution: InstitutionSummary | None = None
