from __future__ import annotations
from uuid import UUID

from app.models.schedule import AttendanceStatus, ScheduledMeeting
from app.models.social_programs import BenefitItem
from app.repositories.schedule import ScheduledMeetingRepository

PRESENT = (AttendanceStatus.present, AttendanceStatus.late)


def meeting_recipients(meeting: ScheduledMeeting, item: BenefitItem, meetings: ScheduledMeetingRepository) -> set[UUID]:
    """Quem recebe no encontro: so os presentes quando o item exige frequencia (lanche), senao todos os inscritos ativos."""
    if item.requires_attendance:
        return {record.student_id for record in meeting.attendance_records if record.status in PRESENT}
    return {enrollment.student_id for enrollment in meetings.list_active_enrollments(meeting.class_offering_id)}
