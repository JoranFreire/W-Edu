from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.notification import NotificationChannel, NotificationTemplate
from app.repositories.notification import NotificationTemplateRepository
from app.schemas.notification import NotificationTemplateCreate, NotificationTemplateUpdate
from app.services.notifications.defaults import DEFAULT_TEMPLATES


class NotificationTemplateService:
    """Templates de notificacao da instituicao, incluindo os padroes criados sob demanda."""

    def __init__(self, db: Session):
        self.repo = NotificationTemplateRepository(db)

    def list(self) -> list[NotificationTemplate]:
        self.ensure_defaults()
        return self.repo.list_all()

    def create(self, data: NotificationTemplateCreate) -> NotificationTemplate:
        if self.repo.get_by_key_and_channel(data.key, data.channel):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Template já existe")
        return self.repo.create(NotificationTemplate(**data.model_dump()))

    def update(self, key: str, channel: NotificationChannel, data: NotificationTemplateUpdate) -> NotificationTemplate:
        template = self.repo.get_by_key_and_channel(key, channel)
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template não encontrado")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(template, field, value)
        return self.repo.update(template)

    def get_for(self, key: str, channel: NotificationChannel) -> NotificationTemplate:
        """Template do canal; sem ele, cai no template interno do mesmo evento."""
        self.ensure_defaults()
        template = self.repo.get_by_key_and_channel(key, channel)
        if not template and channel != NotificationChannel.internal:
            template = self.repo.get_by_key_and_channel(key, NotificationChannel.internal)
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template não encontrado")
        return template

    def ensure_defaults(self) -> None:
        existing = {(template.key, template.channel) for template in self.repo.list_all()}
        for (event_type, channel), (title_template, body_template) in DEFAULT_TEMPLATES.items():
            if (event_type.value, channel) in existing:
                continue
            self.repo.create_if_missing(NotificationTemplate(
                key=event_type.value,
                channel=channel,
                title_template=title_template,
                body_template=body_template,
            ))


def render_template(template: str, payload: dict) -> str:
    """Preenche `{campo}` com o payload; campos ausentes viram texto vazio."""
    class SafeDict(dict):
        def __missing__(self, key):
            return ""

    return template.format_map(SafeDict(payload))
