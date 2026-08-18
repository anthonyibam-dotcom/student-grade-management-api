from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import Page
from app.schemas.course import CourseCreate, CourseResponse, CourseUpdate
from app.services.course_service import (
    create_course,
    delete_course,
    get_course_or_404,
    list_courses,
    update_course,
)

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create(payload: CourseCreate, db: Session = Depends(get_db)) -> CourseResponse:
    return create_course(db, payload)


@router.get("/", response_model=Page[CourseResponse])
def list_all(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> Page[CourseResponse]:
    courses, total = list_courses(db, limit=limit, offset=offset)
    return Page(items=courses, total=total, limit=limit, offset=offset)


@router.get("/{course_id}", response_model=CourseResponse)
def get_one(course_id: int, db: Session = Depends(get_db)) -> CourseResponse:
    return get_course_or_404(db, course_id)


@router.put("/{course_id}", response_model=CourseResponse)
def update(course_id: int, payload: CourseUpdate, db: Session = Depends(get_db)) -> CourseResponse:
    return update_course(db, course_id, payload)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(course_id: int, db: Session = Depends(get_db)) -> None:
    delete_course(db, course_id)
