from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import request_institution_ref
from app.schemas.public_site import InstitutionPageOut, PublicPlanOut, SalesLeadCreate
from app.services.institution import InstitutionService
from app.services.public_site.page import InstitutionPageService
from app.services.saas.plans import SaasPlanService
from app.services.sales.leads import SalesLeadService

router = APIRouter()


@router.get("/institution-page", response_model=InstitutionPageOut | None)
def institution_page(request: Request, db: Session = Depends(get_db)):
    """Pagina da instituicao do endereco acessado (subdominio, dominio proprio, header ou `?institution=`).

    No dominio da plataforma nao ha instituicao: responde null e o site mostra a pagina de contratacao.
    """
    ref = request_institution_ref(request, db) or request.query_params.get("institution")
    if not ref:
        return None
    return InstitutionPageService(db).build(InstitutionService(db).get_public(ref))


@router.get("/plans", response_model=list[PublicPlanOut])
def public_plans(db: Session = Depends(get_db)):
    return SaasPlanService(db).public()


@router.post("/leads", status_code=status.HTTP_202_ACCEPTED)
def register_lead(data: SalesLeadCreate, db: Session = Depends(get_db)) -> dict:
    SalesLeadService(db).register(data)
    # Mesma resposta para robos (campo-armadilha), para nao ensinar a contornar o filtro.
    return {"detail": "Recebemos seu interesse; entraremos em contato."}
