from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_academic_staff
from app.models.student import Student
from app.policies.user_scope import ensure_academic_user_scope, ensure_availability_scope
from app.schemas.student import (
    InstructorAvailabilityCreate,
    InstructorAvailabilityOut,
    InstructorAvailabilityUpdate,
    InstructorProfileOut,
    InstructorProfileUpdate,
    InstructorRatingCreate,
    InstructorRatingOut,
    StudentProfileOut,
    StudentProfileUpdate,
)
from app.services.student import StudentService

router = APIRouter()


@router.get("/students/{student_id}/student-profile", response_model=StudentProfileOut)
@router.get("/users/{student_id}/student-profile", response_model=StudentProfileOut)
def get_student_profile(
    student_id: int,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_academic_staff),
):
    target = StudentService(db).get_or_404(student_id)
    ensure_academic_user_scope(current, target)
    return StudentService(db).get_student_profile(student_id)


@router.patch("/students/{student_id}/student-profile", response_model=StudentProfileOut)
@router.patch("/users/{student_id}/student-profile", response_model=StudentProfileOut)
def update_student_profile(
    student_id: int,
    data: StudentProfileUpdate,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_academic_staff),
):
    target = StudentService(db).get_or_404(student_id)
    ensure_academic_user_scope(current, target)
    return StudentService(db).update_student_profile(student_id, data)


@router.get("/students/{student_id}/instructor-profile", response_model=InstructorProfileOut)
@router.get("/users/{student_id}/instructor-profile", response_model=InstructorProfileOut)
def get_instructor_profile(
    student_id: int,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_academic_staff),
):
    target = StudentService(db).get_or_404(student_id)
    ensure_academic_user_scope(current, target)
    return StudentService(db).get_instructor_profile(student_id)


@router.patch("/students/{student_id}/instructor-profile", response_model=InstructorProfileOut)
@router.patch("/users/{student_id}/instructor-profile", response_model=InstructorProfileOut)
def update_instructor_profile(
    student_id: int,
    data: InstructorProfileUpdate,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_academic_staff),
):
    target = StudentService(db).get_or_404(student_id)
    ensure_academic_user_scope(current, target)
    return StudentService(db).update_instructor_profile(student_id, data)


@router.get("/students/{student_id}/availability", response_model=list[InstructorAvailabilityOut])
@router.get("/users/{student_id}/availability", response_model=list[InstructorAvailabilityOut])
def list_instructor_availability(
    student_id: int,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_academic_staff),
):
    target = StudentService(db).get_or_404(student_id)
    ensure_academic_user_scope(current, target)
    return StudentService(db).list_instructor_availability(student_id)


@router.post("/students/{student_id}/availability", response_model=InstructorAvailabilityOut, status_code=201)
@router.post("/users/{student_id}/availability", response_model=InstructorAvailabilityOut, status_code=201)
def add_instructor_availability(
    student_id: int,
    data: InstructorAvailabilityCreate,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_academic_staff),
):
    target = StudentService(db).get_or_404(student_id)
    ensure_academic_user_scope(current, target)
    return StudentService(db).add_instructor_availability(student_id, data)


@router.patch("/students/availability/{availability_id}", response_model=InstructorAvailabilityOut)
@router.patch("/users/availability/{availability_id}", response_model=InstructorAvailabilityOut)
def update_instructor_availability(
    availability_id: int,
    data: InstructorAvailabilityUpdate,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_academic_staff),
):
    service = StudentService(db)
    ensure_availability_scope(current, service, availability_id)
    return service.update_instructor_availability(availability_id, data)


@router.delete("/students/availability/{availability_id}", status_code=204)
@router.delete("/users/availability/{availability_id}", status_code=204)
def delete_instructor_availability(
    availability_id: int,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_academic_staff),
):
    service = StudentService(db)
    ensure_availability_scope(current, service, availability_id)
    service.delete_instructor_availability(availability_id)


@router.get("/students/{student_id}/ratings", response_model=list[InstructorRatingOut])
@router.get("/users/{student_id}/ratings", response_model=list[InstructorRatingOut])
def list_instructor_ratings(
    student_id: int,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_academic_staff),
):
    target = StudentService(db).get_or_404(student_id)
    ensure_academic_user_scope(current, target)
    return StudentService(db).list_instructor_ratings(student_id)


@router.post("/students/{student_id}/ratings", response_model=InstructorRatingOut, status_code=201)
@router.post("/users/{student_id}/ratings", response_model=InstructorRatingOut, status_code=201)
def add_instructor_rating(
    student_id: int,
    data: InstructorRatingCreate,
    db: Session = Depends(get_db),
    current: Student = Depends(get_current_academic_staff),
):
    target = StudentService(db).get_or_404(student_id)
    ensure_academic_user_scope(current, target)
    return StudentService(db).add_instructor_rating(current.id, student_id, data)
