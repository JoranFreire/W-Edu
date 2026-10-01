from datetime import datetime, timezone

from app.models.finance import ChargeStatus
from app.models.student import Student
from app.repositories.people.dossier import DossierRepository
from app.schemas.user_dossier import DossierCharge, DossierFinance

RECENT_CHARGES = 36


def _as_utc(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def finance_of(repo: DossierRepository, user: Student) -> DossierFinance:
    """Resumo das cobrancas em aberto e o extrato recente, como aluno ou como responsavel financeiro."""
    charges = repo.charges_of(user.id)
    now = datetime.now(timezone.utc)
    open_charges = [charge for charge in charges if charge.status == ChargeStatus.pending]
    due_dates = sorted(_as_utc(charge.due_at) for charge in open_charges if charge.due_at)
    return DossierFinance(
        open_count=len(open_charges),
        overdue_count=sum(1 for due in due_dates if due < now),
        open_cents=sum(charge.amount_cents for charge in open_charges),
        next_due_at=next((due for due in due_dates if due >= now), None),
        charges=[
            DossierCharge(id=charge.id, description=charge.description, amount_cents=charge.amount_cents, status=charge.status,
                          due_at=charge.due_at, paid_at=charge.paid_at, installment_number=charge.installment_number,
                          as_payer=charge.student_id != user.id)
            for charge in charges[:RECENT_CHARGES]
        ],
    )
