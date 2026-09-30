from sqlalchemy.orm import Session

from app.core.tenancy import UNSCOPED
from app.models.institution import Campus, Institution, InstitutionMembership


class InstitutionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, institution_id: int) -> Institution | None:
        return self.db.get(Institution, institution_id)

    def get_by_slug(self, slug: str) -> Institution | None:
        return self.db.query(Institution).filter(Institution.slug == slug).first()

    def get_by_ref(self, ref: str | int) -> Institution | None:
        if isinstance(ref, int) or ref.isdigit():
            return self.get_by_id(int(ref))
        return self.get_by_slug(ref)

    def list_all(self) -> list[Institution]:
        return self.db.query(Institution).order_by(Institution.name).all()

    def first(self) -> Institution | None:
        return self.db.query(Institution).order_by(Institution.id).first()

    def create(self, institution: Institution) -> Institution:
        self.db.add(institution)
        self.db.commit()
        self.db.refresh(institution)
        return institution

    def update(self, institution: Institution) -> Institution:
        self.db.commit()
        self.db.refresh(institution)
        return institution


class MembershipRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, institution_id: int, user_id: int) -> InstitutionMembership | None:
        return (
            self.db.query(InstitutionMembership)
            .filter(InstitutionMembership.institution_id == institution_id, InstitutionMembership.user_id == user_id)
            .first()
        )

    def list_active_for_user(self, user_id: int) -> list[InstitutionMembership]:
        return (
            self.db.query(InstitutionMembership)
            .filter(InstitutionMembership.user_id == user_id, InstitutionMembership.is_active.is_(True))
            .order_by(InstitutionMembership.id)
            .all()
        )

    def list_all_for_user(self, user_id: int) -> list[InstitutionMembership]:
        return self.db.query(InstitutionMembership).filter(InstitutionMembership.user_id == user_id).all()

    def add(self, membership: InstitutionMembership) -> InstitutionMembership:
        self.db.add(membership)
        return membership


class CampusRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, campus_id: int) -> Campus | None:
        return self.db.get(Campus, campus_id)

    def list_all(self) -> list[Campus]:
        return self.db.query(Campus).order_by(Campus.name).all()

    def list_by_institution(self, institution_id: int) -> list[Campus]:
        return (
            self.db.query(Campus)
            .execution_options(**UNSCOPED)
            .filter(Campus.institution_id == institution_id)
            .order_by(Campus.name)
            .all()
        )

    def create(self, campus: Campus) -> Campus:
        self.db.add(campus)
        self.db.commit()
        self.db.refresh(campus)
        return campus

    def update(self, campus: Campus) -> Campus:
        self.db.commit()
        self.db.refresh(campus)
        return campus

    def delete(self, campus: Campus) -> None:
        self.db.delete(campus)
        self.db.commit()
