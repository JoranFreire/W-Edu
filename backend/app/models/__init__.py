import app.core.tenancy  # noqa: F401 — registra o filtro de leitura multi-tenant
import app.core.tenant_integrity  # noqa: F401 — registra as regras de gravacao multi-tenant
from app.models.student import (
    InstructorAvailability,
    InstructorProfile,
    InstructorRating,
    Organization,
    Student,
    StudentProfile,
    User,
)
from app.models.institution import Campus, Institution, InstitutionMembership
from app.models.academic import (
    AcademicUnit,
    Curriculum,
    CurriculumComponent,
    Program,
    Subject,
    SubjectEquivalence,
    SubjectPrerequisite,
)
from app.models.course import Course, CourseModule, LearningPath, LearningPathCourse, CoursePrerequisite
from app.models.course import CourseCompletionRule
from app.models.lesson import Lesson
from app.models.enrollment import Enrollment
from app.models.progress import Progress
from app.models.session import Session
from app.models.attendance import Attendance
from app.models.assignment import AssignmentSubmission
from app.models.quiz import Quiz, QuizQuestion, QuizAttempt
from app.models.certificate import Certificate
from app.models.chat import ChatConversation, ChatMessage
from app.models.notification import NotificationTemplate, NotificationEvent
from app.models.finance import BillingPlan, Subscription, Charge
from app.models.document import Document, DocumentVersion
from app.models.forum import ForumPost, ForumThread
from app.models.schedule import (
    AttendanceRecord,
    CheckinToken,
    ClassEnrollment,
    ClassOffering,
    Location,
    PracticalAssessmentRecord,
    Room,
    ScheduledMeeting,
    WaitlistEntry,
)

from app.core.database import Base as _Base
from app.core.tenant_rls import install_create_hooks as _install_rls, tenant_tables as _tenant_tables

# Politicas de RLS criadas junto com as tabelas de instituicao (create_all); em producao, via migration.
_install_rls(_tenant_tables(_Base))

__all__ = [
    "User", "Student", "Organization", "Institution", "InstitutionMembership", "Campus", "StudentProfile", "InstructorProfile", "InstructorAvailability", "InstructorRating",
    "Course", "CourseModule", "LearningPath", "LearningPathCourse", "CoursePrerequisite", "CourseCompletionRule", "Lesson", "Enrollment",
    "Progress", "Session", "Attendance", "AssignmentSubmission",
    "Quiz", "QuizQuestion", "QuizAttempt", "Certificate", "ChatConversation", "ChatMessage", "NotificationTemplate", "NotificationEvent", "BillingPlan", "Subscription", "Charge",
    "Location", "Room", "ClassOffering", "ClassEnrollment", "WaitlistEntry", "ScheduledMeeting",
    "AttendanceRecord", "CheckinToken", "PracticalAssessmentRecord", "Document", "DocumentVersion", "ForumThread", "ForumPost",
    "AcademicUnit", "Program", "Subject", "SubjectPrerequisite", "SubjectEquivalence", "Curriculum", "CurriculumComponent",
]
