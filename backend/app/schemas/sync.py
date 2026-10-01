from pydantic import BaseModel


class DataVersionsOut(BaseModel):
    """Versao por area (notifications, agenda, report_card, dependents)."""

    versions: dict[str, int]
