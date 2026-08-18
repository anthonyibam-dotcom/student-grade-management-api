from fastapi import APIRouter

from app.api.v1.endpoints import analytics, courses, grades, students

api_router = APIRouter()
api_router.include_router(students.router)
api_router.include_router(courses.router)
api_router.include_router(grades.router)
api_router.include_router(analytics.router)
