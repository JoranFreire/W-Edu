"""Tabelas que alimentam cada tela do app: gravar em qualquer uma sobe a versao da area."""

from app.core.change_tracking import track
from app.models.academic_calendar import GradingPeriod
from app.models.academic_groups import ClassGroup, ClassGroupMember
from app.models.assessment import GradingScheme, PeriodResult
from app.models.guardians import StudentGuardian
from app.models.notification import NotificationEvent
from app.models.schedule import ClassEnrollment, ClassOffering, ScheduledMeeting
from app.models.social_programs import BenefitItem, BenefitVoucher
from app.models.school_life import AgendaItem
from app.models.student import Student
from app.models.warehouse import MaterialRequest, MaterialRequestLine, MaterialReturn, WarehouseItem

NOTIFICATIONS = "notifications"
AGENDA = "agenda"
REPORT_CARD = "report_card"
DEPENDENTS = "dependents"
BENEFITS = "benefits"
MATERIALS = "materials"
# Turmas e encontros de quem ministra: a chamada facial escolhe o encontro mesmo sem rede.
TEACHING = "teaching"

AREAS = (NOTIFICATIONS, AGENDA, REPORT_CARD, DEPENDENTS, BENEFITS, MATERIALS, TEACHING)

track(NotificationEvent, NOTIFICATIONS)
track(AgendaItem, AGENDA)
track(ClassGroup, AGENDA)
track(ClassGroupMember, AGENDA)
track(ClassOffering, AGENDA, REPORT_CARD, BENEFITS, TEACHING)
track(ClassEnrollment, REPORT_CARD)
track(PeriodResult, REPORT_CARD)
track(GradingPeriod, REPORT_CARD)
track(GradingScheme, REPORT_CARD)
track(StudentGuardian, DEPENDENTS)
# Conta global: so nome e e-mail aparecem na lista de dependentes (login e outras colunas nao contam).
track(Student, DEPENDENTS, columns=("name", "email"))
track(BenefitVoucher, BENEFITS)
track(BenefitItem, BENEFITS, columns=("name", "unit", "kind"))
track(MaterialRequest, MATERIALS)
track(MaterialRequestLine, MATERIALS)
track(MaterialReturn, MATERIALS)
track(WarehouseItem, MATERIALS, columns=("name", "unit", "kind"))
track(ScheduledMeeting, TEACHING)
