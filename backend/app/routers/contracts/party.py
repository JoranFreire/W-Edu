from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_student
from app.models.student import Student
from app.routers.contracts.pdf import pdf_response
from app.schemas.contracts import ContractOut
from app.services.contracts.signing import ContractPartyService

router = APIRouter(prefix="/my")


@router.get("", response_model=list[ContractOut])
def my_contracts(db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return ContractPartyService(db).list_mine(current)


@router.get("/{contract_id}/pdf")
def my_contract_pdf(contract_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    contract, content = ContractPartyService(db).pdf_for(current, contract_id)
    return pdf_response(contract, content)


@router.post("/{contract_id}/accept", response_model=ContractOut)
def accept_contract(contract_id: int, db: Session = Depends(get_db), current: Student = Depends(get_current_student)):
    return ContractPartyService(db).accept(current, contract_id)
