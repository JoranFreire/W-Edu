from uuid import UUID

from datetime import date, datetime, timezone
import enum
from sqlalchemy import ForeignKey, String, Boolean, Date, DateTime, Enum as SAEnum, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.age import is_adult
from app.core.ids import new_id
from app.core.database import Base
from app.core.tenancy import TenantMixin


class UserRole(str, enum.Enum):
    student = "student"
    instructor = "instructor"
    coordinator = "coordinator"
    company_manager = "company_manager"
    admin = "admin"
    super_admin = "super_admin"
    institution_admin = "institution_admin"
    secretary = "secretary"
    guardian = "guardian"


# `admin` e o papel legado equivalente a `institution_admin`; `super_admin` administra a plataforma.
ADMIN_ROLES = frozenset({UserRole.admin, UserRole.institution_admin, UserRole.super_admin})


class Organization(TenantMixin, Base):
    __tablename__ = "organizations"
    __table_args__ = (UniqueConstraint("institution_id", "name"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(200), index=True)
    legal_name: Mapped[str | None] = mapped_column(String(200))
    document: Mapped[str | None] = mapped_column(String(50), index=True)
    contact_email: Mapped[str | None] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    users: Mapped[list["Student"]] = relationship(back_populates="organization")
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="organization")
    charges: Mapped[list["Charge"]] = relationship(back_populates="organization")


class Student(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.student)
    organization_id: Mapped[UUID | None] = mapped_column(ForeignKey("organizations.id"), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Maioridade decide o que o reconhecimento facial (Persona) pode fazer com a pessoa.
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    organization: Mapped["Organization | None"] = relationship(back_populates="users")
    student_profile: Mapped["StudentProfile | None"] = relationship(back_populates="student", uselist=False, cascade="all, delete-orphan")
    instructor_profile: Mapped["InstructorProfile | None"] = relationship(back_populates="student", uselist=False, cascade="all, delete-orphan")
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="student")
    progress: Mapped[list["Progress"]] = relationship(back_populates="student")
    sessions: Mapped[list["Session"]] = relationship(back_populates="student")
    attendance: Mapped[list["Attendance"]] = relationship(back_populates="student")
    quiz_attempts: Mapped[list["QuizAttempt"]] = relationship(back_populates="student")
    certificates: Mapped[list["Certificate"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
        foreign_keys="Certificate.student_id",
    )
    issued_certificates: Mapped[list["Certificate"]] = relationship(
        back_populates="issued_by",
        foreign_keys="Certificate.issued_by_id",
    )
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="student")
    charges: Mapped[list["Charge"]] = relationship(back_populates="student", foreign_keys="Charge.student_id")

    @property
    def roles(self) -> list[UserRole]:
        """Papeis na instituicao ativa, o principal primeiro (lidos sob demanda; ver app/policies/roles.py)."""
        from app.policies.roles import roles_of  # import local: a policy depende deste model

        return sorted(roles_of(self), key=lambda role: (role != self.role, role.value))

    @property
    def is_adult(self) -> bool:
        return is_adult(self.birth_date)


User = Student



class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    student_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(50))
    document: Mapped[str | None] = mapped_column(String(50), index=True)
    position: Mapped[str | None] = mapped_column(String(120))
    department: Mapped[str | None] = mapped_column(String(120))
    bio: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    student: Mapped["Student"] = relationship(back_populates="student_profile")


class InstructorProfile(Base):
    __tablename__ = "instructor_profiles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    student_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    specialties: Mapped[str | None] = mapped_column(Text)
    bio: Mapped[str | None] = mapped_column(Text)
    rating: Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    student: Mapped["Student"] = relationship(back_populates="instructor_profile")
    availability_slots: Mapped[list["InstructorAvailability"]] = relationship(back_populates="instructor_profile", cascade="all, delete-orphan")
    ratings: Mapped[list["InstructorRating"]] = relationship(back_populates="instructor_profile", cascade="all, delete-orphan")


class InstructorAvailability(Base):
    __tablename__ = "instructor_availability"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    instructor_profile_id: Mapped[UUID] = mapped_column(ForeignKey("instructor_profiles.id"), index=True)
    day_of_week: Mapped[int] = mapped_column()
    start_time: Mapped[str] = mapped_column(String(5))
    end_time: Mapped[str] = mapped_column(String(5))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    instructor_profile: Mapped["InstructorProfile"] = relationship(back_populates="availability_slots")


class InstructorRating(Base):
    __tablename__ = "instructor_ratings"
    __table_args__ = ()

    id: Mapped[UUID] = mapped_column(primary_key=True, default=new_id)
    instructor_profile_id: Mapped[UUID] = mapped_column(ForeignKey("instructor_profiles.id"), index=True)
    student_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    score: Mapped[int] = mapped_column()
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    instructor_profile: Mapped["InstructorProfile"] = relationship(back_populates="ratings")
    student: Mapped["Student"] = relationship()
