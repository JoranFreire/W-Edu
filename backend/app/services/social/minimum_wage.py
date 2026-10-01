"""Salario minimo de referencia: tabela local espelhando a serie 1619 do SGS do Banco Central.

A tabela ja nasce com os valores conhecidos (migration) e e atualizada pela API quando a ultima
sincronizacao passa de MINIMUM_WAGE_CACHE_HOURS; com a API fora do ar, vale o que esta gravado.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import logging

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.reference import MinimumWageRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MinimumWage:
    cents: int
    source: str          # "bcb" (sincronizado), "seed" (carga inicial), "informed" (parametro) ou "fallback"
    valid_from: date | None


def parse_points(payload: list[dict]) -> list[tuple[date, int]]:
    """Pontos (inicio, centavos) da resposta do SGS (`data` em DD/MM/AAAA, `valor` em reais)."""
    points = []
    for point in payload:
        day, month, year = (int(part) for part in point["data"].split("/"))
        points.append((date(year, month, day), int(Decimal(point["valor"]) * 100)))
    return points


# Ultima tentativa de sincronizar neste processo (evita consultar a API a cada relatorio).
_last_attempt: datetime | None = None


class MinimumWageProvider:
    def __init__(self, db: Session):
        self.repo = MinimumWageRepository(db)

    def current(self, on: date | None = None) -> MinimumWage:
        on = on or date.today()
        self.refresh_if_stale()
        row = self.repo.valid_on(on)
        if row:
            return MinimumWage(cents=row.cents, source=row.source, valid_from=row.valid_from)
        return MinimumWage(cents=settings.MINIMUM_WAGE_FALLBACK_CENTS, source="fallback", valid_from=None)

    def refresh_if_stale(self) -> None:
        global _last_attempt
        if not settings.MINIMUM_WAGE_API_URL:
            return
        now, ttl = datetime.now(timezone.utc), timedelta(hours=settings.MINIMUM_WAGE_CACHE_HOURS)
        last_sync = self.repo.last_sync()
        if last_sync is not None and last_sync.tzinfo is None:
            last_sync = last_sync.replace(tzinfo=timezone.utc)
        if any(moment is not None and now - moment < ttl for moment in (last_sync, _last_attempt)):
            return
        _last_attempt = now
        self.refresh(now)

    def refresh(self, now: datetime) -> bool:
        """Busca os ultimos anos da serie e grava as mudancas; falha so registra aviso."""
        today = now.date()
        params = {"formato": "json", "dataInicial": date(today.year - 3, 1, 1).strftime("%d/%m/%Y"), "dataFinal": date(today.year, 12, 31).strftime("%d/%m/%Y")}
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(settings.MINIMUM_WAGE_API_URL, params=params)
                response.raise_for_status()
                points = parse_points(response.json())
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            logger.warning("Salario minimo do Banco Central indisponivel; mantida a tabela local: %s", exc)
            return False
        self.repo.upsert(points, now)
        return True
