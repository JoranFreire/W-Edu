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
from app.models.institution import Campus, Institution, InstitutionMembership, MemberRole
from app.models.academic import (
    AcademicUnit,
    Curriculum,
    CurriculumComponent,
    Program,
    Subject,
    SubjectEquivalence,
    SubjectPrerequisite,
)
from app.models.academic_calendar import AcademicTerm, CalendarEvent, GradingPeriod
from app.models.academic_groups import ClassGroup, ClassGroupMember, ProgramEnrollment
from app.models.assessment import AssessmentItem, GradeEntry, GradingScheme, OfferingPeriodClosure, PeriodResult
from app.models.class_diary import ClassDiaryEntry, DiaryAttendance
from app.models.course_registration import OfferingTimeSlot, RegistrationWindow
from app.models.completion import ComplementaryActivity, FinalProject, Internship, InternshipLog
from app.models.tuition import StudentDiscount, TuitionPlan
from app.models.contracts import ContractTemplate, EnrollmentContract
from app.models.saas import InstitutionSubscription, PlatformInvoice, SaasPlan
from app.models.sales import LeadStatus, SalesLead
from app.models.admissions import AdmissionApplication, AdmissionCall, ApplicationDocument
from app.models.social_programs import BenefitDelivery, BenefitItem, BenefitStockEntry, BenefitVoucher, FundingSource
from app.models.reference_values import MinimumWageValue
from app.models.access import AccessRole, AccessRoleAssignment
from app.models.warehouse import MaterialRequest, MaterialRequestLine, MaterialReturn, WarehouseEntry, WarehouseItem
from app.models.guardians import StudentGuardian
from app.models.data_version import DataVersion
from app.models.school_life import AgendaItem, StudentOccurrence
from app.models.secretariat import AcademicDeclaration, CreditTransfer, ProgramEnrollmentEvent, TermRegistration
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
from app.models.facial_login import FacialLoginAssertion
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

import app.services.sync.areas  # noqa: E402,F401 — registra as tabelas de cada area do cache dos apps

# Politicas de RLS criadas junto com as tabelas de instituicao (create_all); em producao, via migration.
_install_rls(_tenant_tables(_Base))

__all__ = [
    "User", "Student", "Organization", "Institution", "InstitutionMembership", "MemberRole", "Campus", "StudentProfile", "InstructorProfile", "InstructorAvailability", "InstructorRating",
    "Course", "CourseModule", "LearningPath", "LearningPathCourse", "CoursePrerequisite", "CourseCompletionRule", "Lesson", "Enrollment",
    "Progress", "Session", "Attendance", "AssignmentSubmission",
    "Quiz", "QuizQuestion", "QuizAttempt", "Certificate", "ChatConversation", "ChatMessage", "NotificationTemplate", "NotificationEvent", "BillingPlan", "Subscription", "Charge",
    "Location", "Room", "ClassOffering", "ClassEnrollment", "WaitlistEntry", "ScheduledMeeting",
    "AttendanceRecord", "CheckinToken", "PracticalAssessmentRecord", "Document", "DocumentVersion", "ForumThread", "ForumPost",
    "AcademicUnit", "Program", "Subject", "SubjectPrerequisite", "SubjectEquivalence", "Curriculum", "CurriculumComponent",
    "AcademicTerm", "GradingPeriod", "CalendarEvent", "ProgramEnrollment", "ClassGroup", "ClassGroupMember",
    "GradingScheme", "AssessmentItem", "GradeEntry", "ClassDiaryEntry", "DiaryAttendance",
    "OfferingPeriodClosure", "PeriodResult", "ProgramEnrollmentEvent", "TermRegistration", "CreditTransfer", "AcademicDeclaration", "StudentGuardian", "DataVersion", "StudentOccurrence", "AgendaItem",
    "RegistrationWindow", "OfferingTimeSlot", "ComplementaryActivity", "Internship", "InternshipLog", "FinalProject",
    "TuitionPlan", "StudentDiscount", "ContractTemplate", "EnrollmentContract",
    "SaasPlan", "SalesLead", "LeadStatus", "InstitutionSubscription", "PlatformInvoice",
    "AdmissionCall", "AdmissionApplication", "ApplicationDocument",
    "FundingSource", "BenefitItem", "BenefitStockEntry", "BenefitDelivery", "BenefitVoucher", "MinimumWageValue",
    "AccessRole", "AccessRoleAssignment",
    "WarehouseItem", "WarehouseEntry", "MaterialRequest", "MaterialRequestLine", "MaterialReturn",
]
