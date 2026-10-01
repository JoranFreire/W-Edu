"""A matricula por disciplina so acontece com a janela aberta."""

from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.models.course_registration import RegistrationWindow
from app.services.registration.rules import window_is_open


def ensure_window_open(window: RegistrationWindow) -> None:
    if not window_is_open(window.opens_at, window.closes_at, datetime.now(timezone.utc)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A janela de matrícula está fechada")
