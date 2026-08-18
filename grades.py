from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import Page
from app.schemas.grade import GradeCreate, GradeResponse, GradeUpdate
from app.services.grade_service import (
    create_grade,
    delete_grade,
    get_grade_or_404,
    list_grades,
    update_grade,
)

router = APIRouter(prefix="/grades", tags=["Grades"])


@router.post("/", response_model=GradeResponse, status_code=status.HTTP_201_CREATED)
def create(payload: GradeCreate, db: Session = Depends(get_db)) -> GradeResponse:
    return create_grade(db, payload)


@router.get("/", response_model=Page[GradeResponse])
def list_all(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    student_id: int | None = Query(default=None, gt=0),
    course_id: int | None = Query(default=None, gt=0),
    db: Session = Depends(get_db),
) -> Page[GradeResponse]:
    grades, total = list_grades(
        db, limit=limit, offset=offset, student_id=student_id, course_id=course_id
    )
    return Page(items=grades, total=total, limit=limit, offset=offset)


@router.get("/{grade_id}", response_model=GradeResponse)
def get_one(grade_id: int, db: Session = Depends(get_db)) -> GradeResponse:
    return get_grade_or_404(db, grade_id)


@router.put("/{grade_id}", response_model=GradeResponse)
def update(grade_id: int, payload: GradeUpdate, db: Session = Depends(get_db)) -> GradeResponse:
    return update_grade(db, grade_id, payload)


@router.delete("/{grade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(grade_id: int, db: Session = Depends(get_db)) -> None:
    delete_grade(db, grade_id)
