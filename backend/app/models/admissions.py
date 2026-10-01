"""Processo seletivo de cursos gratuitos: edital, inscricoes, comprovantes e convocacoes."""

from datetime import date, datetime, timezone
import enum

from sqlalchemy import JSON, Boolean, Date, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.tenancy import TenantMixin


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SelectionMethod(str, enum.Enum):
    first_come = "first_come"  # ordem de inscricao
    lottery = "lottery"        # sorteio com semente publicada
    review = "review"          # analise de perfil com nota


class AdmissionCallStatus(str, enum.Enum):
    draft = "draft"
    open = "open"          # inscricoes abertas
    closed = "closed"      # inscricoes encerradas, aguardando selecao
    selected = "selected"  # resultado publicado e convocacoes em andamento


class Schooling(str, enum.Enum):
    """Escolaridade, em ordem crescente (a comparacao usa a posicao)."""

    none = "none"
    elementary_incomplete = "elementary_incomplete"
    elementary = "elementary"
    high_school_incomplete = "high_school_incomplete"
    high_school = "high_school"
    higher_incomplete = "higher_incomplete"
    higher = "higher"


class ApplicationStatus(str, enum.Enum):
    submitted = "submitted"      # apta, aguardando selecao
    ineligible = "ineligible"    # nao atende aos requisitos
    waitlisted = "waitlisted"    # classificada, aguardando chamada
    selected = "selected"        # convocada, aguardando confirmacao
    confirmed = "confirmed"      # matriculada na turma
    declined = "declined"        # desistiu da vaga
    expired = "expired"          # nao confirmou no prazo
    withdrawn = "withdrawn"      # cancelou a inscricao antes da selecao


class SeatKind(str, enum.Enum):
    general = "general"
    reserved = "reserved"


class DocumentReview(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class AdmissionCall(TenantMixin, Base):
    """Edital de uma turma: vagas (com reserva), periodo de inscricao, requisitos e forma de selecao."""

    __tablename__ = "admission_calls"

    id: Mapped[int] = mapped_column(primary_key=True)
    class_offering_id: Mapped[int] = mapped_column(ForeignKey("class_offerings.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    method: Mapped[SelectionMethod] = mapped_column(SAEnum(SelectionMethod), default=SelectionMethod.first_come)
    seats: Mapped[int] = mapped_column(Integer)
    reserved_seats: Mapped[int] = mapped_column(Integer, default=0)
    reserved_label: Mapped[str | None] = mapped_column(String(200))   # quem concorre a reserva
    opens_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    closes_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    confirmation_days: Mapped[int] = mapped_column(Integer, default=3)
    # Requisitos verificados na inscricao (vazio: nao exigido).
    min_age: Mapped[int | None] = mapped_column(Integer)
    max_age: Mapped[int | None] = mapped_column(Integer)
    min_schooling: Mapped[Schooling | None] = mapped_column(SAEnum(Schooling))
    max_income_per_capita_cents: Mapped[int | None] = mapped_column(Integer)
    required_city: Mapped[str | None] = mapped_column(String(120))
    required_documents: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[AdmissionCallStatus] = mapped_column(SAEnum(AdmissionCallStatus), default=AdmissionCallStatus.draft)
    lottery_seed: Mapped[str | None] = mapped_column(String(64))
    selected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    class_offering: Mapped["ClassOffering"] = relationship()


class AdmissionApplication(TenantMixin, Base):
    """Inscricao no edital: respostas do questionario, analise, classificacao e convocacao."""

    __tablename__ = "admission_applications"
    __table_args__ = (UniqueConstraint("call_id", "applicant_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    call_id: Mapped[int] = mapped_column(ForeignKey("admission_calls.id", ondelete="CASCADE"), index=True)
    applicant_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    protocol: Mapped[str] = mapped_column(String(20), index=True)
    # Questionario socioeconomico.
    birth_date: Mapped[date] = mapped_column(Date)
    schooling: Mapped[Schooling] = mapped_column(SAEnum(Schooling))
    family_income_cents: Mapped[int] = mapped_column(Integer)
    household_size: Mapped[int] = mapped_column(Integer)
    city: Mapped[str] = mapped_column(String(120))
    claims_reserved: Mapped[bool] = mapped_column(Boolean, default=False)
    # Analise da secretaria: reserva conferida (vazio: nao conferida) e nota (selecao por analise).
    reserved_verified: Mapped[bool | None] = mapped_column(Boolean)
    review_score: Mapped[float | None] = mapped_column(Float)
    status: Mapped[ApplicationStatus] = mapped_column(SAEnum(ApplicationStatus), default=ApplicationStatus.submitted)
    ineligibility_reasons: Mapped[list] = mapped_column(JSON, default=list)
    rank: Mapped[int | None] = mapped_column(Integer)
    seat_kind: Mapped[SeatKind | None] = mapped_column(SAEnum(SeatKind))
    called_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    confirm_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    call: Mapped["AdmissionCall"] = relationship()
    applicant: Mapped["Student"] = relationship()
    documents: Mapped[list["ApplicationDocument"]] = relationship(
        back_populates="application", cascade="all, delete-orphan", order_by="ApplicationDocument.id"
    )


class ApplicationDocument(TenantMixin, Base):
    """Comprovante enviado pelo candidato e a conferencia da secretaria."""

    __tablename__ = "application_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("admission_applications.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(120))
    file_name: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str | None] = mapped_column(String(120))
    storage_path: Mapped[str] = mapped_column(String(500))
    review: Mapped[DocumentReview] = mapped_column(SAEnum(DocumentReview), default=DocumentReview.pending)
    review_note: Mapped[str | None] = mapped_column(Text)
    reviewed_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    application: Mapped["AdmissionApplication"] = relationship(back_populates="documents")
