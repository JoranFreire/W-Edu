from app.models.student import Student
from app.repositories.people.dossier import DossierRepository
from app.schemas.user_dossier import DossierMaterialLine, DossierMaterialRequest


def material_requests_of(repo: DossierRepository, user: Student) -> list[DossierMaterialRequest]:
    """Requisicoes ao almoxarifado feitas pela pessoa e o que foi entregue e devolvido."""
    return [
        DossierMaterialRequest(
            id=request.id, purpose=request.purpose, needed_on=request.needed_on, status=request.status,
            offering_name=request.class_offering.name if request.class_offering else None, return_due_on=request.return_due_on,
            lines=[
                DossierMaterialLine(item_name=line.item.name, unit=line.item.unit, requested=line.quantity_requested,
                                    approved=line.quantity_approved, delivered=line.quantity_delivered, returned=line.quantity_returned)
                for line in request.lines
            ],
        )
        for request in repo.material_requests_of(user.id)
    ]
