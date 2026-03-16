from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrmBase:
    model_config = ConfigDict(from_attributes=True)


class ExerciseBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)


class ExerciseRead(OrmBase, ExerciseBase):
    id: UUID
    muscle_groups: list["MuscleGroupRead"] = Field(default_factory=list)


class MuscleGroupBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class MuscleGroupCreate(MuscleGroupBase):
    pass


class MuscleGroupUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)


class MuscleGroupRead(OrmBase, MuscleGroupBase):
    id: UUID


class WorkoutBase(BaseModel):
    notes: str | None = Field(default=None, min_length=1, max_length=2048)


class WorkoutCreate(WorkoutBase):
    pass


class WorkoutUpdate(BaseModel):
    notes: str | None = Field(default=None, min_length=1, max_length=2048)


class WorkoutRead(OrmBase, WorkoutBase):
    id: UUID
    date: datetime
    exercises: list["WorkoutExerciseRead"] = Field(default_factory=list)


class WorkoutExerciseBase(BaseModel):
    order: int = Field(gt=0)


class WorkoutExerciseCreate(WorkoutExerciseBase):
    workout_id: UUID
    exercise_id: UUID


class WorkoutExerciseUpdate(BaseModel):
    order: int | None = Field(default=None, gt=0)
    workout_id: UUID | None = None
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
