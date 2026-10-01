"""Salario minimo de referencia: serie 1619 do SGS do Banco Central, com cache e valor de reserva."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MinimumWage:
    cents: int
    source: str          # "bcb" (Banco Central), "informed" (parametro) ou "fallback" (configuracao)
    valid_from: date | None


def parse_sgs(payload: list[dict], on: date) -> MinimumWage | None:
    """Ultimo valor vigente ate `on` (a serie traz meses futuros ja definidos em lei)."""
    points = []
    for point in payload:
        day, month, year = (int(part) for part in point["data"].split("/"))
        start = date(year, month, day)
        if start <= on:
            points.append((start, int(Decimal(point["valor"]) * 100)))
    if not points:
        return None
    start, cents = max(points)
    return MinimumWage(cents=cents, source="bcb", valid_from=start)


# Cache por processo: o valor muda uma vez por ano.
_cache: dict[tuple[int, int], tuple[datetime, MinimumWage]] = {}


class MinimumWageProvider:
    def current(self, on: date | None = None) -> MinimumWage:
        on = on or date.today()
        fallback = MinimumWage(cents=settings.MINIMUM_WAGE_FALLBACK_CENTS, source="fallback", valid_from=None)
        if not settings.MINIMUM_WAGE_API_URL:
            return fallback
        key, now = (on.year, on.month), datetime.now(timezone.utc)
        cached = _cache.get(key)
        if cached and now - cached[0] < timedelta(hours=settings.MINIMUM_WAGE_CACHE_HOURS):
            return cached[1]
        value = self._fetch(on) or fallback
        if value.source == "bcb":
            _cache[key] = (now, value)
        return value

    @staticmethod
    def _fetch(on: date) -> MinimumWage | None:
        params = {"formato": "json", "dataInicial": (on - timedelta(days=400)).strftime("%d/%m/%Y"), "dataFinal": on.strftime("%d/%m/%Y")}
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(settings.MINIMUM_WAGE_API_URL, params=params)
                response.raise_for_status()
                return parse_sgs(response.json(), on)
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            logger.warning("Salario minimo do Banco Central indisponivel: %s", exc)
            return None
