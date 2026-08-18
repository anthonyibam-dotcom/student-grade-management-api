from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import Page
from app.schemas.student import StudentCreate, StudentDetail, StudentListItem, StudentUpdate
from app.services.student_service import (
    calculate_gpa,
    create_student,
    delete_student,
    get_student_or_404,
    list_students,
    update_student,
)

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/", response_model=StudentListItem, status_code=status.HTTP_201_CREATED)
def create(payload: StudentCreate, db: Session = Depends(get_db)) -> StudentListItem:
    return create_student(db, payload)


@router.get("/", response_model=Page[StudentListItem])
def list_all(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
) -> Page[StudentListItem]:
    students, total = list_students(db, limit=limit, offset=offset, search=search)
    return Page(items=students, total=total, limit=limit, offset=offset)


@router.get("/{student_id}", response_model=StudentDetail)
def get_one(student_id: int, db: Session = Depends(get_db)) -> StudentDetail:
    student = get_student_or_404(db, student_id)
    gpa, weighted_average = calculate_gpa(student.grades)
    courses_by_id = {grade.course.id: grade.course for grade in student.grades}
    return StudentDetail(
        id=student.id,
        first_name=student.first_name,
        last_name=student.last_name,
        email=student.email,
        enrollment_date=student.enrollment_date,
        created_at=student.created_at,
        courses=list(courses_by_id.values()),
        grade_count=len(student.grades),
        gpa=gpa,
        weighted_average=weighted_average,
    )


@router.put("/{student_id}", response_model=StudentListItem)
def update(student_id: int, payload: StudentUpdate, db: Session = Depends(get_db)) -> StudentListItem:
    return update_student(db, student_id, payload)


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(student_id: int, db: Session = Depends(get_db)) -> None:
    delete_student(db, student_id)
