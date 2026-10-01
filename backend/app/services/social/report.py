from __future__ import annotations

import csv
from datetime import date
import io

from sqlalchemy.orm import Session

from app.models.admissions import SeatKind
from app.repositories.warehouse import MaterialRequestRepository
from app.repositories.social import BenefitDeliveryRepository, BenefitStockRepository, FundingSourceRepository, SocialIndicatorRepository
from app.schemas.social_programs import BenefitUsage, FundingReportOut, FundingSourceOut, OfferingIndicators, ProfileOut
from app.services.social.funding import FundingSourceService
from app.services.social.minimum_wage import MinimumWage, MinimumWageProvider
from app.services.social.rules import indicators, profile_counts
from app.services.warehouse.reports import consumption



class FundingReportService:
    """Prestacao de contas do financiador: indicadores por turma, perfil do publico, beneficios e saldo."""

    def __init__(self, db: Session):
        self.funding = FundingSourceService(db)
        self.repo = FundingSourceRepository(db)
        self.indicators = SocialIndicatorRepository(db)
        self.deliveries = BenefitDeliveryRepository(db)
        self.stock = BenefitStockRepository(db)
        self.minimum_wage = MinimumWageProvider(db)
        self.material_requests = MaterialRequestRepository(db)

    def report(self, funding_id: int, minimum_wage_cents: int | None = None) -> FundingReportOut:
        """Faixas de renda pelo salario minimo informado ou, sem ele, o do Banco Central."""
        funding = self.funding.get_or_404(funding_id)
        wage = MinimumWage(minimum_wage_cents, "informed", None) if minimum_wage_cents else self.minimum_wage.current()
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
        materials = consumption(self.material_requests.delivered_for_offerings(ids)).by_item
        spent = sum(item.cost_cents for item in usage) + sum(row.cost_cents for row in materials)
        return FundingReportOut(
            funding=FundingSourceOut.model_validate(funding), offerings=rows, totals=totals,
            profile=ProfileOut(**profile_counts(answers, date.today(), wage.cents)), benefits=usage,
            minimum_wage_cents=wage.cents, minimum_wage_source=wage.source,
            stock_received_cents=self.stock.received_cost(funding.id), benefits_cost_cents=sum(item.cost_cents for item in usage),
            materials=[BenefitUsage(item_name=row.label, unit="", quantity=row.quantity, cost_cents=row.cost_cents) for row in materials],
            materials_cost_cents=sum(row.cost_cents for row in materials),
            budget_balance_cents=funding.amount_cents - spent if funding.amount_cents is not None else None,
        )

    def csv(self, funding_id: int, minimum_wage_cents: int | None = None) -> str:
        """Planilha (separador ;) com indicadores por turma e beneficios entregues."""
        report = self.report(funding_id, minimum_wage_cents)
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter=";")
        writer.writerow(["Financiador", report.funding.name, report.funding.agreement_number or ""])
        writer.writerow(["Salário mínimo de referência (R$)", f"{report.minimum_wage_cents / 100:.2f}".replace(".", ","), report.minimum_wage_source])
        writer.writerow([])
        writer.writerow(["Turma", "Inscritos", "Matriculados", "Ativos", "Concluintes", "Desligados", "Desistentes", "Evasão (%)"])
        for row in [*report.offerings, report.totals]:
            writer.writerow([row.name, row.applications, row.enrolled, row.active, row.completed, row.dismissed, row.dropped, f"{row.evasion_rate:.1f}".replace(".", ",")])
        writer.writerow([])
        writer.writerow(["Benefício", "Unidade", "Quantidade", "Custo (R$)"])
        for item in report.benefits:
            writer.writerow([item.item_name, item.unit, item.quantity, f"{item.cost_cents / 100:.2f}".replace(".", ",")])
        writer.writerow([])
        writer.writerow(["Material do almoxarifado", "Quantidade", "Custo (R$)"])
        for item in report.materials:
            writer.writerow([item.item_name, item.quantity, f"{item.cost_cents / 100:.2f}".replace(".", ",")])
        return buffer.getvalue()
