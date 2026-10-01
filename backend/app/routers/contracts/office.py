from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_secretariat
from app.models.student import Student
from app.routers.contracts.pdf import pdf_response
from app.schemas.contracts import ContractIssue, ContractOut
from app.services.contracts.documents import contract_pdf
from app.services.contracts.issuing import ContractIssueService

router = APIRouter()


@router.get("/enrollments/{enrollment_id}", response_model=list[ContractOut])
def enrollment_contracts(enrollment_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return ContractIssueService(db).list(enrollment_id)


@router.post("/enrollments/{enrollment_id}", response_model=ContractOut, status_code=201)
def issue_contract(enrollment_id: int, data: ContractIssue, db: Session = Depends(get_db), current: Student = Depends(get_current_secretariat)):
    return ContractIssueService(db).issue(enrollment_id, data, current.id)


@router.post("/{contract_id}/cancel", response_model=ContractOut)
def cancel_contract(contract_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_secretariat)):
    return ContractIssueService(db).cancel(contract_id, current.id)


@router.get("/{contract_id}/pdf")
def office_contract_pdf(contract_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    contract = ContractIssueService(db).get_or_404(contract_id)
    return pdf_response(contract, contract_pdf(contract))
