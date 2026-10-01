from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.contracts import ContractValidationOut
from app.services.contracts.validation import ContractValidationService

router = APIRouter()


@router.get("/validate/{code}", response_model=ContractValidationOut)
def validate_contract(code: str, db: Session = Depends(get_db)):
    return ContractValidationService(db).validate(code)
