from pydantic import BaseModel, EmailStr, Field


class PublicProfile(BaseModel):
    """Conteudo da pagina publica da instituicao (tudo opcional)."""
    tagline: str | None = Field(default=None, max_length=200)
    about: str | None = Field(default=None, max_length=4000)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    whatsapp: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=300)
    website: str | None = Field(default=None, max_length=300)
    instagram: str | None = Field(default=None, max_length=120)
    enrollment_info: str | None = Field(default=None, max_length=2000)
