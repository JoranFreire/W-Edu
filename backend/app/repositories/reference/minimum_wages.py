from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import func

from app.models.reference_values import MinimumWageValue


class MinimumWageRepository:
    """Serie local do salario minimo (tabela global: nao passa pelo filtro de instituicao)."""

    def __init__(self, db):
        self.db = db

    def valid_on(self, day: date) -> MinimumWageValue | None:
        return (
            self.db.query(MinimumWageValue)
            .filter(MinimumWageValue.valid_from <= day)
            .order_by(MinimumWageValue.valid_from.desc())
            .first()
        )

    def last_sync(self) -> datetime | None:
        return self.db.query(func.max(MinimumWageValue.synced_at)).filter(MinimumWageValue.source == "bcb").scalar()

    def upsert(self, points: list[tuple[date, int]], synced_at: datetime) -> None:
        """Grava so as mudancas de valor (a serie e mensal); valor confirmado pela API passa a ser `bcb`."""
        rows = sorted(self.db.query(MinimumWageValue).all(), key=lambda row: row.valid_from)
        for valid_from, cents in sorted(points):
            current = next((row for row in reversed(rows) if row.valid_from <= valid_from), None)
            if current is not None and current.cents == cents:
                current.source, current.synced_at = "bcb", synced_at
                continue
            row = MinimumWageValue(valid_from=valid_from, cents=cents, source="bcb", synced_at=synced_at)
            self.db.add(row)
            rows = sorted([*rows, row], key=lambda item: item.valid_from)
        self.db.commit()
