from __future__ import annotations

import csv
from datetime import date
import io

from sqlalchemy.orm import Session

from app.models.admissions import SeatKind
from app.repositories.social import BenefitDeliveryRepository, BenefitStockRepository, FundingSourceRepository, SocialIndicatorRepository
from app.schemas.social_programs import BenefitUsage, FundingReportOut, FundingSourceOut, OfferingIndicators, ProfileOut
from app.services.social.funding import FundingSourceService
from app.services.social.rules import indicators, profile_counts

DEFAULT_MINIMUM_WAGE_CENTS = 151800


class FundingReportService:
    """Prestacao de contas do financiador: indicadores por turma, perfil do publico, beneficios e saldo."""

    def __init__(self, db: Session):
        self.funding = FundingSourceService(db)
        self.repo = FundingSourceRepository(db)
        self.indicators = SocialIndicatorRepository(db)
        self.deliveries = BenefitDeliveryRepository(db)
        self.stock = BenefitStockRepository(db)

    def report(self, funding_id: int, minimum_wage_cents: int = DEFAULT_MINIMUM_WAGE_CENTS) -> FundingReportOut:
        funding = self.funding.get_or_404(funding_id)
        offerings = self.repo.funded_offerings(funding.id)
        ids = [offering.id for offering in offerings]
        applications = self.indicators.applications(ids)
        enrollments = self.indicators.enrollments(ids)
        rows = [
            OfferingIndicators(
                class_offering_id=offering.id, name=offering.name, applications=applications.get(offering.id, 0),
                **indicators([e for e in enrollments if e.class_offering_id == offering.id]),
            )
            for offering in offerings
        ]
        totals = OfferingIndicators(class_offering_id=None, name="Total", applications=sum(applications.values()), **indicators(enrollments))
        answers = [(a.birth_date, a.schooling, a.family_income_cents, a.household_size, a.seat_kind == SeatKind.reserved)
                   for a in self.indicators.confirmed_answers(ids)]
        usage = [BenefitUsage(item_name=name, unit=unit, quantity=quantity, cost_cents=cost) for name, unit, quantity, cost in self.deliveries.usage(ids)]
        spent = sum(item.cost_cents for item in usage)
        return FundingReportOut(
            funding=FundingSourceOut.model_validate(funding), offerings=rows, totals=totals,
            profile=ProfileOut(**profile_counts(answers, date.today(), minimum_wage_cents)), benefits=usage,
            stock_received_cents=self.stock.received_cost(funding.id), benefits_cost_cents=spent,
            budget_balance_cents=funding.amount_cents - spent if funding.amount_cents is not None else None,
        )

    def csv(self, funding_id: int, minimum_wage_cents: int = DEFAULT_MINIMUM_WAGE_CENTS) -> str:
        """Planilha (separador ;) com indicadores por turma e beneficios entregues."""
        report = self.report(funding_id, minimum_wage_cents)
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter=";")
        writer.writerow(["Financiador", report.funding.name, report.funding.agreement_number or ""])
        writer.writerow([])
        writer.writerow(["Turma", "Inscritos", "Matriculados", "Ativos", "Concluintes", "Desligados", "Desistentes", "Evasão (%)"])
        for row in [*report.offerings, report.totals]:
            writer.writerow([row.name, row.applications, row.enrolled, row.active, row.completed, row.dismissed, row.dropped, f"{row.evasion_rate:.1f}".replace(".", ",")])
        writer.writerow([])
        writer.writerow(["Benefício", "Unidade", "Quantidade", "Custo (R$)"])
        for item in report.benefits:
            writer.writerow([item.item_name, item.unit, item.quantity, f"{item.cost_cents / 100:.2f}".replace(".", ",")])
        return buffer.getvalue()
