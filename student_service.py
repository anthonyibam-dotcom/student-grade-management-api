from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.errors import ConflictError, NotFoundError
from app.models import Course, Grade, Student
from app.schemas.student import StudentCreate, StudentUpdate

_GPA_POINTS = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0}


def get_student_or_404(db: Session, student_id: int) -> Student:
    student = db.scalar(
        select(Student).options(selectinload(Student.grades).selectinload(Grade.course)).where(Student.id == student_id)
    )
    if student is None:
        raise NotFoundError("STUDENT_NOT_FOUND", f"Student {student_id} was not found")
    return student


def create_student(db: Session, payload: StudentCreate) -> Student:
    student = Student(**payload.model_dump())
    db.add(student)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("STUDENT_EMAIL_EXISTS", "A student with this email already exists") from exc
    db.refresh(student)
    return student


def list_students(db: Session, *, limit: int, offset: int, search: str | None) -> tuple[list[Student], int]:
    query = select(Student).order_by(Student.id).offset(offset).limit(limit)
    count_query = select(func.count()).select_from(Student)
    if search:
        pattern = f"%{search.strip()}%"
        predicate = or_(Student.first_name.ilike(pattern), Student.last_name.ilike(pattern))
        query = query.where(predicate)
        count_query = count_query.where(predicate)
    students = list(db.scalars(query).all())
    total = db.scalar(count_query) or 0
    return students, total


def update_student(db: Session, student_id: int, payload: StudentUpdate) -> Student:
    student = get_student_or_404(db, student_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(student, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("STUDENT_EMAIL_EXISTS", "A student with this email already exists") from exc
    db.refresh(student)
    return get_student_or_404(db, student_id)


def delete_student(db: Session, student_id: int) -> None:
    student = db.get(Student, student_id)
    if student is None:
        raise NotFoundError("STUDENT_NOT_FOUND", f"Student {student_id} was not found")
    db.delete(student)
    db.commit()


def calculate_gpa(grades: list[Grade]) -> tuple[float, float]:
    if not grades:
        return 0.0, 0.0
    total_credits = sum(grade.course.credits for grade in grades)
    weighted_points = sum(_GPA_POINTS[grade.letter_grade] * grade.course.credits for grade in grades)
    weighted_scores = sum(grade.score * grade.course.credits for grade in grades)
    if total_credits == 0:
        return 0.0, 0.0
    return round(weighted_points / total_credits, 2), round(weighted_scores / total_credits, 2)
