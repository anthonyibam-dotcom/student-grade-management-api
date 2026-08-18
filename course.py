from pydantic import BaseModel, ConfigDict, Field, field_validator


class CourseBase(BaseModel):
    code: str = Field(min_length=2, max_length=20)
    title: str = Field(min_length=1, max_length=200)
    credits: int = Field(ge=1, le=5)
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        value = value.strip().upper()
        if not value:
            raise ValueError("course code must not be blank")
        return value

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        value = " ".join(value.strip().split())
        if not value:
            raise ValueError("course title must not be blank")
        return value


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=2, max_length=20)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    credits: int | None = Field(default=None, ge=1, le=5)
    description: str | None = Field(default=None, max_length=2000)

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str | None) -> str | None:
        return value.strip().upper() if value is not None else None

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = " ".join(value.strip().split())
        if not value:
            raise ValueError("course title must not be blank")
        return value


class CourseSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    title: str
    credits: int


class CourseResponse(CourseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
