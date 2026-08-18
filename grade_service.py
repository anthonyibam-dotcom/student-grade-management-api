from sqlalchemy import case, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.models import Course, Grade, Student
from app.schemas.grade import GradeCreate, GradeUpdate


def get_grade_or_404(db: Session, grade_id: int) -> Grade:
    grade = db.get(Grade, grade_id)
    if grade is None:
        raise NotFoundError("GRADE_NOT_FOUND", f"Grade {grade_id} was not found")
    return grade


def create_grade(db: Session, payload: GradeCreate) -> Grade:
    if db.get(Student, payload.student_id) is None:
        raise NotFoundError("STUDENT_NOT_FOUND", f"Student {payload.student_id} was not found")
    if db.get(Course, payload.course_id) is None:
        raise NotFoundError("COURSE_NOT_FOUND", f"Course {payload.course_id} was not found")
    grade = Grade(**payload.model_dump(), letter_grade=Grade.letter_from_score(payload.score))
    db.add(grade)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(
            "GRADE_EXISTS", "A grade for this student, course, and semester already exists"
        ) from exc
    db.refresh(grade)
    return grade


def list_grades(
    db: Session, *, limit: int, offset: int, student_id: int | None, course_id: int | None
) -> tuple[list[Grade], int]:
    query = select(Grade).order_by(Grade.id).offset(offset).limit(limit)
    count_query = select(func.count()).select_from(Grade)
    if student_id is not None:
        query = query.where(Grade.student_id == student_id)
        count_query = count_query.where(Grade.student_id == student_id)
    if course_id is not None:
        query = query.where(Grade.course_id == course_id)
        count_query = count_query.where(Grade.course_id == course_id)
    return list(db.scalars(query).all()), db.scalar(count_query) or 0


def update_grade(db: Session, grade_id: int, payload: GradeUpdate) -> Grade:
    grade = get_grade_or_404(db, grade_id)
    grade.score = payload.score
    grade.letter_grade = Grade.letter_from_score(payload.score)
    db.commit()
    db.refresh(grade)
    return grade


def delete_grade(db: Session, grade_id: int) -> None:
    grade = get_grade_or_404(db, grade_id)
    db.delete(grade)
    db.commit()


def course_stats(db: Session, course_id: int) -> dict[str, float | int | None]:
    if db.get(Course, course_id) is None:
        raise NotFoundError("COURSE_NOT_FOUND", f"Course {course_id} was not found")
    stats = db.execute(
        select(
            func.count(Grade.id),
            func.avg(Grade.score),
            func.max(Grade.score),
            func.min(Grade.score),
            func.sum(case((Grade.score >= 60, 1), else_=0)),
        ).where(Grade.course_id == course_id)
    ).one()
    grade_count, mean_score, max_score, min_score, passing_count = stats
    return {
        "course_id": course_id,
        "grade_count": grade_count,
        "mean_score": round(mean_score, 2) if mean_score is not None else None,
        "max_score": max_score,
        "min_score": min_score,
        "passing_rate": round((passing_count / grade_count) * 100, 2) if grade_count else None,
    }
