from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_admin_or_coordinator, get_current_secretariat
from app.models.student import Student
from app.schemas.social_programs import FundingReportOut, FundingSourceCreate, FundingSourceOut, FundingSourceUpdate
from app.services.social.funding import FundingSourceService
from app.services.social.report import FundingReportService

router = APIRouter(prefix="/funding-sources")


@router.get("", response_model=list[FundingSourceOut])
def list_funding_sources(db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    return FundingSourceService(db).list()


@router.post("", response_model=FundingSourceOut, status_code=201)
def create_funding_source(data: FundingSourceCreate, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return FundingSourceService(db).create(data)


@router.patch("/{funding_id}", response_model=FundingSourceOut)
def update_funding_source(funding_id: UUID, data: FundingSourceUpdate, db: Session = Depends(get_db), _: Student = Depends(get_current_admin_or_coordinator)):
    return FundingSourceService(db).update(funding_id, data)


@router.get("/{funding_id}/report", response_model=FundingReportOut)
def funding_report(
    funding_id: UUID, minimum_wage_cents: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat),
):
    return FundingReportService(db).report(funding_id, minimum_wage_cents)


@router.get("/{funding_id}/report.csv")
def funding_report_csv(funding_id: UUID, db: Session = Depends(get_db), _: Student = Depends(get_current_secretariat)):
    content = FundingReportService(db).csv(funding_id)
    return Response(content, media_type="text/csv; charset=utf-8", headers={"Content-Disposition": f'attachment; filename="prestacao_contas_{funding_id}.csv"'})
