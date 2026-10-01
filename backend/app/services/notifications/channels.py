from email.message import EmailMessage
import smtplib

import httpx
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.notification import NotificationEvent
from app.repositories.student import StudentRepository


class WhatsAppChannel:
    """Envio pelo W-Omni para o telefone do perfil do aluno."""

    def __init__(self, db: Session):
        self.student_repo = StudentRepository(db)

    def send(self, event: NotificationEvent) -> None:
        if not settings.WOMNI_URL:
            raise RuntimeError("WOMNI_URL não configurado")
        if not event.recipient_student_id:
            raise RuntimeError("Evento WhatsApp sem recipient_student_id")

        student = self.student_repo.get_by_id(event.recipient_student_id)
        phone = student.student_profile.phone if student and student.student_profile else None
        if not student or not phone:
            raise RuntimeError("Destinatário sem telefone cadastrado")

        headers = {}
        if settings.WOMNI_API_TOKEN:
            headers["Authorization"] = f"Bearer {settings.WOMNI_API_TOKEN}"

        base_url = settings.WOMNI_URL.rstrip("/")
        payload = {
            "channel": "whatsapp",
            "to": phone,
            "recipient": {
                "student_id": student.id,
                "name": student.name,
                "email": student.email,
            },
            "message": {
                "title": event.title,
                "body": event.body,
            },
            "metadata": {
                "source": "w-edu",
                "event_id": event.id,
                "event_type": event.event_type.value,
                "course_id": event.course_id,
                "class_offering_id": event.class_offering_id,
                "scheduled_meeting_id": event.scheduled_meeting_id,
                "payload": event.payload,
            },
        }
        with httpx.Client(timeout=settings.NOTIFICATION_DISPATCH_TIMEOUT_SECONDS) as client:
            response = client.post(f"{base_url}/messages", json=jsonable_encoder(payload), headers=headers)
            response.raise_for_status()


class EmailChannel:
    """Envio por SMTP para o e-mail do aluno."""

    def __init__(self, db: Session):
        self.student_repo = StudentRepository(db)

    def send(self, event: NotificationEvent) -> None:
        if not settings.SMTP_HOST:
            raise RuntimeError("SMTP_HOST não configurado")
        if not settings.SMTP_FROM_EMAIL:
            raise RuntimeError("SMTP_FROM_EMAIL não configurado")
        if not event.recipient_student_id:
            raise RuntimeError("Evento email sem recipient_student_id")

        student = self.student_repo.get_by_id(event.recipient_student_id)
        if not student or not student.email:
            raise RuntimeError("Destinatário sem email cadastrado")

        message = EmailMessage()
        message["Subject"] = event.title
        message["From"] = settings.SMTP_FROM_EMAIL
        message["To"] = student.email
        message.set_content(event.body)

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=settings.NOTIFICATION_DISPATCH_TIMEOUT_SECONDS) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls()
            if settings.SMTP_USERNAME:
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD or "")
            smtp.send_message(message)
