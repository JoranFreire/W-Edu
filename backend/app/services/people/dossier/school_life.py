from sqlalchemy.orm import Session

from app.models.student import Student
from app.repositories.people.dossier import DossierRepository
from app.repositories.school_life.occurrences import OccurrenceRepository
from app.schemas.user_dossier import DossierBenefit, DossierOccurrence, DossierOccurrences

MAX_OCCURRENCES = 100


def occurrences_of(db: Session, user: Student) -> DossierOccurrences:
    occurrences = sorted(OccurrenceRepository(db).list_by_student(user.id), key=lambda item: item.occurred_on, reverse=True)
    return DossierOccurrences(
        total=len(occurrences),
        recent=[DossierOccurrence(id=item.id, kind=item.kind, severity=item.severity, description=item.description,
                                  occurred_on=item.occurred_on) for item in occurrences[:MAX_OCCURRENCES]],
    )


def benefits_of(repo: DossierRepository, user: Student) -> list[DossierBenefit]:
    """Beneficios recebidos pelo aluno (lanche, kit, transporte) nas turmas financiadas."""
    return [
        DossierBenefit(id=delivery.id, item_name=delivery.item.name, unit=delivery.item.unit, quantity=delivery.quantity,
                       delivered_on=delivery.delivered_on, offering_name=offering_name)
        for delivery, offering_name in repo.benefits_of(user.id)
    ]
