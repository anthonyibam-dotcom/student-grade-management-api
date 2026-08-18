from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.student import Student


class Grade(Base):
    __tablename__ = "grades"
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 100", name="ck_grades_score_range"),
        UniqueConstraint("student_id", "course_id", "semester", name="uq_grade_student_course_semester"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    letter_grade: Mapped[str] = mapped_column(String(2), nullable=False)
    semester: Mapped[str] = mapped_column(String(30), nullable=False, index=True)

    student: Mapped["Student"] = relationship("Student", back_populates="grades")
    course: Mapped["Course"] = relationship("Course", back_populates="grades")

    @staticmethod
    def letter_from_score(score: float) -> str:
        if score >= 90:
            return "A"
        if score >= 80:
            return "B"
        if score >= 70:
            return "C"
        if score >= 60:
            return "D"
        return "F"
