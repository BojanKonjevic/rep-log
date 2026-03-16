from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from rep_log.database import Base, BaseModel

exercise_muscle_group = Table(
    "exercise_muscle_group",
    Base.metadata,
    Column(
        "exercise_id", ForeignKey("exercises.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "muscle_group_id",
        ForeignKey("muscle_groups.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class WorkoutExercise(BaseModel):
    __tablename__ = "workout_exercises"
    workout_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("workouts.id", ondelete="CASCADE")
    )
    exercise_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("exercises.id", ondelete="CASCADE")
    )
    order: Mapped[int] = mapped_column(Integer)


class Exercise(BaseModel):
    __tablename__ = "exercises"
    name: Mapped[str] = mapped_column(String(255), index=True, unique=True)


class MuscleGroup(BaseModel):
    __tablename__ = "muscle_groups"
    name: Mapped[str] = mapped_column(String(255), index=True, unique=True)


class Workout(BaseModel):
    __tablename__ = "workouts"
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    notes: Mapped[str | None] = mapped_column(String(2048), nullable=True)


class Set(BaseModel):
    __tablename__ = "sets"
    workout_exercise_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("workout_exercises.id", ondelete="CASCADE")
    )
    set_number: Mapped[int] = mapped_column(Integer)
    reps: Mapped[int] = mapped_column(Integer)
    weight: Mapped[float] = mapped_column(Float)
