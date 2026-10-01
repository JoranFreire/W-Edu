from sqlalchemy.orm import Session

from app.core.tenancy import bind_institution
from app.models.academic import Program, ProgramStatus
from app.models.course import Course
from app.models.institution import Campus, Institution
from app.schemas.institution import InstitutionSummary
from app.schemas.public_site import InstitutionPageOut, PublicCampus, PublicCourse, PublicProfile, PublicProgram
from app.services.admissions.public import PublicAdmissionsService

MAX_COURSES = 12


class InstitutionPageService:
    """Pagina publica da instituicao: apresentacao, o que oferece e as inscricoes abertas."""

    def __init__(self, db: Session):
        self.db = db

    def build(self, institution: Institution) -> InstitutionPageOut:
        # Pagina publica: a sessao passa a ler so os dados desta instituicao (filtro do tenant e RLS).
        bind_institution(self.db, institution.id)
        programs = (
            self.db.query(Program).filter(Program.status == ProgramStatus.active).order_by(Program.level, Program.name).all()
        )
        courses = self.db.query(Course).order_by(Course.name).limit(MAX_COURSES).all()
        campuses = self.db.query(Campus).filter(Campus.is_active.is_(True)).order_by(Campus.name).all()
        calls = [call for call in PublicAdmissionsService(self.db).catalog() if call.is_accepting]
        return InstitutionPageOut(
            institution=InstitutionSummary.model_validate(institution),
            profile=PublicProfile.model_validate(institution.public_profile or {}),
            programs=[
                PublicProgram(id=p.id, code=p.code, name=p.name, level=p.level, degree=p.degree,
                              duration_terms=p.duration_terms, total_hours=p.total_hours)
                for p in programs
            ],
            courses=[PublicCourse(id=c.id, name=c.name, description=c.description, modality=c.modality) for c in courses],
            campuses=[PublicCampus(name=c.name, address=c.address) for c in campuses],
            open_calls=calls,
        )
