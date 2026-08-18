from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models import Course
from app.schemas.course import CourseCreate, CourseUpdate


def get_course_or_404(db: Session, course_id: int) -> Course:
    course = db.get(Course, course_id)
    if course is None:
        raise NotFoundError("COURSE_NOT_FOUND", f"Course {course_id} was not found")
    return course


def create_course(db: Session, payload: CourseCreate) -> Course:
    course = Course(**payload.model_dump())
    db.add(course)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("COURSE_CODE_EXISTS", "A course with this code already exists") from exc
    db.refresh(course)
    return course


def list_courses(db: Session, *, limit: int, offset: int) -> tuple[list[Course], int]:
    courses = list(db.scalars(select(Course).order_by(Course.id).offset(offset).limit(limit)).all())
    total = db.scalar(select(func.count()).select_from(Course)) or 0
    return courses, total


def update_course(db: Session, course_id: int, payload: CourseUpdate) -> Course:
    course = get_course_or_404(db, course_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(course, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("COURSE_CODE_EXISTS", "A course with this code already exists") from exc
    db.refresh(course)
    return course


def delete_course(db: Session, course_id: int) -> None:
    course = get_course_or_404(db, course_id)
    db.delete(course)
    db.commit()
