from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

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


class User(BaseModel):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE")
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
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

    workout: Mapped["Workout"] = relationship(back_populates="exercises")
    exercise: Mapped["Exercise"] = relationship(back_populates="workout_exercises")
    sets: Mapped[list["Set"]] = relationship(
        back_populates="workout_exercise",
        cascade="all, delete-orphan",
        order_by="Set.set_number",
    )


class Exercise(BaseModel):
    __tablename__ = "exercises"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "name",
        ),
    )
    name: Mapped[str] = mapped_column(String(255), index=True)
    workout_exercises: Mapped[list["WorkoutExercise"]] = relationship(
        back_populates="exercise"
    )
    muscle_groups: Mapped[list["MuscleGroup"]] = relationship(
        secondary=exercise_muscle_group, back_populates="exercises"
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE")
    )


class MuscleGroup(BaseModel):
    __tablename__ = "muscle_groups"
    name: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    exercises: Mapped[list["Exercise"]] = relationship(
        secondary=exercise_muscle_group, back_populates="muscle_groups"
    )


class Workout(BaseModel):
    __tablename__ = "workouts"
    exercises: Mapped[list["WorkoutExercise"]] = relationship(
        back_populates="workout",
        cascade="all, delete-orphan",
        order_by="WorkoutExercise.order",
    )
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    notes: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE")
    )


class Set(BaseModel):
    __tablename__ = "sets"
    workout_exercise_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("workout_exercises.id", ondelete="CASCADE")
    )
    set_number: Mapped[int] = mapped_column(Integer)
    reps: Mapped[int] = mapped_column(Integer)
    weight: Mapped[float] = mapped_column(Float)
    workout_exercise: Mapped["WorkoutExercise"] = relationship(back_populates="sets")
