from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.grade import CourseStatsResponse, GPAResponse
from app.services.grade_service import course_stats
from app.services.student_service import calculate_gpa, get_student_or_404

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/students/{student_id}/gpa", response_model=GPAResponse)
def student_gpa(student_id: int, db: Session = Depends(get_db)) -> GPAResponse:
    student = get_student_or_404(db, student_id)
    gpa, weighted_average = calculate_gpa(student.grades)
    return GPAResponse(
        student_id=student_id,
        gpa=gpa,
        weighted_average=weighted_average,
        grade_count=len(student.grades),
    )


@router.get("/courses/{course_id}/stats", response_model=CourseStatsResponse)
def course_statistics(course_id: int, db: Session = Depends(get_db)) -> CourseStatsResponse:
    return CourseStatsResponse(**course_stats(db, course_id))
