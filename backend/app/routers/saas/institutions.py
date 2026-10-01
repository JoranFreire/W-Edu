from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_super_admin
from app.models.student import Student
from app.schemas.saas import InstitutionPlanOut, InvoiceGenerate, PlatformInvoiceOut, SubscriptionInput, SubscriptionOut
from app.services.saas.invoices import PlatformInvoiceService
from app.services.saas.overview import InstitutionPlanOverview
from app.services.saas.subscriptions import InstitutionSubscriptionService

router = APIRouter()


@router.get("/institutions/{institution_id}", response_model=InstitutionPlanOut)
def institution_plan(institution_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_super_admin)):
    return InstitutionPlanOverview(db).for_institution(institution_id)


@router.put("/institutions/{institution_id}/subscription", response_model=SubscriptionOut)
def set_subscription(institution_id: int, data: SubscriptionInput, db: Session = Depends(get_db), _: Student = Depends(get_current_super_admin)):
    return InstitutionSubscriptionService(db).set(institution_id, data)


@router.post("/institutions/{institution_id}/invoices", response_model=PlatformInvoiceOut, status_code=201)
def generate_invoice(institution_id: int, data: InvoiceGenerate, db: Session = Depends(get_db), _: Student = Depends(get_current_super_admin)):
    return PlatformInvoiceService(db).generate(institution_id, data.period_start)


@router.post("/invoices/{invoice_id}/paid", response_model=PlatformInvoiceOut)
def mark_invoice_paid(invoice_id: int, db: Session = Depends(get_db), _: Student = Depends(get_current_super_admin)):
    return PlatformInvoiceService(db).mark_paid(invoice_id)
