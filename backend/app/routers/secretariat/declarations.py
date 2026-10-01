from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin_or_coordinator, get_current_secretariat, get_current_student
from app.models.secretariat import AcademicDeclaration
from app.models.student import Student
from app.schemas.secretariat import DeclarationCreate, DeclarationOut, DeclarationRevoke, DeclarationValidationOut
from app.services.secretariat.declarations import DeclarationService

router = APIRouter()


def _pdf_response(service: DeclarationService, declaration: AcademicDeclaration) -> Response:
    filename = f"declaracao_{declaration.kind.value}_{declaration.validation_code}.pdf"
    return Response(service.pdf(declaration), media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.get("/enrollments/{enrollment_id}/declarations", response_model=list[DeclarationOut])
def list_declarations(enrollment_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return DeclarationService(db).list(enrollment_id)


@router.post("/enrollments/{enrollment_id}/declarations", response_model=DeclarationOut, status_code=201)
def issue_declaration(
    enrollment_id: UUID,
    data: DeclarationCreate,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_secretariat),
):
    return DeclarationService(db).issue(enrollment_id, data, current.id)


@router.get("/declarations/{declaration_id}/pdf")
def declaration_pdf(declaration_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    service = DeclarationService(db)
    return _pdf_response(service, service.get_or_404(declaration_id))


@router.post("/declarations/{declaration_id}/revoke", response_model=DeclarationOut)
def revoke_declaration(
    declaration_id: UUID,
    data: DeclarationRevoke,
    db: Session = Depends(get_db),
    _: Student = Depends(get_current_admin_or_coordinator),
):
    return DeclarationService(db).revoke(declaration_id, data.reason)


@router.get("/declarations/validate/{code}", response_model=DeclarationValidationOut)
def validate_declaration(code: str, db: Session = Depends(get_db)):
    """Publica: qualquer pessoa confere a autenticidade pelo codigo impresso."""
    return DeclarationService(db).validate(code)


@router.get("/my/declarations", response_model=list[DeclarationOut])
def my_declarations(db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return DeclarationService(db).list_for_student(current)


@router.get("/my/declarations/{declaration_id}/pdf")
def my_declaration_pdf(declaration_id: UUID, db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    service = DeclarationService(db)
    return _pdf_response(service, service.get_for_student(declaration_id, current))
