from datetime import date, datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    Column,
    Date,
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

from rep_log.database import Base, DBModel, TZDateTime

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


class User(DBModel):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true"
    )
    created_at: Mapped[datetime] = mapped_column(TZDateTime, server_default=func.now())


class RefreshToken(DBModel):
    __tablename__ = "refresh_tokens"
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE")
    )
    expires_at: Mapped[datetime] = mapped_column(TZDateTime)
    revoked: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false"
    )


class WorkoutExercise(DBModel):
    __tablename__ = "workout_exercises"
    __table_args__ = (
        UniqueConstraint(
            "workout_id",
            "order",
        ),
    )
    workout_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("workouts.id", ondelete="CASCADE")
    )
    exercise_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("exercises.id", ondelete="CASCADE")
    )
    order: Mapped[int] = mapped_column(Integer)

    workout: Mapped["Workout"] = relationship(back_populates="exercises")
    exercise: Mapped["Exercise"] = relationship(
        back_populates="workout_exercises", lazy="selectin"
    )
    sets: Mapped[list["Set"]] = relationship(
        back_populates="workout_exercise",
        cascade="all, delete-orphan",
        order_by="Set.set_number",
        lazy="selectin",
    )


class Exercise(DBModel):
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
        secondary=exercise_muscle_group, back_populates="exercises", lazy="selectin"
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE")
    )


class MuscleGroup(DBModel):
    __tablename__ = "muscle_groups"
    name: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    exercises: Mapped[list["Exercise"]] = relationship(
        secondary=exercise_muscle_group, back_populates="muscle_groups"
    )


class Workout(DBModel):
    __tablename__ = "workouts"
    name: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    exercises: Mapped[list["WorkoutExercise"]] = relationship(
        back_populates="workout",
        cascade="all, delete-orphan",
        order_by="WorkoutExercise.order",
        lazy="selectin",
    )
    workout_date: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    notes: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE")
    )


class Set(DBModel):
    __tablename__ = "sets"
    __table_args__ = (
        UniqueConstraint(
            "workout_exercise_id",
            "set_number",
        ),
    )
    workout_exercise_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("workout_exercises.id", ondelete="CASCADE")
    )
    set_number: Mapped[int] = mapped_column(Integer)
    reps: Mapped[int] = mapped_column(Integer)
    weight: Mapped[float] = mapped_column(Float)
    workout_exercise: Mapped["WorkoutExercise"] = relationship(back_populates="sets")
