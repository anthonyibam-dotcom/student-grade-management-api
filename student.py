from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.course import CourseSummary


class StudentBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    enrollment_date: date

    @field_validator("first_name", "last_name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = " ".join(value.strip().split())
        if not value:
            raise ValueError("name must not be blank")
        return value


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    enrollment_date: date | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = " ".join(value.strip().split())
        if not value:
            raise ValueError("name must not be blank")
        return value


class StudentListItem(StudentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class StudentDetail(StudentListItem):
    courses: list[CourseSummary] = Field(default_factory=list)
    grade_count: int = 0
    gpa: float = 0.0
    weighted_average: float = 0.0
