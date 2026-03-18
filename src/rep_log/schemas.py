from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OrmBase:
    model_config = ConfigDict(from_attributes=True)


class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserRead(OrmBase, BaseModel):
    id: UUID
    email: str
    is_active: bool


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class ExerciseBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class ExerciseCreate(ExerciseBase):
    muscle_group_names: list[str] = Field(default_factory=list)
    pass


class ExerciseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    muscle_group_ids: list[UUID] | None = None


class ExerciseRead(OrmBase, ExerciseBase):
    id: UUID
    muscle_groups: list["MuscleGroupRead"] = Field(default_factory=list)


class MuscleGroupBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class MuscleGroupRead(OrmBase, MuscleGroupBase):
    id: UUID


class WorkoutBase(BaseModel):
    notes: str | None = Field(default=None, min_length=1, max_length=2048)


class WorkoutCreate(WorkoutBase):
    workout_date: date = Field(default_factory=date.today)


class WorkoutUpdate(BaseModel):
    notes: str | None = Field(default=None, min_length=1, max_length=2048)
    workout_date: date | None = None


class WorkoutRead(OrmBase, WorkoutBase):
    id: UUID
    workout_date: date
    exercises: list["WorkoutExerciseRead"] = Field(default_factory=list)


class WorkoutExerciseBase(BaseModel):
    order: int = Field(gt=0)


class WorkoutExerciseCreate(WorkoutExerciseBase):
    exercise_id: UUID


class WorkoutExerciseUpdate(BaseModel):
    order: int | None = Field(default=None, gt=0)
    exercise_id: UUID | None = None


class WorkoutExerciseRead(OrmBase, WorkoutExerciseBase):
    id: UUID
    workout_id: UUID
    exercise: ExerciseRead
    sets: list["SetRead"] = Field(default_factory=list)


class SetBase(BaseModel):
    set_number: int = Field(gt=0)
    reps: int = Field(gt=0)
    weight: float = Field(ge=0)


class SetCreate(SetBase):
    workout_exercise_id: UUID


class SetUpdate(BaseModel):
    set_number: int | None = Field(default=None, gt=0)
    reps: int | None = Field(default=None, gt=0)
    weight: float | None = Field(default=None, ge=0)
    workout_exercise_id: UUID | None = None


class SetRead(OrmBase, SetBase):
    id: UUID
    workout_exercise_id: UUID


WorkoutRead.model_rebuild()
WorkoutExerciseRead.model_rebuild()
ExerciseRead.model_rebuild()
